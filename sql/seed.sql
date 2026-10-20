USE restaurante_gestion;

INSERT IGNORE INTO rol (nombre_rol, descripcion) VALUES
('ADMIN', 'Acceso total al sistema, incluidos usuarios y configuración.'),
('GERENTE', 'Gestión operativa, personal, carta, clientes, salón y pedidos.'),
('CAJERO', 'Gestión de clientes, pedidos y consulta de carta/salón.'),
('MOZO', 'Carga y seguimiento de pedidos, consulta de clientes, carta y mesas.'),
('CONSULTA', 'Acceso de solo lectura a información habilitada.');

INSERT IGNORE INTO estado_pedido (nombre_estado) VALUES
('Pendiente'), ('En preparación'), ('Listo'), ('Entregado'), ('Cancelado');

INSERT IGNORE INTO tipo_comprobante (nombre_tipo_comprobante) VALUES
('Ticket'), ('Factura A'), ('Factura B'), ('Factura C'), ('Nota de crédito');

INSERT IGNORE INTO tipo_cliente (nombre_tipo_cliente) VALUES
('Ocasional'), ('Frecuente'), ('Empresa');

INSERT IGNORE INTO estado_condicion (nombre_estado_condicion, empresa_de_capacitacion) VALUES
('Activo', NULL), ('Suspendido', NULL), ('Finalizado', NULL);

INSERT IGNORE INTO condicion (nombre_condicion, id_estado_condicion)
SELECT 'Relación de dependencia', id_estado_condicion
FROM estado_condicion WHERE nombre_estado_condicion = 'Activo';

INSERT IGNORE INTO condicion (nombre_condicion, id_estado_condicion)
SELECT 'Eventual', id_estado_condicion
FROM estado_condicion WHERE nombre_estado_condicion = 'Activo';

INSERT IGNORE INTO area (nombre_area) VALUES
('Cocina'), ('Salón'), ('Caja'), ('Administración');

INSERT IGNORE INTO cargo (nombre_cargo) VALUES
('Cocinero/a'), ('Mozo/a'), ('Cajero/a'), ('Encargado/a'), ('Gerente');

INSERT IGNORE INTO categoria (nombre_categoria, descripcion_categoria) VALUES
('Entradas', 'Platos de entrada'),
('Principales', 'Platos principales'),
('Postres', 'Postres'),
('Bebidas', 'Bebidas con y sin alcohol');
