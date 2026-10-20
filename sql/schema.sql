

CREATE DATABASE IF NOT EXISTS restaurante_gestion

USE restaurante_gestion;

CREATE TABLE IF NOT EXISTS ciudad (
    id_ciudad INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre_ciudad VARCHAR(100) NOT NULL,
    CONSTRAINT uq_ciudad_nombre UNIQUE (nombre_ciudad)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS restaurante (
    cuit BIGINT UNSIGNED PRIMARY KEY,
    razon_social VARCHAR(150) NOT NULL,
    nombre_fantasia VARCHAR(150) NOT NULL,
    direccion VARCHAR(180) NOT NULL,
    id_ciudad INT UNSIGNED NOT NULL,
    CONSTRAINT chk_restaurante_cuit CHECK (cuit BETWEEN 10000000000 AND 99999999999),
    CONSTRAINT fk_restaurante_ciudad
        FOREIGN KEY (id_ciudad) REFERENCES ciudad(id_ciudad)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    INDEX idx_restaurante_ciudad (id_ciudad),
    INDEX idx_restaurante_nombre (nombre_fantasia)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS area (
    id_area INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre_area VARCHAR(100) NOT NULL,
    CONSTRAINT uq_area_nombre UNIQUE (nombre_area)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS cargo (
    id_cargo INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre_cargo VARCHAR(100) NOT NULL,
    CONSTRAINT uq_cargo_nombre UNIQUE (nombre_cargo)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS area_cargo (
    id_area INT UNSIGNED NOT NULL,
    id_cargo INT UNSIGNED NOT NULL,
    PRIMARY KEY (id_area, id_cargo),
    CONSTRAINT fk_area_cargo_area
        FOREIGN KEY (id_area) REFERENCES area(id_area)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_area_cargo_cargo
        FOREIGN KEY (id_cargo) REFERENCES cargo(id_cargo)
        ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS estado_condicion (
    id_estado_condicion INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre_estado_condicion VARCHAR(100) NOT NULL,
    empresa_de_capacitacion VARCHAR(150) NULL,
    CONSTRAINT uq_estado_condicion_nombre UNIQUE (nombre_estado_condicion)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS condicion (
    id_condicion INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre_condicion VARCHAR(120) NOT NULL,
    id_estado_condicion INT UNSIGNED NOT NULL,
    CONSTRAINT uq_condicion_nombre UNIQUE (nombre_condicion),
    CONSTRAINT fk_condicion_estado
        FOREIGN KEY (id_estado_condicion) REFERENCES estado_condicion(id_estado_condicion)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    INDEX idx_condicion_estado (id_estado_condicion)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS empleado (
    dni BIGINT UNSIGNED PRIMARY KEY,
    nombre_empleado VARCHAR(100) NOT NULL,
    apellido_empleado VARCHAR(100) NOT NULL,
    fecha_nacimiento DATE NOT NULL,
    CONSTRAINT chk_empleado_dni CHECK (dni BETWEEN 1000000 AND 999999999)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS restaurante_cargo_empleado (
    id_cargo INT UNSIGNED NOT NULL,
    id_condicion INT UNSIGNED NOT NULL,
    cuit_restaurante BIGINT UNSIGNED NOT NULL,
    dni_empleado BIGINT UNSIGNED NOT NULL,
    PRIMARY KEY (id_cargo, id_condicion, cuit_restaurante, dni_empleado),
    CONSTRAINT fk_rce_cargo
        FOREIGN KEY (id_cargo) REFERENCES cargo(id_cargo)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_rce_condicion
        FOREIGN KEY (id_condicion) REFERENCES condicion(id_condicion)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_rce_restaurante
        FOREIGN KEY (cuit_restaurante) REFERENCES restaurante(cuit)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_rce_empleado
        FOREIGN KEY (dni_empleado) REFERENCES empleado(dni)
        ON UPDATE CASCADE ON DELETE CASCADE,
    INDEX idx_rce_restaurante (cuit_restaurante),
    INDEX idx_rce_empleado (dni_empleado)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS categoria (
    id_categoria INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre_categoria VARCHAR(100) NOT NULL,
    descripcion_categoria VARCHAR(255) NULL,
    CONSTRAINT uq_categoria_nombre UNIQUE (nombre_categoria)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS producto (
    id_producto INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre_producto VARCHAR(150) NOT NULL,
    descripcion VARCHAR(255) NULL,
    precio_unitario DECIMAL(12,2) NOT NULL,
    id_categoria_producto INT UNSIGNED NOT NULL,
    cuit_restaurante BIGINT UNSIGNED NOT NULL,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT chk_producto_precio CHECK (precio_unitario >= 0),
    CONSTRAINT fk_producto_categoria
        FOREIGN KEY (id_categoria_producto) REFERENCES categoria(id_categoria)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_producto_restaurante
        FOREIGN KEY (cuit_restaurante) REFERENCES restaurante(cuit)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT uq_producto_restaurante_nombre UNIQUE (cuit_restaurante, nombre_producto),
    INDEX idx_producto_categoria (id_categoria_producto),
    INDEX idx_producto_restaurante (cuit_restaurante)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS mesa (
    id_mesa INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    numero_referencia VARCHAR(30) NOT NULL,
    cantidad_sillas INT UNSIGNED NOT NULL DEFAULT 2,
    ubicacion_x DECIMAL(10,2) NULL,
    ubicacion_y DECIMAL(10,2) NULL,
    descripcion TEXT NULL,
    cuit_restaurante BIGINT UNSIGNED NOT NULL,
    activa BOOLEAN NOT NULL DEFAULT TRUE,
    CONSTRAINT chk_mesa_sillas CHECK (cantidad_sillas > 0),
    CONSTRAINT fk_mesa_restaurante
        FOREIGN KEY (cuit_restaurante) REFERENCES restaurante(cuit)
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT uq_mesa_restaurante_referencia UNIQUE (cuit_restaurante, numero_referencia),
    INDEX idx_mesa_restaurante (cuit_restaurante)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS tipo_cliente (
    id_tipo_cliente INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre_tipo_cliente VARCHAR(100) NOT NULL,
    CONSTRAINT uq_tipo_cliente_nombre UNIQUE (nombre_tipo_cliente)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS cliente (
    dni BIGINT UNSIGNED PRIMARY KEY,
    nombre_cliente VARCHAR(100) NOT NULL,
    apellido_cliente VARCHAR(100) NOT NULL,
    fecha_nacimiento DATE NULL,
    id_tipo_cliente INT UNSIGNED NOT NULL,
    CONSTRAINT chk_cliente_dni CHECK (dni BETWEEN 1000000 AND 999999999),
    CONSTRAINT fk_cliente_tipo
        FOREIGN KEY (id_tipo_cliente) REFERENCES tipo_cliente(id_tipo_cliente)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    INDEX idx_cliente_tipo (id_tipo_cliente),
    INDEX idx_cliente_nombre (apellido_cliente, nombre_cliente)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS tipo_comprobante (
    id_tipo_comprobante INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre_tipo_comprobante VARCHAR(100) NOT NULL,
    CONSTRAINT uq_tipo_comprobante_nombre UNIQUE (nombre_tipo_comprobante)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS estado_pedido (
    id_estado INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre_estado VARCHAR(100) NOT NULL,
    CONSTRAINT uq_estado_pedido_nombre UNIQUE (nombre_estado)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS pedido (
    id_pedido BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    id_tipo_comprobante INT UNSIGNED NOT NULL,
    cuit_restaurante BIGINT UNSIGNED NOT NULL,
    dni_empleado BIGINT UNSIGNED NOT NULL,
    dni_cliente BIGINT UNSIGNED NULL,
    id_mesa INT UNSIGNED NULL,
    id_estado INT UNSIGNED NOT NULL,
    fecha_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    total_pedido DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    observaciones VARCHAR(255) NULL,
    CONSTRAINT chk_pedido_total CHECK (total_pedido >= 0),
    CONSTRAINT fk_pedido_tipo_comprobante
        FOREIGN KEY (id_tipo_comprobante) REFERENCES tipo_comprobante(id_tipo_comprobante)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_pedido_restaurante
        FOREIGN KEY (cuit_restaurante) REFERENCES restaurante(cuit)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_pedido_empleado
        FOREIGN KEY (dni_empleado) REFERENCES empleado(dni)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_pedido_cliente
        FOREIGN KEY (dni_cliente) REFERENCES cliente(dni)
        ON UPDATE CASCADE ON DELETE SET NULL,
    CONSTRAINT fk_pedido_mesa
        FOREIGN KEY (id_mesa) REFERENCES mesa(id_mesa)
        ON UPDATE CASCADE ON DELETE SET NULL,
    CONSTRAINT fk_pedido_estado
        FOREIGN KEY (id_estado) REFERENCES estado_pedido(id_estado)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    INDEX idx_pedido_fecha (fecha_hora),
    INDEX idx_pedido_restaurante (cuit_restaurante),
    INDEX idx_pedido_estado (id_estado),
    INDEX idx_pedido_cliente (dni_cliente)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS detalle_pedido (
    id_producto INT UNSIGNED NOT NULL,
    id_pedido BIGINT UNSIGNED NOT NULL,
    cantidad INT UNSIGNED NOT NULL,
    subtotal DECIMAL(12,2) NOT NULL,
    PRIMARY KEY (id_producto, id_pedido),
    CONSTRAINT chk_detalle_cantidad CHECK (cantidad > 0),
    CONSTRAINT chk_detalle_subtotal CHECK (subtotal >= 0),
    CONSTRAINT fk_detalle_producto
        FOREIGN KEY (id_producto) REFERENCES producto(id_producto)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_detalle_pedido
        FOREIGN KEY (id_pedido) REFERENCES pedido(id_pedido)
        ON UPDATE CASCADE ON DELETE CASCADE,
    INDEX idx_detalle_pedido (id_pedido)
) ENGINE=InnoDB;

-- =========================================================
-- Seguridad / perfiles de usuario (entidades agregadas)
-- =========================================================
CREATE TABLE IF NOT EXISTS rol (
    id_rol INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre_rol VARCHAR(40) NOT NULL,
    descripcion VARCHAR(255) NULL,
    CONSTRAINT uq_rol_nombre UNIQUE (nombre_rol)
) ENGINE=InnoDB;

-- |Admin ---> restaurante La Nona
-- |Vendedor ---> restaurante La Nona
-- |Admin ---> restaurante Status
-- |Super Admin ---> Visualiza todo

CREATE TABLE IF NOT EXISTS usuario (
    id_usuario INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre_usuario VARCHAR(80) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    nombre_completo VARCHAR(150) NOT NULL,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    id_rol INT UNSIGNED NOT NULL,
    dni_empleado BIGINT UNSIGNED NULL,
    cuit_restaurante BIGINT UNSIGNED NULL,
    creado_en DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ultimo_acceso DATETIME NULL,
    CONSTRAINT uq_usuario_nombre UNIQUE (nombre_usuario),
    CONSTRAINT uq_usuario_empleado UNIQUE (dni_empleado),
    CONSTRAINT fk_usuario_rol
        FOREIGN KEY (id_rol) REFERENCES rol(id_rol)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_usuario_empleado
        FOREIGN KEY (dni_empleado) REFERENCES empleado(dni)
        ON UPDATE CASCADE ON DELETE SET NULL,
    CONSTRAINT fk_usuario_restaurante
        FOREIGN KEY (cuit_restaurante) REFERENCES restaurante(cuit)
        ON UPDATE CASCADE ON DELETE SET NULL,
    INDEX idx_usuario_rol (id_rol)
) ENGINE=InnoDB;
