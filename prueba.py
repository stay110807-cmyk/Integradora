import argparse
import csv
import json
import statistics
import sys
from collections import defaultdict
from datetime import date, datetime, timedelta
 
 

def parse_fecha(texto):

    texto = texto.strip().replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(texto)
    except ValueError:
        dt = datetime.strptime(texto[:10], "%Y-%m-%d")
    return dt.replace(tzinfo=None)
 
 
def cargar_trello(ruta):
    
    with open(ruta, encoding="utf-8") as f:
        datos = json.load(f)
 
    tarjetas = {}
    acciones = sorted(datos.get("actions", []), key=lambda a: a["date"])
    for a in acciones:
        d = a.get("data", {})
        tarjeta = d.get("card")
        if not tarjeta:
            continue
        tipo = a["type"]
        lista = None
        if tipo in ("createCard", "copyCard", "convertToCardFromCheckItem"):
            lista = d.get("list", {}).get("name")
        elif tipo == "updateCard" and "listAfter" in d:
            lista = d["listAfter"]["name"]
        elif tipo == "moveCardToBoard":
            lista = d.get("list", {}).get("name")
        if lista is None:
            continue
        t = tarjetas.setdefault(
            tarjeta["id"], {"nombre": tarjeta.get("name", tarjeta["id"]), "movs": []}
        )
        t["nombre"] = tarjeta.get("name", t["nombre"])
        t["movs"].append((parse_fecha(a["date"]), lista))
    return tarjetas
 
 
def cargar_csv(ruta):

    tarjetas = {}
    with open(ruta, encoding="utf-8-sig", newline="") as f:
        for fila in csv.DictReader(f):
            nombre = fila["tarjeta"].strip()
            t = tarjetas.setdefault(nombre, {"nombre": nombre, "movs": []})
            t["movs"].append((parse_fecha(fila["fecha"]), fila["lista"].strip()))
    for t in tarjetas.values():
        t["movs"].sort()
    return tarjetas
 
 

def percentil(valores, p):

    v = sorted(valores)
    if not v:
        return float("nan")
    k = (len(v) - 1) * p / 100
    i = int(k)
    if i + 1 >= len(v):
        return float(v[-1])
    return v[i] + (v[i + 1] - v[i]) * (k - i)
 
 
def primera_entrada(movs, listas, despues_de=None):
    for dt, lista in movs:
        if lista in listas and (despues_de is None or dt >= despues_de):
            return dt
    return None
 
 
def lista_en(movs, momento):
    """Lista en la que estaba la tarjeta en un instante (None si no existia)."""
    actual = None
    for dt, lista in movs:
        if dt <= momento:
            actual = lista
        else:
            break
    return actual
 
 
def calcular_ciclos(tarjetas, inicio, fin, desde, hasta):
    """Una fila por tarjeta terminada dentro del periodo."""
    filas, sin_inicio = [], 0
    for t in tarjetas.values():
        ini = primera_entrada(t["movs"], inicio)
        if ini is None:
            # Se fue directo a Terminado: no hay tiempo de ciclo medible.
            if primera_entrada(t["movs"], fin) is not None:
                sin_inicio += 1
            continue
        fn = primera_entrada(t["movs"], fin, despues_de=ini)
        if fn is None or not (desde <= fn.date() <= hasta):
            continue
        dias = max((fn - ini).total_seconds() / 86400, 0.0)
        filas.append(
            {"tarjeta": t["nombre"], "inicio": ini, "fin": fn, "ciclo_dias": round(dias, 2)}
        )
    return filas, sin_inicio
 
 
def throughput_semanal(filas, desde, hasta):
    """{(anio, semana): terminadas}, incluyendo semanas con cero."""
    conteo = defaultdict(int)
    for f in filas:
        iso = f["fin"].isocalendar()
        conteo[(iso[0], iso[1])] += 1
    semanas, d = [], desde
    while d <= hasta:
        iso = d.isocalendar()
        clave = (iso[0], iso[1])
        if clave not in semanas:
            semanas.append(clave)
        d += timedelta(days=1)
    return {s: conteo.get(s, 0) for s in semanas}
 
 
def calcular_cfd(tarjetas, columnas, desde, hasta):
    """{fecha: {lista: n}} con el estado al final de cada dia."""
    cfd, d = {}, desde
    while d <= hasta:
        fin_dia = datetime.combine(d, datetime.max.time())
        fila = {c: 0 for c in columnas}
        for t in tarjetas.values():
            lista = lista_en(t["movs"], fin_dia)
            if lista in fila:
                fila[lista] += 1
        cfd[d] = fila
        d += timedelta(days=1)
    return cfd
 
 
# ---------------------------------------------------------------- salida
def guardar_csv_ciclos(filas, ruta):
    with open(ruta, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["tarjeta", "inicio", "fin", "ciclo_dias"])
        for r in sorted(filas, key=lambda r: r["fin"]):
            w.writerow([r["tarjeta"], r["inicio"].date(), r["fin"].date(), r["ciclo_dias"]])
 
 
def guardar_csv_cfd(cfd, columnas, ruta):
    with open(ruta, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["fecha"] + columnas)
        for dia, fila in cfd.items():
            w.writerow([dia] + [fila[c] for c in columnas])
 
 
def graficar_cfd(cfd, columnas, ruta):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("  (matplotlib no esta instalado: pip install matplotlib. Se omite el PNG)")
        return False
    dias = list(cfd.keys())
    # CFD: la columna final abajo y el trabajo pendiente arriba.
    orden = list(reversed(columnas))
    series = [[cfd[d][c] for d in dias] for c in orden]
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.stackplot(dias, series, labels=orden, alpha=0.85)
    ax.set_title("Diagrama de flujo acumulado (CFD)")
    ax.set_xlabel("Fecha")
    ax.set_ylabel("Tarjetas acumuladas")
    ax.legend(loc="upper left")
    ax.grid(alpha=0.3)
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(ruta, dpi=150)
    plt.close(fig)
    return True
 
 
# ---------------------------------------------------------------- main
def main():
    p = argparse.ArgumentParser(description="Metricas Kanban desde la exportacion del tablero")
    p.add_argument("archivo", help="Exportacion .json de Trello o .csv (tarjeta,lista,fecha)")
    p.add_argument("--inicio", default="En proceso",
                   help="Columnas donde empieza el trabajo, separadas por coma")
    p.add_argument("--fin", default="Terminado",
                   help="Columnas de terminado, separadas por coma")
    p.add_argument("--columnas", default=None,
                   help="Orden de columnas del tablero para el CFD, separadas por coma")
    p.add_argument("--desde", default=None, help="Fecha inicial AAAA-MM-DD")
    p.add_argument("--hasta", default=None, help="Fecha final AAAA-MM-DD (por defecto hoy)")
    p.add_argument("--salida", default="resultados", help="Prefijo de los archivos de salida")
    a = p.parse_args()
 
    tarjetas = cargar_csv(a.archivo) if a.archivo.lower().endswith(".csv") else cargar_trello(a.archivo)
    if not tarjetas:
        sys.exit("No se encontraron tarjetas ni movimientos en el archivo.")
 
    todas = [dt for t in tarjetas.values() for dt, _ in t["movs"]]
    desde = date.fromisoformat(a.desde) if a.desde else min(todas).date()
    hasta = date.fromisoformat(a.hasta) if a.hasta else max(max(todas).date(), date.today())
    if hasta < desde:
        sys.exit("--hasta no puede ser anterior a --desde.")
 
    inicio = {x.strip() for x in a.inicio.split(",")}
    fin = {x.strip() for x in a.fin.split(",")}
    if a.columnas:
        columnas = [x.strip() for x in a.columnas.split(",")]
    else:
        columnas = []
        for t in tarjetas.values():
            for _, lista in t["movs"]:
                if lista not in columnas:
                    columnas.append(lista)
 
    filas, sin_inicio = calcular_ciclos(tarjetas, inicio, fin, desde, hasta)
    dias_periodo = (hasta - desde).days + 1
    print(f"Periodo: {desde} a {hasta} ({dias_periodo} dias, {dias_periodo / 7:.1f} semanas)")
    if dias_periodo < 14:
        print("AVISO: la actividad pide al menos 2 semanas reales de trabajo.")
    print(f"Tarjetas en el tablero: {len(tarjetas)} | terminadas en el periodo: {len(filas)}")
    if sin_inicio:
        print(f"AVISO: {sin_inicio} tarjeta(s) pasaron a Terminado sin pasar por {sorted(inicio)}; "
              "no se les puede medir el tiempo de ciclo.")
 
    ciclos = [f["ciclo_dias"] for f in filas]
    prom = statistics.mean(ciclos) if ciclos else float("nan")
    p85 = percentil(ciclos, 85)
    print("\n== Tiempo de ciclo (dias) ==")
    print(f"  Promedio: {prom:.2f}")
    print(f"  Mediana : {statistics.median(ciclos) if ciclos else float('nan'):.2f}")
    print(f"  Percentil 85: {p85:.2f}  (85 % de las tarjetas se termina en este tiempo o menos)")
 
    tp = throughput_semanal(filas, desde, hasta)
    print("\n== Throughput semanal (tarjetas terminadas) ==")
    for (anio, semana), n in tp.items():
        print(f"  {anio}-S{semana:02d}: {n:3d} {'#' * n}")
    tp_prom = statistics.mean(tp.values()) if tp else float("nan")
    print(f"  Promedio: {tp_prom:.2f} por semana")
 
    # WIP y antiguedad de lo que sigue en curso
    ahora = datetime.combine(hasta, datetime.max.time())
    en_curso = []
    for t in tarjetas.values():
        lista = lista_en(t["movs"], ahora)
        if lista in inicio:
            ini = primera_entrada(t["movs"], inicio)
            en_curso.append((t["nombre"], lista, (ahora - ini).total_seconds() / 86400))
    print(f"\n== WIP actual: {len(en_curso)} tarjeta(s) en curso ==")
    for nombre, lista, edad in sorted(en_curso, key=lambda x: -x[2]):
        print(f"  {edad:5.1f} dias | {lista} | {nombre}")
 
    cfd = calcular_cfd(tarjetas, columnas, desde, hasta)
    cols_wip = [c for c in columnas if c in inicio]
    wip_prom = (
        statistics.mean(sum(fila[c] for c in cols_wip) for fila in cfd.values())
        if cols_wip else float("nan")
    )
    tp_dia = len(filas) / dias_periodo
    print("\n== Ley de Little: WIP = throughput x tiempo de ciclo ==")
    print(f"  WIP promedio (del CFD)         : {wip_prom:.2f}")
    print(f"  Throughput diario x ciclo prom.: {tp_dia * prom:.2f}")
    print("  (Si difieren mucho, el flujo no es estable o el periodo es corto.)")
 
    guardar_csv_ciclos(filas, f"{a.salida}_ciclos.csv")
    guardar_csv_cfd(cfd, columnas, f"{a.salida}_cfd.csv")
    print(f"\nArchivos: {a.salida}_ciclos.csv, {a.salida}_cfd.csv", end="")
    if graficar_cfd(cfd, columnas, f"{a.salida}_cfd.png"):
        print(f", {a.salida}_cfd.png", end="")
    print()
 
 
if __name__ == "__main__":
    main()