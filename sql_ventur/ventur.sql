PRAGMA foreign_keys = ON;

CREATE TABLE proveedores (
    id_proveedor   INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_prove   TEXT    NOT NULL,
    fecha_ingreso  TEXT    NOT NULL,                      
    estatus        INTEGER NOT NULL DEFAULT 1 CHECK (estatus IN (0,1))
);

CREATE TABLE proveedores_contactos (
    id_contacto    INTEGER PRIMARY KEY AUTOINCREMENT,
    id_proveedor   INTEGER NOT NULL,
    tipo_contacto  TEXT    NOT NULL
                   CHECK (tipo_contacto IN ('telefono','correo','whatsapp','red_social')),
    contacto       TEXT    NOT NULL,
    FOREIGN KEY (id_proveedor) REFERENCES proveedores(id_proveedor)
        ON DELETE CASCADE
);

CREATE TABLE marcas (
    id_marca       INTEGER PRIMARY KEY AUTOINCREMENT,
    id_proveedor   INTEGER NOT NULL,
    nombre_marca   TEXT    NOT NULL,
    FOREIGN KEY (id_proveedor) REFERENCES proveedores(id_proveedor)
);


CREATE TABLE productos (
    id_producto    INTEGER PRIMARY KEY AUTOINCREMENT,
    id_marca       INTEGER NOT NULL,
    nombre_produ   TEXT    NOT NULL,
    descripcion    TEXT,
    precio_venta   INTEGER NOT NULL CHECK (precio_venta >= 0),   
    stock_produ    INTEGER NOT NULL DEFAULT 0 CHECK (stock_produ >= 0),
    codigo_barras  TEXT    UNIQUE,                               
    estatus        INTEGER NOT NULL DEFAULT 1 CHECK (estatus IN (0,1)),
    FOREIGN KEY (id_marca) REFERENCES marcas(id_marca)
);

CREATE TABLE empleados (
    id_empleado     INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_empleado TEXT    NOT NULL,
    rol             TEXT    NOT NULL,
    telefono        TEXT,
    correo          TEXT,
    direccion       TEXT
);

CREATE TABLE movimientos_inventario (
    id_movimiento  INTEGER PRIMARY KEY AUTOINCREMENT,
    id_producto    INTEGER NOT NULL,
    id_empleado    INTEGER NOT NULL,
    tipo           TEXT    NOT NULL
                   CHECK (tipo IN ('entrega','retiro','ajuste','merma')),
    cantidad       INTEGER NOT NULL CHECK (cantidad > 0),
    fecha_hora     TEXT    NOT NULL DEFAULT (datetime('now','localtime')),
    observaciones  TEXT,
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto),
    FOREIGN KEY (id_empleado) REFERENCES empleados(id_empleado)
);

CREATE TABLE ventas (
    id_venta            INTEGER PRIMARY KEY AUTOINCREMENT,
    id_empleado         INTEGER NOT NULL,
    fecha_hora          TEXT    NOT NULL DEFAULT (datetime('now','localtime')),
    forma_pago          TEXT    NOT NULL CHECK (forma_pago IN ('efectivo','tarjeta')),
    porcentaje_tarjeta  INTEGER NOT NULL DEFAULT 0
                        CHECK (porcentaje_tarjeta >= 0),       
    FOREIGN KEY (id_empleado) REFERENCES empleados(id_empleado)
);

CREATE TABLE pagos_proveedores (
    id_pago         INTEGER PRIMARY KEY AUTOINCREMENT,
    id_proveedor    INTEGER NOT NULL,
    id_empleado     INTEGER,                                
    fecha_pago      TEXT    NOT NULL,
    periodo_inicio  TEXT    NOT NULL,
    periodo_fin     TEXT    NOT NULL,                       
    monto_total     INTEGER NOT NULL CHECK (monto_total >= 0),  
    CHECK (periodo_fin >= periodo_inicio),
    FOREIGN KEY (id_proveedor) REFERENCES proveedores(id_proveedor),
    FOREIGN KEY (id_empleado)  REFERENCES empleados(id_empleado)
);

CREATE TABLE detalle_venta (
    id_detalle       INTEGER PRIMARY KEY AUTOINCREMENT,
    id_venta         INTEGER NOT NULL,
    id_producto      INTEGER NOT NULL,
    id_pago          INTEGER,                               
    cantidad         INTEGER NOT NULL CHECK (cantidad > 0), 
    precio_unitario  INTEGER NOT NULL CHECK (precio_unitario >= 0), 
    monto_proveedor  INTEGER NOT NULL CHECK (monto_proveedor >= 0), 
    FOREIGN KEY (id_venta)    REFERENCES ventas(id_venta),
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto),
    FOREIGN KEY (id_pago)     REFERENCES pagos_proveedores(id_pago)
);

CREATE TABLE notificaciones (
    id_notificacion  INTEGER PRIMARY KEY AUTOINCREMENT,
    id_venta         INTEGER NOT NULL,
    destinatario     TEXT    NOT NULL,
    estado           TEXT    NOT NULL DEFAULT 'pendiente'
                     CHECK (estado IN ('pendiente','enviada','error')),
    fecha_creacion   TEXT    NOT NULL DEFAULT (datetime('now','localtime')),
    fecha_envio      TEXT,
    FOREIGN KEY (id_venta) REFERENCES ventas(id_venta)
);