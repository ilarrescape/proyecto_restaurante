# Módulo de gestión de restaurantes

## De qué trata este módulo?

Este módulo forma parte del proyecto de gestión de restaurantes, Su objetivo es poder administrar los restaurantes y manejar las asignaciones de los empleados dentro de cada uno

Para desarrollarlo se utilizaron Python, SQLAlchemy, MySQL y Streamlit

## Modelos utilizados

Para el funcionamiento del módulo se utilizan las siguientes clases:

- **Ciudad:** guarda los datos de las ciudades donde están ubicados los restaurantes
- **Restaurante:** contiene información como el CUIT, la razón social, el nombre de fantasía, la dirección y la ciudad
- **Empleado:** almacena los datos de los empleados, como DNI, nombre, apellido y fecha de nacimiento
- **Cargo:** representa los distintos cargos que puede tener un empleado
- **EstadoCondicion:** permite identificar los diferentes estados de las condiciones
- **Condicion:** guarda las condiciones que pueden tener los empleados
- **RestauranteCargoEmpleado:** relaciona a un restaurante con un empleado, un cargo y una condición

Además, el proyecto cuenta con las clases `Rol` y `Usuario`, que pertenecen al sistema de autenticación

## Operaciones que se pueden realizar

### Restaurantes

Desde el módulo se pueden realizar las siguientes operaciones:

- Agregar un restaurante
- Ver los restaurantes registrados
- Modificar los datos de un restaurante
- Eliminar un restaurante
### Asignaciones

También se pueden administrar las asignaciones de empleados:

- Crear una asignación
- Consultar las asignaciones existentes
- Modificar una asignación
- Eliminar una asignación

Estas operaciones permiten relacionar a los empleados con los restaurantes, sus cargos y sus condiciones

## Archivos del módulo

Los archivos principales que se desarrollaron son:

- `src/models.py`: contiene las clases del proyecto y las relaciones entre ellas
- `src/services/database.py`: se encarga de configurar la conexión con la base de datos
- `src/services/restaurante_service.py`: contiene las funciones para administrar los restaurantes
- `src/services/restaurante_cargo_empleado_service.py`: contiene las funciones para administrar las asignaciones
- `src/ui/app.py`: contiene la interfaz del módulo, desarrollada con Streamlit

## Conexión con la base de datos

Para conectarse a MySQL se utiliza SQLAlchemy

Los datos de conexión se obtienen desde las variables de entorno configuradas en el archivo `.env`, como el usuario, la contraseña, el host, el puerto y el nombre de la base de datos

El archivo `.env` contiene información privada, por eso no debe subirse al repositorio de GitHub

## Tecnologías utilizadas

- Python
- MySQL
- SQLAlchemy
- Streamlit
- Pandas
- Plotly

## Pruebas realizadas

Una vez terminado el desarrollo, se realizaron distintas pruebas para comprobar que el módulo funcionara correctamente

Se verificó que:

- Los modelos se importaran correctamente
- Las relaciones entre las clases estuvieran configuradas
- Los servicios pudieran importarse sin errores
- La aplicación de Streamlit pudiera ejecutarse

Finalmente, se comprobó que la interfaz funcionara correctamente

## Integración con el proyecto

El módulo se integró al repositorio grupal y se publicó en la rama `rama-santiago`

De esta manera, los cambios quedan separados de la rama principal (`main`) y pueden revisarse antes de incorporarse al proyecto general
