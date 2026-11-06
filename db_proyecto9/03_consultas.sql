-- =====================================================================
-- Ventur · A09 · 03_consultas.sql
-- Consultas de negocio. Ejecutar después de 01_ddl.sql y 02_dml.sql.
-- Para las capturas se usa la fecha de referencia 2026-11-01 (en producción: date('now')).
-- =====================================================================

-- ---------------------------------------------------------------------
-- Q1 · ¿Qué movimientos tuvo un producto y quién los hizo?
-- Caso de uso: CU-09 Consultar historial (y CU-05).  Tipo: JOIN de 3 tablas
-- ---------------------------------------------------------------------
SELECT p.codigo, p.nombre AS producto, m.fecha_hora, m.tipo, m.cantidad,
       e.nombre || ' ' || e.apellidos AS responsable, m.origen
  FROM movimiento m
  JOIN producto p ON p.id_producto = m.id_producto
  JOIN empleado e ON e.id_empleado = m.id_empleado
 WHERE p.codigo = 'P-001'
 ORDER BY m.fecha_hora;

-- ---------------------------------------------------------------------
-- Q2 · ¿Qué productos están agotados o con stock bajo?
-- Caso de uso: CU-06 Generar alerta de stock (RN-11).  Tipo: VISTA
-- ---------------------------------------------------------------------
DROP VIEW IF EXISTS v_alertas_stock;
CREATE VIEW v_alertas_stock AS
SELECT p.codigo, p.nombre, p.existencias, p.stock_minimo,
       CASE WHEN p.existencias = 0 THEN 'Agotado' ELSE 'Stock bajo' END AS alerta
  FROM producto p
 WHERE p.estado = 'Activo'
   AND p.existencias <= p.stock_minimo;

SELECT * FROM v_alertas_stock ORDER BY existencias, codigo;

-- ---------------------------------------------------------------------
-- Q3 · ¿Cuánto se vendió por proveedor y cuánto se le debe después de la
--      comisión bancaria del 4 % en pagos con tarjeta?
-- Caso de uso: CU-11 Reporte (extensión de ventas).  Tipo: JOIN + GROUP BY + HAVING
-- ---------------------------------------------------------------------
SELECT pr.nombre_comercial AS proveedor,
       SUM(d.cantidad)                                          AS piezas,
       ROUND(SUM(d.cantidad * d.precio_unitario), 2)            AS venta_bruta,
       ROUND(SUM(CASE WHEN v.metodo_pago = 'Tarjeta'
                      THEN d.cantidad * d.precio_unitario ELSE 0 END)
             * (SELECT valor FROM parametro WHERE clave = 'comision_tarjeta'), 2) AS comision_banco,
       ROUND(SUM(d.cantidad * d.precio_unitario)
             - SUM(CASE WHEN v.metodo_pago = 'Tarjeta'
                        THEN d.cantidad * d.precio_unitario ELSE 0 END)
               * (SELECT valor FROM parametro WHERE clave = 'comision_tarjeta'), 2) AS neto_proveedor
  FROM detalle_venta d
  JOIN venta v      ON v.id_venta     = d.id_venta
  JOIN producto p   ON p.id_producto  = d.id_producto
  JOIN marca m      ON m.id_marca     = p.id_marca
  JOIN proveedor pr ON pr.id_proveedor = m.id_proveedor
 WHERE v.fecha_hora >= '2026-10-01' AND v.fecha_hora < '2026-12-01'
 GROUP BY pr.id_proveedor, pr.nombre_comercial
HAVING SUM(d.cantidad * d.precio_unitario) >= 100
 ORDER BY neto_proveedor DESC;

-- ---------------------------------------------------------------------
-- Q4 · ¿Qué productos activos no tuvieron movimientos en los últimos 30 días?
-- Caso de uso: CU-04 Consultar productos / CU-11 Reporte.  Tipo: SUBCONSULTA
-- ---------------------------------------------------------------------
SELECT p.codigo, p.nombre, p.existencias, p.precio
  FROM producto p
 WHERE p.estado = 'Activo'
   AND p.id_producto NOT IN (SELECT m.id_producto
                               FROM movimiento m
                              WHERE m.fecha_hora >= date('2026-11-01', '-30 days'))
 ORDER BY p.codigo;

-- ---------------------------------------------------------------------
-- Q5 · ¿Cuál es la función actual de cada empleado activo?
-- Caso de uso: CU-08 Asignar función a empleado.  Tipo: SUBCONSULTA correlacionada + LEFT JOIN
-- (los empleados sin función asignada también aparecen)
-- ---------------------------------------------------------------------
SELECT e.usuario, e.nombre || ' ' || e.apellidos AS empleado, r.nombre AS rol,
       COALESCE(f.nombre, '(sin función)') AS funcion_actual,
       a.fecha_cambio
  FROM empleado e
  JOIN rol r ON r.id_rol = e.id_rol
  LEFT JOIN asignacion_funcion a
         ON a.id_empleado = e.id_empleado
        AND a.fecha_cambio = (SELECT MAX(a2.fecha_cambio)
                                FROM asignacion_funcion a2
                               WHERE a2.id_empleado = e.id_empleado)
  LEFT JOIN funcion_laboral f ON f.id_funcion = a.id_funcion
 WHERE e.estado = 'Activo'
 ORDER BY e.id_empleado;

-- ---------------------------------------------------------------------
-- Q6 · ¿Cuántas piezas y cuánto dinero hay en inventario por categoría?
-- Caso de uso: CU-11 Reporte de existencias.  Tipo: VISTA + GROUP BY
-- ---------------------------------------------------------------------
DROP VIEW IF EXISTS v_reporte_existencias;
CREATE VIEW v_reporte_existencias AS
SELECT c.nombre AS categoria,
       COUNT(p.id_producto)                         AS productos,
       SUM(p.existencias)                           AS piezas,
       ROUND(SUM(p.existencias * p.precio), 2)      AS valor_inventario,
       SUM(CASE WHEN p.existencias <= p.stock_minimo THEN 1 ELSE 0 END) AS en_alerta
  FROM categoria c
  JOIN producto p ON p.id_categoria = c.id_categoria AND p.estado = 'Activo'
 GROUP BY c.id_categoria, c.nombre;

SELECT * FROM v_reporte_existencias ORDER BY valor_inventario DESC;

-- ---------------------------------------------------------------------
-- Q7 · ¿Existe una cuenta activa con este usuario? (el hash se compara en la aplicación)
-- Caso de uso: CU-01 Iniciar sesión (ALG-01).  Tipo: consulta con 1 JOIN
-- En el código se escribe con parámetro: WHERE e.usuario = ? (ver 04_seguridad.sql y seguridad_demo.py)
-- ---------------------------------------------------------------------
SELECT e.id_empleado, e.usuario, e.hash_contrasena, r.nombre AS rol
  FROM empleado e
  JOIN rol r ON r.id_rol = e.id_rol
 WHERE e.usuario = 'rosa'
   AND e.estado = 'Activo';

-- ---------------------------------------------------------------------
-- Q8 · Buscar productos por parte del nombre, de la categoría o del código
-- Caso de uso: CU-04 Buscar y consultar productos (RNF-03).  Tipo: JOIN con filtro LIKE
-- ---------------------------------------------------------------------
SELECT p.codigo, p.nombre, c.nombre AS categoria, p.existencias, p.precio
  FROM producto p
  JOIN categoria c ON c.id_categoria = p.id_categoria
 WHERE p.estado = 'Activo'
   AND (p.nombre LIKE '%catrina%' OR c.nombre LIKE '%catrina%' OR p.codigo LIKE '%catrina%')
 ORDER BY p.nombre;
