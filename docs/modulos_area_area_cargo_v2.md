# Módulos Área y Área-Cargo

## Alcance

Se incorporó la gestión de áreas disponible en `rama-facu` y se agregó la gestión de asociaciones entre áreas y cargos. El módulo Área permite registrar, consultar, modificar y eliminar áreas. El módulo Área-Cargo permite asociar un cargo con un área, consultar todas las asociaciones o filtrarlas por área o cargo, y quitar una asociación.

Solo se incorporaron estos cambios. No se hizo un merge de `rama-facu` ni se copiaron sus pantallas de Mesas u otros módulos.

## Revisión de `rama-facu` y dependencias

En `rama-facu`, el módulo de áreas estaba implementado en `src/services/areas.py` y en una sección de `app.py`. El servicio usa las clases `Area`, `AreaCargo` y `Cargo`, más los controles de acceso de autenticación. La pantalla obtiene las áreas y cargos disponibles desde la base, administra áreas y reemplaza en bloque la lista de cargos asociados a un área.

En `rama-diego-belizan` ya existían las clases `Area`, `Cargo` y `AreaCargo` en `src/models.py`, y las tablas `area`, `cargo` y `area_cargo` en `sql/schema.sql`. También están las áreas y cargos iniciales en `sql/seed.sql`. Por eso no se copiaron ni modificaron modelos, esquema o semilla. Se evitó copiar el `app.py` completo de la otra rama porque incluye pantallas y cambios que no pertenecen a este alcance.

## Archivos recuperados, creados y modificados

- **Recuperado y adaptado:** `src/services/areas.py`, tomando las operaciones CRUD de área del archivo de `rama-facu`. Mantiene autorización ADMIN y elimina explícitamente las asociaciones Área-Cargo antes de borrar un área.
- **Creado:** `src/services/area_cargo.py`, con las operaciones de asociar, consultar/filtrar y quitar asociaciones.
- **Modificado:** `app.py`, incorporando las opciones **Áreas** y **Área-Cargo** al menú de Administración.
- **Creado:** `tests/test_area_cargo.py`, con pruebas para relaciones, filtros y regresión de Cargo y TipoComprobante.
- **Creado:** este documento como nueva versión de documentación. Las versiones anteriores se conservan.

## Reglas de Área-Cargo

- La asociación usa la clave compuesta existente `(id_area, id_cargo)`; intentar repetirla genera un mensaje de validación.
- Antes de crear una asociación se confirma que el área y el cargo existan.
- Los filtros de consulta también validan los identificadores recibidos.
- La eliminación requiere que exista la asociación.
- Los servicios requieren un usuario ADMIN, igual que los módulos de administración existentes.
- Las escrituras de la interfaz se ejecutan con `factory.begin()` y reutilizan la fábrica de sesiones existente.

## Cómo probar en Streamlit

1. Usar la rama `rama-diego-belizan`, configurar MySQL y contar con el esquema y un usuario ADMIN.
2. Desde la raíz del proyecto, iniciar con `streamlit run app.py`. De acuerdo con el comportamiento actual de `src/services/auth.py`, ingresar la contraseña solicitada en la terminal para que la aplicación continúe.
3. En **Áreas**, crear un área de prueba, modificar su nombre y verificar que aparezca en la lista. La eliminación pide confirmación e informa que también quitará sus asociaciones.
4. En **Área-Cargo**, seleccionar un área y un cargo y asociarlos. La relación debe aparecer en la tabla.
5. Filtrar por área, por cargo y por ambos; verificar que la lista muestre las coincidencias.
6. Intentar asociar de nuevo el mismo par; debe rechazarse como duplicado.
7. Quitar una asociación y comprobar que deja de aparecer. Si se elimina un área, se eliminan también sus asociaciones.
8. Revisar **Cargos** y **Tipos de comprobante** para confirmar que siguen disponibles.

## Verificación técnica

Las operaciones usan las claves foráneas y la clave primaria compuesta existentes. Las reglas de validación de la aplicación se complementan con las restricciones de la base de datos. Se ejecutaron seis pruebas automatizadas con SQLite; cubren autenticación/administración existentes, asociaciones y filtros Área-Cargo, y operaciones CRUD de Cargo y TipoComprobante. También pasó la compilación de los módulos modificados y `git diff --check`.

La carga visual de Streamlit no se pudo confirmar con `AppTest`: la solicitud interactiva de contraseña en `auth.py` no funciona dentro de ese entorno automatizado. Para la prueba manual, iniciar Streamlit desde una terminal y responder allí a la solicitud de contraseña. La conexión y las pantallas completas requieren una base MySQL configurada.
