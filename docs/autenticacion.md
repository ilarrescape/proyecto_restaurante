# Login y administración de usuarios

La aplicación usa Streamlit, SQLAlchemy y MySQL. El email se guarda en la columna existente `usuario.nombre_usuario`, normalizado a minúsculas. No hay registro público. ADMIN tiene todos los permisos definidos por la aplicación, incluida la creación de restaurantes y la administración de usuarios. No es un usuario administrador de MySQL.

## Instalación e inicialización

1. Crear un entorno virtual e instalar las dependencias con `pip install -r requirements.txt`.
2. Configurar `.env` con `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_POOL_SIZE`, `DB_MAX_OVERFLOW`, `EMAIL_SUPER` y `PASSWORD_SUPER`. `.env.example` contiene los nombres y ejemplos. No publicar `.env`.
3. Ejecutar `sql/schema.sql` con una cuenta de MySQL que pueda crear la base y las tablas. El archivo utiliza el nombre `restaurante_gestion`; si se cambia `DB_NAME`, adaptar ese nombre en el SQL. Para una instalación existente se conservan las tablas; este cambio no requiere columnas nuevas.
4. Crear la cuenta de conexión siguiendo `sql/create_app_user.sql`, reemplazando su contraseña por la configurada en `.env`. Esta cuenta necesita SELECT, INSERT, UPDATE y DELETE; el script de inicialización no crea tablas.
5. Desde la raíz ejecutar `python -m scripts.bootstrap`.
6. Iniciar la interfaz con `streamlit run app.py` e ingresar con `EMAIL_SUPER` y `PASSWORD_SUPER`.

El paso 5 ejecuta primero `sql/seed.sql` mediante la conexión configurada. Los catálogos usan `INSERT IGNORE` y claves únicas, por lo que se agregan los valores ausentes sin duplicar los existentes. Luego consulta el email en la tabla `usuario`: si no existe crea un usuario activo con rol ADMIN y contraseña bcrypt. Si existe conserva su contraseña, rol y estado. Cambiar PASSWORD_SUPER no restablece una contraseña existente. Cambiar EMAIL_SUPER identifica otra cuenta y puede crear otro administrador.

Un bloqueo de MySQL serializa inicializaciones concurrentes y se libera al finalizar; la semilla y la creación se confirman en una sola transacción. Los errores revierten esa transacción. El bootstrap es un comando explícito: la interfaz no necesita leer las credenciales del superusuario ni ejecutar la semilla en cada sesión.

## Login y sesión

Se consulta el email y se verifica la contraseña contra `password_hash` con `bcrypt.checkpw`. El hash no se descifra. Las cuentas inactivas no pueden ingresar; el mensaje de error es común para usuario ausente, contraseña incorrecta o cuenta inactiva. Se registra `ultimo_acceso` al autenticar.

La sesión de Streamlit guarda el identificador del usuario y la última actividad. Cada ejecución vuelve a consultar la cuenta y su rol. Cerrar sesión elimina el estado; `SESSION_TIMEOUT_MINUTES` define la inactividad permitida (120 minutos por defecto), verificada en la siguiente interacción. No hay sesión persistente entre navegadores. Las contraseñas admiten hasta 72 bytes UTF-8 por el límite de bcrypt; se rechazan las vacías o superiores a ese límite.

## Administración

Tras ingresar, ADMIN puede crear restaurantes con ciudad, CUIT, razón social, nombre y dirección. Después puede crear usuarios y modificar su rol, restaurante, empleado asociado y estado activo. Los empleados seleccionados deben existir y estar vinculados al restaurante en `restaurante_cargo_empleado`. La carga de empleados y sus cargos sigue fuera del alcance de esta interfaz.

Los usuarios operativos requieren restaurante; ADMIN puede tener alcance global sin restaurante. No se permite que un administrador se desactive o se quite su propio rol ADMIN. Los servicios verifican la autorización independientemente de la interfaz y las operaciones se ejecutan en transacciones.

| Rol | Permisos definidos |
| --- | --- |
| ADMIN | Restaurantes, usuarios, personal, carta, clientes, salón, pedidos y consulta |
| GERENTE | Personal, carta, clientes, salón, pedidos y consulta |
| CAJERO | Clientes, pedidos y consulta |
| MOZO | Pedidos y consulta |
| CONSULTA | Consulta |

Los permisos son conjuntos fijos definidos en `src/services/auth.py`; ADMIN los asigna mediante el rol. No hay edición individual de permisos ni tablas adicionales para ello. `has_permission` está disponible para futuros módulos, que deberán validar además el restaurante del usuario en sus consultas. Los módulos operativos todavía no están implementados.

## Archivos y validación

- `src/database.py`: conexión y fábrica de sesiones.
- `src/services/bootstrap.py` y `scripts/bootstrap.py`: semilla y administrador inicial.
- `src/services/auth.py`: bcrypt, login y permisos.
- `src/services/admin.py`: operaciones administrativas con autorización.
- `app.py`: formularios y sesión.
- `tests/test_auth.py`: pruebas con SQLite para bcrypt, login, cuentas inactivas, creación de usuarios y restricciones de ADMIN. Ejecutar `python -m pytest -q`.

Las pruebas de servicios no sustituyen la verificación de integración del bootstrap con MySQL. Para comprobar su idempotencia, ejecutarlo dos veces en una base de prueba y verificar que solo exista una cuenta para EMAIL_SUPER y que el hash se conserve en la segunda ejecución. En producción, servir la interfaz mediante HTTPS. No se implementan recuperación de contraseña, MFA ni limitación persistente de intentos de login.

### Validación realizada

Se ejecutaron cuatro pruebas automatizadas correctamente y se verificó la carga del formulario de login con `streamlit.testing.v1.AppTest`. La prueba del bootstrap adapta las sentencias MySQL a SQLite para comprobar la semilla, la creación única y la conservación del hash; no valida el bloqueo en un servidor MySQL. También pasaron la compilación de los archivos Python y `git diff --check`. No se ejecutó la inicialización contra la base configurada en `.env`.
