-- =====================================================================
-- Ventur · A09 · 04_seguridad.sql
-- Seguridad de los datos. Ejecutar después de 01_ddl.sql y 02_dml.sql.
--
-- NOTA SOBRE EL SGBD: SQLite no tiene usuarios de base de datos ni GRANT/REVOKE,
-- porque el motor es un archivo que se abre desde la propia aplicación. Por eso el
-- "privilegio mínimo" se aplica en tres capas (ver seguridad_demo.py y el documento):
--   1) permisos del archivo .db en el sistema de la tablet (solo la app lo lee y escribe);
--   2) la conexión de la app usa set_authorizer() y bloquea DROP, ALTER, ATTACH y PRAGMA peligrosos;
--   3) los reportes usan una conexión de solo lectura (file:ventur.db?mode=ro).
-- Este script agrega la cuarta capa: protecciones dentro de la propia base de datos.
-- =====================================================================
PRAGMA foreign_keys = ON;

-- 1) La aplicación nunca lee el hash de contraseña en pantallas de empleados:
--    usa esta vista, que no expone hash_contrasena.
DROP VIEW IF EXISTS v_empleado_publico;
CREATE VIEW v_empleado_publico AS
SELECT e.id_empleado, e.nombre, e.apellidos, e.usuario, r.nombre AS rol, e.estado
  FROM empleado e
  JOIN rol r ON r.id_rol = e.id_rol;

-- 2) El historial es de solo agregar: no se edita ni se borra (RN-09, RN-12).
CREATE TRIGGER IF NOT EXISTS trg_movimiento_no_update
BEFORE UPDATE ON movimiento
BEGIN SELECT RAISE(ABORT, 'El historial de movimientos no se puede modificar'); END;

CREATE TRIGGER IF NOT EXISTS trg_movimiento_no_delete
BEFORE DELETE ON movimiento
BEGIN SELECT RAISE(ABORT, 'El historial de movimientos no se puede borrar'); END;

CREATE TRIGGER IF NOT EXISTS trg_respaldo_no_delete
BEFORE DELETE ON respaldo
BEGIN SELECT RAISE(ABORT, 'La bitácora de respaldos no se puede borrar'); END;

-- 3) Las bajas son lógicas (RN-12): no se permite DELETE físico de productos,
--    empleados ni ventas; se usa UPDATE ... SET estado = 'Baja'.
CREATE TRIGGER IF NOT EXISTS trg_producto_no_delete
BEFORE DELETE ON producto
BEGIN SELECT RAISE(ABORT, 'Use baja lógica: UPDATE producto SET estado = ''Baja'''); END;

CREATE TRIGGER IF NOT EXISTS trg_empleado_no_delete
BEFORE DELETE ON empleado
BEGIN SELECT RAISE(ABORT, 'Use baja lógica: UPDATE empleado SET estado = ''Baja'''); END;

CREATE TRIGGER IF NOT EXISTS trg_venta_no_delete
BEFORE DELETE ON venta
BEGIN SELECT RAISE(ABORT, 'Las ventas registradas no se pueden borrar'); END;

-- 4) Un empleado dado de baja no puede registrar movimientos ni ventas (RN-14).
CREATE TRIGGER IF NOT EXISTS trg_movimiento_empleado_activo
BEFORE INSERT ON movimiento
WHEN (SELECT estado FROM empleado WHERE id_empleado = NEW.id_empleado) = 'Baja'
BEGIN SELECT RAISE(ABORT, 'El empleado está dado de baja'); END;

CREATE TRIGGER IF NOT EXISTS trg_venta_empleado_activo
BEFORE INSERT ON venta
WHEN (SELECT estado FROM empleado WHERE id_empleado = NEW.id_empleado) = 'Baja'
BEGIN SELECT RAISE(ABORT, 'El empleado está dado de baja'); END;

-- 5) Contraseñas: la base solo guarda el hash bcrypt (60 caracteres que empiezan con $2b$).
--    Este CHECK evita guardar por error una contraseña en texto plano.
--    (SQLite no permite agregar un CHECK con ALTER; por eso se aplica con un trigger.)
CREATE TRIGGER IF NOT EXISTS trg_empleado_hash_valido_ins
BEFORE INSERT ON empleado
WHEN NEW.hash_contrasena NOT LIKE '$2_$%' OR length(NEW.hash_contrasena) <> 60
BEGIN SELECT RAISE(ABORT, 'La contraseña debe guardarse como hash bcrypt'); END;

CREATE TRIGGER IF NOT EXISTS trg_empleado_hash_valido_upd
BEFORE UPDATE OF hash_contrasena ON empleado
WHEN NEW.hash_contrasena NOT LIKE '$2_$%' OR length(NEW.hash_contrasena) <> 60
BEGIN SELECT RAISE(ABORT, 'La contraseña debe guardarse como hash bcrypt'); END;
