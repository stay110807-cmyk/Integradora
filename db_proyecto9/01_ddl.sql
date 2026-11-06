-- =====================================================================
-- Ventur · A09 · 01_ddl.sql  (SQLite 3.31 o superior)
-- Crea la estructura de la base de datos. Ejecutar primero.
-- Importante: SQLite exige activar las llaves foráneas en CADA conexión.
-- =====================================================================
PRAGMA foreign_keys = ON;

-- ---------- Catálogos ----------
CREATE TABLE rol (
    id_rol      INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre      VARCHAR(20) NOT NULL UNIQUE
                CHECK (nombre IN ('Dueña', 'Empleado'))          -- RN-04, RN-13
);

CREATE TABLE funcion_laboral (
    id_funcion  INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre      VARCHAR(50) NOT NULL UNIQUE
                CHECK (length(nombre) >= 3)                      -- catálogo (RN-17)
);

CREATE TABLE categoria (
    id_categoria INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre       VARCHAR(50) NOT NULL UNIQUE
                 CHECK (length(nombre) >= 3)
);

CREATE TABLE parametro (
    clave       VARCHAR(30) PRIMARY KEY,
    valor       DECIMAL(10,4) NOT NULL CHECK (valor >= 0),
    descripcion VARCHAR(100) NOT NULL
);

-- ---------- Personal y acceso ----------
CREATE TABLE empleado (
    id_empleado     INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre          VARCHAR(60)  NOT NULL CHECK (length(nombre) >= 2),
    apellidos       VARCHAR(80)  NOT NULL CHECK (length(apellidos) >= 2),
    usuario         VARCHAR(30)  NOT NULL UNIQUE
                    CHECK (length(usuario) >= 3),                 -- RN-01
    hash_contrasena VARCHAR(100) NOT NULL,                       -- RN-02 (bcrypt, nunca texto plano)
    id_rol          INTEGER NOT NULL,
    estado          VARCHAR(10) NOT NULL DEFAULT 'Activo'
                    CHECK (estado IN ('Activo', 'Baja')),        -- RN-12, RN-14
    fecha_alta      TEXT NOT NULL DEFAULT (date('now', 'localtime')),
    fecha_baja      TEXT,
    CHECK ((estado = 'Activo' AND fecha_baja IS NULL)
        OR (estado = 'Baja'   AND fecha_baja IS NOT NULL)),
    FOREIGN KEY (id_rol) REFERENCES rol (id_rol)
        ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE asignacion_funcion (
    id_asignacion INTEGER PRIMARY KEY AUTOINCREMENT,
    id_empleado   INTEGER NOT NULL,
    id_funcion    INTEGER NOT NULL,
    fecha_cambio  TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    UNIQUE (id_empleado, fecha_cambio),
    FOREIGN KEY (id_empleado) REFERENCES empleado (id_empleado)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (id_funcion) REFERENCES funcion_laboral (id_funcion)
        ON DELETE RESTRICT ON UPDATE CASCADE
);

-- ---------- Proveedores y marcas ----------
CREATE TABLE proveedor (
    id_proveedor     INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_comercial VARCHAR(80) NOT NULL UNIQUE
                     CHECK (length(nombre_comercial) >= 2),
    estado           VARCHAR(10) NOT NULL DEFAULT 'Activo'
                     CHECK (estado IN ('Activo', 'Baja'))
);

CREATE TABLE marca (
    id_marca     INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre       VARCHAR(60) NOT NULL CHECK (length(nombre) >= 2),
    id_proveedor INTEGER NOT NULL,
    UNIQUE (nombre, id_proveedor),
    FOREIGN KEY (id_proveedor) REFERENCES proveedor (id_proveedor)
        ON DELETE RESTRICT ON UPDATE CASCADE
);

-- ---------- Inventario ----------
CREATE TABLE producto (
    id_producto  INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo       VARCHAR(20)  NOT NULL UNIQUE                    -- RN-06
                 CHECK (length(codigo) >= 2),
    nombre       VARCHAR(100) NOT NULL CHECK (length(nombre) >= 2),
    id_categoria INTEGER NOT NULL,
    id_marca     INTEGER,                                        -- NULL = producto propio del bazar
    precio       DECIMAL(10,2) NOT NULL CHECK (precio >= 0),     -- RN-07
    existencias  INTEGER NOT NULL DEFAULT 0 CHECK (existencias >= 0),  -- RN-07, RN-08
    stock_minimo INTEGER NOT NULL DEFAULT 0 CHECK (stock_minimo >= 0), -- RN-07
    estado       VARCHAR(10) NOT NULL DEFAULT 'Activo'
                 CHECK (estado IN ('Activo', 'Baja')),           -- RN-12 (baja lógica)
    FOREIGN KEY (id_categoria) REFERENCES categoria (id_categoria)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (id_marca) REFERENCES marca (id_marca)
        ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE movimiento (
    id_movimiento INTEGER PRIMARY KEY AUTOINCREMENT,
    id_producto   INTEGER NOT NULL,
    id_empleado   INTEGER NOT NULL,                              -- RN-09 (responsable)
    tipo          VARCHAR(10) NOT NULL CHECK (tipo IN ('Entrada', 'Salida')),
    cantidad      INTEGER NOT NULL CHECK (cantidad > 0),         -- RN-16
    fecha_hora    TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),  -- RN-09
    origen        VARCHAR(10) NOT NULL DEFAULT 'Manual'
                  CHECK (origen IN ('Manual', 'Venta')),
    FOREIGN KEY (id_producto) REFERENCES producto (id_producto)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (id_empleado) REFERENCES empleado (id_empleado)
        ON DELETE RESTRICT ON UPDATE CASCADE
);

-- ---------- Ventas (extensión de A08: la clienta pidió registrar ventas) ----------
CREATE TABLE venta (
    id_venta    INTEGER PRIMARY KEY AUTOINCREMENT,
    id_empleado INTEGER NOT NULL,
    fecha_hora  TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    metodo_pago VARCHAR(10) NOT NULL CHECK (metodo_pago IN ('Efectivo', 'Tarjeta')),
    FOREIGN KEY (id_empleado) REFERENCES empleado (id_empleado)
        ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE detalle_venta (
    id_venta        INTEGER NOT NULL,
    id_producto     INTEGER NOT NULL,
    cantidad        INTEGER NOT NULL CHECK (cantidad > 0),
    precio_unitario DECIMAL(10,2) NOT NULL CHECK (precio_unitario >= 0),
    PRIMARY KEY (id_venta, id_producto),
    FOREIGN KEY (id_venta) REFERENCES venta (id_venta)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (id_producto) REFERENCES producto (id_producto)
        ON DELETE RESTRICT ON UPDATE CASCADE
);

-- ---------- Respaldos (CU-10) ----------
CREATE TABLE respaldo (
    id_respaldo INTEGER PRIMARY KEY AUTOINCREMENT,
    id_empleado INTEGER NOT NULL,
    fecha_hora  TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    tipo        VARCHAR(15) NOT NULL CHECK (tipo IN ('Respaldo', 'Restauración')),
    archivo     VARCHAR(150) NOT NULL,
    resultado   VARCHAR(10) NOT NULL CHECK (resultado IN ('Exitoso', 'Fallido')),
    FOREIGN KEY (id_empleado) REFERENCES empleado (id_empleado)
        ON DELETE RESTRICT ON UPDATE CASCADE
);

-- ---------- Índices (búsqueda en menos de 2 s, RNF-03) ----------
CREATE INDEX idx_producto_nombre      ON producto (nombre);
CREATE INDEX idx_producto_categoria   ON producto (id_categoria);
CREATE INDEX idx_movimiento_producto  ON movimiento (id_producto, fecha_hora);
CREATE INDEX idx_movimiento_empleado  ON movimiento (id_empleado);
CREATE INDEX idx_venta_fecha          ON venta (fecha_hora);

-- ---------- Triggers de lógica de negocio ----------
-- RN-10: las existencias se recalculan al registrar un movimiento.
-- RN-08: si una salida supera las existencias, el CHECK (existencias >= 0)
--        hace fallar la sentencia completa y no se guarda nada.
CREATE TRIGGER trg_movimiento_actualiza_existencias
AFTER INSERT ON movimiento
BEGIN
    UPDATE producto
       SET existencias = existencias
           + CASE NEW.tipo WHEN 'Entrada' THEN NEW.cantidad ELSE -NEW.cantidad END
     WHERE id_producto = NEW.id_producto;
END;

-- No se registran movimientos de productos dados de baja (ALG-03).
CREATE TRIGGER trg_movimiento_producto_activo
BEFORE INSERT ON movimiento
WHEN (SELECT estado FROM producto WHERE id_producto = NEW.id_producto) = 'Baja'
BEGIN
    SELECT RAISE(ABORT, 'Producto no encontrado (dado de baja)');
END;

-- Una venta genera automáticamente la salida de inventario (una sola fuente de verdad).
CREATE TRIGGER trg_detalle_venta_genera_salida
AFTER INSERT ON detalle_venta
BEGIN
    INSERT INTO movimiento (id_producto, id_empleado, tipo, cantidad, fecha_hora, origen)
    SELECT NEW.id_producto, v.id_empleado, 'Salida', NEW.cantidad, v.fecha_hora, 'Venta'
      FROM venta v
     WHERE v.id_venta = NEW.id_venta;
END;
