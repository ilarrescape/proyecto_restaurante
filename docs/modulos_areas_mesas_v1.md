# Implementación de los módulos de áreas y mesas

## Alcance

Esta versión agrega pantallas y operaciones para administrar áreas, asociar cargos a cada área y mantener las mesas de los restaurantes. Se apoya en las clases y tablas que ya estaban definidas en `src/models.py` y `sql/schema.sql`; no requiere crear ni alterar tablas.

## Módulo de áreas

La pantalla **Áreas** permite:

- Consultar el listado de áreas y los cargos asociados.
- Crear un área con un nombre obligatorio de hasta 100 caracteres.
- Cambiar el nombre de un área.
- Asociar uno o varios cargos existentes, quitar asociaciones o reemplazar el conjunto de cargos.
- Eliminar un área después de confirmación. Al eliminarla también se eliminan sus filas de relación en `area_cargo`; los cargos permanecen.

Los nombres duplicados se rechazan. Las áreas son un catálogo global y no tienen atributo de estado en el modelo actual. No se crean cargos desde esta pantalla: se eligen los registros ya existentes en la tabla `cargo`.

## Módulo de mesas

La pantalla **Mesas** permite seleccionar un restaurante autorizado y:

- Consultar el listado de mesas, su capacidad, ubicación, descripción y estado.
- Crear una mesa con referencia, cantidad de sillas y coordenadas/descripción opcionales.
- Editar esos datos.
- Activar o desactivar una mesa mediante el campo `activa`.
- Eliminar una mesa después de confirmación si no tiene pedidos asociados.

La referencia es obligatoria y admite hasta 30 caracteres; debe ser única dentro del restaurante. La cantidad de sillas debe ser mayor que cero. Una mesa con pedidos asociados no se elimina: la aplicación indica que se la desactive para preservar el historial.

## Permisos

- **ADMIN:** acceso a áreas y mesas de cualquier restaurante.
- **GERENTE:** acceso a áreas y a las mesas del restaurante asociado a su usuario.
- Los demás roles no tienen permisos `personal` para áreas ni `salon` para mesas según `src/services/auth.py`.

Las funciones de servicio verifican los permisos además de ocultar las secciones no habilitadas en la interfaz. La asociación del empleado con el restaurante no se requiere para mantener mesas: se usa el restaurante vinculado al usuario.

## Archivos agregados o modificados

- `src/services/areas.py`: consultas, creación, edición, eliminación y gestión de asociaciones área-cargo.
- `src/services/tables.py`: consultas, creación, edición, activación/desactivación y eliminación de mesas.
- `app.py`: navegación, formularios, listados y confirmación de eliminaciones.
- `docs/modulos_areas_mesas_v1.md`: documentación de esta versión.

Los modelos existentes en `src/models.py` y el esquema `sql/schema.sql` ya incluían las entidades `Area`, `Cargo`, `AreaCargo` y `Mesa`, por lo que no se agregaron migraciones.

## Uso

1. Iniciar sesión con una cuenta ADMIN o GERENTE.
2. Seleccionar **Áreas** para mantener áreas y sus cargos.
3. Seleccionar **Mesas** para elegir un restaurante y operar sobre sus mesas.
4. Para asignar mesas a una cuenta GERENTE, asociar previamente esa cuenta al restaurante desde la administración de usuarios.

## Consideraciones

- La eliminación de áreas y mesas es física y requiere confirmación en la interfaz.
- Las mesas con pedidos quedan protegidas frente a eliminación; desactivarlas conserva el registro.
- La aplicación convierte los errores de validación y autorización en mensajes visibles. Las restricciones de unicidad de la base de datos también protegen frente a operaciones concurrentes.
- Esta implementación no cambia los módulos preexistentes de autenticación, restaurantes o usuarios, ni reemplaza `docs/autenticacion.md`.
