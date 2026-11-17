-- =====================================================================
-- Ventur · A09 · 02_dml.sql
-- Datos de prueba ANÓNIMOS (nombres y negocios ficticios). Ejecutar después de 01_ddl.sql.
-- Contraseñas de prueba: rosa = Abc123; los demás = Demo-<usuario> (solo para pruebas).
-- Las existencias iniciales se registran en producto; los movimientos y las ventas
-- las ajustan mediante los triggers del DDL.
-- Casos límite incluidos: empleado en baja, empleado sin función y sin movimientos,
-- producto agotado, productos en stock bajo, producto sin movimientos, producto propio
-- (sin marca), producto dado de baja, proveedor sin marcas, marca sin productos,
-- precio histórico distinto al actual en una venta y un respaldo fallido.
-- =====================================================================
PRAGMA foreign_keys = ON;
BEGIN TRANSACTION;

INSERT INTO rol (nombre) VALUES ('Dueña'), ('Empleado');
INSERT INTO funcion_laboral (nombre) VALUES ('Atención a clientes'), ('Inventario'), ('Caja'), ('Exhibición y limpieza');
INSERT INTO categoria (nombre) VALUES ('Hogar'), ('Decoración'), ('Accesorios'), ('Papelería'), ('Textil');
INSERT INTO parametro (clave, valor, descripcion) VALUES ('comision_tarjeta', 0.04, 'Comisión bancaria sobre pagos con tarjeta; se descuenta al proveedor');
INSERT INTO empleado (nombre, apellidos, usuario, hash_contrasena, id_rol, estado, fecha_alta, fecha_baja) VALUES
  ('Rosa', 'Ejemplo A', 'rosa', '$2b$12$keZ/pg5P6WsVfs3XeHiqM.MBTRSv0oWzyzQUXRpm8fEe2sbrBYR2S', 1, 'Activo', '2026-09-14', NULL),
  ('Luis', 'Ejemplo B', 'luis', '$2b$12$YLnrpCQ4grqzPLPytSWEj.Y1DBaaLszIowDZa.dTRi82AximM7tYC', 2, 'Activo', '2026-09-21', NULL),
  ('Marta', 'Ejemplo C', 'marta', '$2b$12$tMeRkp8n9gjf5ilesyxMQOdtzv6NuOo5z75586xcN0lFRf5.47yyG', 2, 'Activo', '2026-09-21', NULL),
  ('Pablo', 'Ejemplo D', 'pablo', '$2b$12$d2X6nN5TNUAJkG60Cl.qVOmedDLXGN0QnxO3e/rFLFXzY5aLMQmpm', 2, 'Activo', '2026-09-28', NULL),
  ('Elena', 'Ejemplo E', 'elena', '$2b$12$riPq/jIO09M8ZI1KwQMxC.zBUtlGzbEeNwe1Kgf7GzXl70Pk3jGLi', 2, 'Activo', '2026-09-28', NULL),
  ('Iván', 'Ejemplo F', 'ivan', '$2b$12$gZdOC9xcInr0Sr4g2cJAi.TEMIAZSIMryVO.6bZ7V7svFUYFrblRy', 2, 'Activo', '2026-10-01', NULL),
  ('Carla', 'Ejemplo G', 'carla', '$2b$12$i7HdxZ9IAyJVbbo2NJJYO.I/UPWKTsOIYB7klexdCeeOGZ5jgSbeq', 2, 'Activo', '2026-10-01', NULL),
  ('Hugo', 'Ejemplo H', 'hugo', '$2b$12$iryxYECa4lkTbkC/ONw3..PnhI1djn9v.7NU5Ifdx6wfIp18iC63O', 2, 'Baja', '2026-09-14', '2026-10-20'),
  ('Nora', 'Ejemplo I', 'nora', '$2b$12$3BBgDseuqrcXr0W3WjNmf.vhG1/5o1Cx9qHYopMfQj8W5pKl5ybyi', 2, 'Activo', '2026-10-05', NULL),
  ('Saúl', 'Ejemplo J', 'saul', '$2b$12$.3q7Tely9sclxh4EcTcsIuqJKTp/YcFqp9I/sqDugZtv61vAMbAuy', 2, 'Activo', '2026-10-05', NULL);
INSERT INTO asignacion_funcion (id_empleado, id_funcion, fecha_cambio) VALUES
  (2, 1, '2026-09-21 09:00:00'),
  (2, 2, '2026-10-15 10:00:00'),
  (3, 3, '2026-09-21 09:05:00'),
  (4, 2, '2026-09-28 09:00:00'),
  (5, 1, '2026-09-28 09:10:00'),
  (6, 3, '2026-10-01 09:00:00'),
  (6, 1, '2026-10-12 09:00:00'),
  (7, 4, '2026-10-01 09:15:00'),
  (8, 1, '2026-09-14 09:00:00'),
  (10, 2, '2026-10-05 09:00:00');
INSERT INTO proveedor (nombre_comercial) VALUES
  ('Barro Vivo'),
  ('Papel y Color'),
  ('Hilos de Durango'),
  ('Plata Sierra'),
  ('Alebrijes Casa Verde'),
  ('Velas del Valle'),
  ('Vidrio Soplado Rivera'),
  ('Cuadernos Tinta'),
  ('Madera Noble'),
  ('Colectivo Mariposa');
INSERT INTO marca (nombre, id_proveedor) VALUES
  ('Barro Vivo', 1),
  ('Talavera Norte', 1),
  ('Papel y Color', 2),
  ('Hilos de Durango', 3),
  ('Rebozos Luna', 3),
  ('Plata Sierra', 4),
  ('Casa Verde', 5),
  ('Velas del Valle', 6),
  ('Vidrio Rivera', 7),
  ('Tinta Viva', 8),
  ('Mariposa', 10);
INSERT INTO producto (codigo, nombre, id_categoria, id_marca, precio, existencias, stock_minimo, estado) VALUES
  ('P-001', 'Taza de barro pintada', 1, 1, 85, 12, 3, 'Activo'),
  ('P-002', 'Vaso de vidrio soplado', 1, 9, 40, 6, 2, 'Activo'),
  ('P-003', 'Catrina de papel maché chica', 2, 3, 120, 8, 2, 'Activo'),
  ('P-004', 'Catrina de barro grande', 2, 2, 350, 5, 2, 'Activo'),
  ('P-005', 'Collar de plata con dije', 3, 6, 280, 10, 3, 'Activo'),
  ('P-006', 'Aretes bordados', 3, 4, 95, 15, 5, 'Activo'),
  ('P-007', 'Cuaderno artesanal', 4, NULL, 60, 20, 5, 'Activo'),
  ('P-008', 'Marcapáginas ilustrado', 4, 10, 25, 40, 10, 'Activo'),
  ('P-009', 'Rebozo de algodón', 5, 5, 450, 6, 3, 'Activo'),
  ('P-010', 'Mantel bordado', 5, 4, 380, 6, 2, 'Activo'),
  ('P-011', 'Vela aromática', 1, 8, 70, 18, 4, 'Activo'),
  ('P-012', 'Llavero de alebrije', 3, 7, 35, 30, 8, 'Activo'),
  ('P-013', 'Alebrije mediano', 2, 7, 150, 7, 2, 'Activo'),
  ('P-014', 'Posavasos de madera', 1, NULL, 30, 0, 0, 'Baja');
-- Movimientos manuales (el trigger actualiza las existencias)
INSERT INTO movimiento (id_producto, id_empleado, tipo, cantidad, fecha_hora, origen) VALUES
  (1, 8, 'Salida', 2, '2026-10-02 10:15:00', 'Manual'),
  (1, 4, 'Entrada', 10, '2026-10-05 09:10:00', 'Manual'),
  (2, 2, 'Salida', 4, '2026-10-06 11:20:00', 'Manual'),
  (3, 1, 'Salida', 8, '2026-10-08 16:40:00', 'Manual'),
  (4, 4, 'Entrada', 3, '2026-10-09 09:30:00', 'Manual'),
  (5, 2, 'Salida', 2, '2026-10-10 13:05:00', 'Manual'),
  (6, 3, 'Salida', 5, '2026-10-11 12:00:00', 'Manual'),
  (7, 5, 'Salida', 6, '2026-10-12 11:45:00', 'Manual'),
  (8, 4, 'Entrada', 20, '2026-10-12 15:20:00', 'Manual'),
  (9, 6, 'Salida', 3, '2026-10-14 10:10:00', 'Manual'),
  (10, 7, 'Salida', 1, '2026-10-15 17:30:00', 'Manual'),
  (11, 10, 'Entrada', 6, '2026-10-16 09:50:00', 'Manual'),
  (12, 2, 'Salida', 10, '2026-10-17 14:15:00', 'Manual'),
  (11, 5, 'Salida', 4, '2026-10-19 12:25:00', 'Manual'),
  (5, 4, 'Entrada', 5, '2026-10-21 09:40:00', 'Manual'),
  (10, 2, 'Salida', 2, '2026-10-23 16:00:00', 'Manual');
-- Ventas (cada detalle genera su salida de inventario con el trigger)
INSERT INTO venta (id_empleado, metodo_pago, fecha_hora) VALUES
  (3, 'Tarjeta', '2026-10-24 10:05:00'),
  (2, 'Efectivo', '2026-10-24 12:30:00'),
  (6, 'Tarjeta', '2026-10-25 11:15:00'),
  (3, 'Efectivo', '2026-10-25 13:40:00'),
  (5, 'Tarjeta', '2026-10-26 12:10:00'),
  (7, 'Efectivo', '2026-10-27 16:20:00'),
  (2, 'Tarjeta', '2026-10-28 11:00:00'),
  (10, 'Efectivo', '2026-10-29 15:35:00'),
  (4, 'Tarjeta', '2026-10-30 10:45:00'),
  (3, 'Efectivo', '2026-10-30 17:05:00'),
  (6, 'Tarjeta', '2026-10-31 12:50:00'),
  (5, 'Efectivo', '2026-11-01 11:30:00');
INSERT INTO detalle_venta (id_venta, id_producto, cantidad, precio_unitario) VALUES
  (1, 1, 2, 80),
  (1, 7, 1, 60),
  (2, 6, 1, 95),
  (3, 4, 1, 350),
  (4, 11, 2, 70),
  (4, 12, 3, 35),
  (5, 9, 1, 450),
  (6, 8, 4, 25),
  (7, 5, 1, 280),
  (7, 6, 2, 95),
  (8, 10, 1, 380),
  (9, 1, 1, 85),
  (9, 11, 1, 70),
  (10, 12, 2, 35),
  (11, 4, 1, 350),
  (11, 7, 2, 60),
  (12, 8, 6, 25);
INSERT INTO respaldo (id_empleado, fecha_hora, tipo, archivo, resultado) VALUES
  (1, '2026-10-09 18:00:00', 'Respaldo', 'respaldos/respaldo_2026-10-09.db', 'Exitoso'),
  (1, '2026-10-16 18:00:00', 'Respaldo', 'respaldos/respaldo_2026-10-16.db', 'Exitoso'),
  (1, '2026-10-23 18:00:00', 'Respaldo', 'respaldos/respaldo_2026-10-23.db', 'Exitoso'),
  (1, '2026-10-30 18:00:00', 'Respaldo', 'respaldos/respaldo_2026-10-30.db', 'Fallido'),
  (1, '2026-10-30 18:10:00', 'Respaldo', 'respaldos/respaldo_2026-10-30.db', 'Exitoso');

COMMIT;
