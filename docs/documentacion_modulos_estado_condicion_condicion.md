# Módulos Estado de condición y Condición

## Alcance

Esta versión documenta la administración de los catálogos `estado_condicion` y `condicion` incorporada a la aplicación Streamlit. Se reutilizan las clases `EstadoCondicion` y `Condicion` existentes en `src/models.py`; no se crean ni duplican modelos ni tablas.

## Relación entre entidades

- Un estado de condición puede tener varias condiciones.
- Cada condición requiere un `id_estado_condicion` que refiera a un estado existente.
- `restaurante_cargo_empleado.id_condicion` puede referenciar una condición asignada a un empleado.
- No se permite eliminar un estado con condiciones dependientes ni una condición que esté asignada. Esto acompaña las restricciones de claves foráneas definidas en el esquema.

## Servicios

Los archivos `src/services/estado_condicion.py` y `src/services/condicion.py` implementan operaciones de listado, búsqueda por ID, creación, modificación y eliminación. Las operaciones verifican que el usuario actor tenga rol `ADMIN`, como los servicios administrativos existentes.

Las validaciones respetan los tamaños de columna y los nombres únicos del esquema. Al crear o modificar una condición se valida el estado asociado. Los servicios hacen `flush`; la interfaz confirma los cambios con `commit`.

## Interfaz Streamlit

En el selector **Módulo** de la barra lateral se agregaron **Estados de condición** y **Condiciones**, además de **Gestión actual** para acceder a la interfaz previa. Cada nuevo módulo tiene pestañas para crear, consultar, modificar y eliminar registros.

Para operar estos catálogos, la interfaz solicita el ID de un usuario ADMIN. La validación efectiva se realiza en los servicios contra la base de datos. La interfaz de condiciones permite seleccionar un estado existente y muestra tanto su ID como su nombre en las consultas.

## Archivos involucrados

- `src/services/estado_condicion.py`
- `src/services/condicion.py`
- `src/ui/app.py`
- `src/models.py` (modelos ya existentes, sin cambios)
- `sql/schema.sql` (relaciones existentes, sin cambios)
