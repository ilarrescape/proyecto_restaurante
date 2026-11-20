# Módulos de Cargo y Tipo de Comprobante

## Objetivo

Esta implementación agrega a la interfaz de Streamlit la administración de cargos y tipos de comprobante. Reutiliza las clases existentes `Cargo` y `TipoComprobante`, el motor y las sesiones configuradas en `src/database.py`, y el control de acceso ADMIN de `src/services/auth.py`. No modifica los modelos ni el esquema de base de datos. El módulo `AreaCargo` queda fuera de alcance.

## Funcionalidades

### Cargos

- Registrar cargos con nombre obligatorio de hasta 100 caracteres.
- Consultar los cargos registrados, ordenados por nombre.
- Modificar el nombre de un cargo.
- Eliminar un cargo cuando no está asignado a empleados.
- Evitar nombres duplicados.

La asociación con áreas (`area_cargo`) se conserva en la base según sus claves foráneas y reglas existentes. Esta implementación no administra esa asociación. La base define eliminación en cascada para las asociaciones con áreas y restricción para asignaciones de empleados; la aplicación comprueba primero que no haya empleados vinculados.

### Tipos de comprobante

- Registrar tipos con nombre obligatorio de hasta 100 caracteres.
- Consultar los tipos registrados, ordenados por nombre.
- Modificar el nombre de un tipo.
- Eliminar un tipo solamente si no está utilizado por pedidos.
- Evitar nombres duplicados.

## Archivos

- `src/services/cargo.py`: operaciones de consulta, alta, modificación y baja de cargos.
- `src/services/tipo_comprobante.py`: operaciones de consulta, alta, modificación y baja de tipos de comprobante.
- `app.py`: agrega las opciones **Cargos** y **Tipos de comprobante** al menú Administración.

Cada escritura desde la interfaz utiliza `factory.begin()` para mantener el manejo transaccional ya utilizado por la aplicación. Los servicios realizan las validaciones y requieren un usuario ADMIN, por lo que las reglas se aplican aunque se invoquen fuera de la pantalla.

## Cómo probar manualmente

1. Configurar MySQL y las variables de entorno siguiendo `docs/autenticacion.md`.
2. Asegurarse de que el esquema esté inicializado y que haya una cuenta ADMIN. La semilla ya carga algunos cargos y tipos de comprobante; por eso los selectores pueden mostrar registros existentes.
3. Iniciar la aplicación desde la raíz del proyecto:

   ```bash
   streamlit run app.py
   ```

4. Iniciar sesión con la cuenta ADMIN y abrir **Cargos** en el menú lateral.
5. Registrar un cargo nuevo. Debe aparecer en el listado. Intentar repetir el mismo nombre debe mostrar un error de duplicado.
6. Seleccionar el cargo creado, cambiar el nombre y guardar. El listado debe mostrar el nombre actualizado.
7. Eliminar el cargo de prueba si no está asignado a un empleado. Para verificar la protección, intentar eliminar un cargo que figure en `restaurante_cargo_empleado`: la operación debe rechazarse.
8. Abrir **Tipos de comprobante** y repetir el alta, consulta, modificación y baja con un tipo de prueba.
9. Para verificar la protección de pedidos, intentar eliminar un tipo cuyo `id_tipo_comprobante` aparezca en `pedido`: la aplicación debe impedirlo y explicar que está en uso.

Las pruebas de eliminación protegida deben realizarse con registros vinculados en la base de pruebas. No conviene usar registros productivos para estas comprobaciones.

## Alcance y consideraciones

- Solo ADMIN puede consultar o modificar estos catálogos desde los servicios.
- Los nombres son únicos según las restricciones actuales de la base. La validación de aplicación evita la mayoría de duplicados; ante escrituras concurrentes, la restricción única de MySQL sigue siendo la protección final.
- La interfaz informa los errores de validación de los servicios. Los errores de base de datos no previstos conservan el mensaje general de SQLAlchemy definido por `app.py`.
- No se implementa la gestión de áreas ni de asociaciones área-cargo.
