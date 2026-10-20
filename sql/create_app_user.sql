CREATE USER IF NOT EXISTS 'restaurante_app'@'localhost' IDENTIFIED BY 'cambiar_clave';
GRANT SELECT, INSERT, UPDATE, DELETE ON restaurante_gestion.* TO 'restaurante_app'@'localhost';
FLUSH PRIVILEGES;
