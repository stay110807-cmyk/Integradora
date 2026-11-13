# Ventur (Flet + MVC)

Control de inventario y ventas para tableta Android. Funciona sin internet.

## Acceso de prueba

| Usuario | Contraseña | Rol   |
|---------|------------|-------|
| admin   | admin123   | Dueña |

Cambia la contraseña en `src/models/autenticacion.py`. Para agregar un empleado hay un
ejemplo comentado en `RepositorioUsuarios.__init__`.

## Correr en la computadora

    pip install "flet[all]==1.1.0"
    cd ventur
    flet run

## Verla en la tableta mientras programas

Instala la app **Flet** en la tableta (misma red Wi-Fi que la computadora) y corre:

    flet run --android

## Generar el APK

    flet build apk

La primera vez descarga Flutter y el SDK de Android (tarda y pesa varios GB).
El APK queda en `build/apk/`.

## Estructura

    pyproject.toml                  nombre, versión y configuración del APK
    src/
      main.py                       punto de entrada
      models/                       datos y reglas (igual que en la versión tkinter)
      controllers/app_controller.py sesión, navegación, Productos y Caja
      views/
        tema.py                     paleta de los mockups
        componentes.py              texto, botón, píldora, aviso, campo, selector
        tabla.py                    encabezado y filas de las tablas
        ventana.py                  muestra una vista a la vez; diálogos
        vista_login.py  vista_dashboard.py  vista_base.py
        vista_productos.py  vista_caja.py  formulario_producto.py  vista_modulo.py
      assets/                       logos, iconos e icon.png (icono de la app)
    tools/generar_iconos.py         regenera los iconos (necesita Pillow)

## Cómo se conectan las piezas

Cada vista es una clase con un atributo `.control` (lo que se dibuja). El controlador crea
la vista, se la da a `Ventana.mostrar()` y la actualiza cuando cambian los datos.
Las vistas nunca importan al controlador: reciben funciones (`al_agregar`, `al_cobrar`...).

## Importante para SQLite

En el APK, los archivos de la app son de solo lectura. La base de datos tiene que guardarse
en la carpeta que indica la variable de entorno `FLET_APP_STORAGE_DATA`, no junto al código.
