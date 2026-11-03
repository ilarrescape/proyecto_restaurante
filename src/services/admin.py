from sqlalchemy import select
from src.models import Usuario, Rol, Restaurante, Ciudad, Empleado, RestauranteCargoEmpleado
from src.services.auth import require_admin, hash_password, normalize_email


def create_restaurant(session, actor_id, cuit, razon, nombre, direccion, ciudad):
    require_admin(session, actor_id)
    if not 10000000000 <= cuit <= 99999999999:
        raise ValueError("El CUIT debe tener 11 dígitos.")
    for value, limit in [(razon, 150), (nombre, 150), (direccion, 180), (ciudad, 100)]:
        if not value.strip() or len(value.strip()) > limit:
            raise ValueError("Completá todos los campos respetando su longitud máxima.")
    city = session.scalar(select(Ciudad).where(Ciudad.nombre_ciudad == ciudad.strip()))
    if city is None:
        city = Ciudad(nombre_ciudad=ciudad.strip())
        session.add(city)
        session.flush()
    restaurant = Restaurante(cuit=cuit, razon_social=razon.strip(), nombre_fantasia=nombre.strip(),
                            direccion=direccion.strip(), id_ciudad=city.id_ciudad)
    session.add(restaurant)
    session.flush()
    return restaurant


def validate_assignment(session, role_id, restaurant_id, employee_id):
    role = session.get(Rol, role_id)
    if role is None:
        raise ValueError("El rol no existe.")
    if restaurant_id is not None and session.get(Restaurante, restaurant_id) is None:
        raise ValueError("El restaurante no existe.")
    if employee_id is not None:
        if restaurant_id is None:
            raise ValueError("Seleccioná el restaurante del empleado.")
        if session.get(Empleado, employee_id) is None:
            raise ValueError("El empleado no existe.")
        assignment = session.scalar(select(RestauranteCargoEmpleado).where(
            RestauranteCargoEmpleado.dni_empleado == employee_id,
            RestauranteCargoEmpleado.cuit_restaurante == restaurant_id))
        if assignment is None:
            raise ValueError("El empleado no está vinculado a ese restaurante.")
    if role.nombre_rol != "ADMIN" and restaurant_id is None:
        raise ValueError("Los usuarios operativos requieren un restaurante.")


def create_user(session, actor_id, email, name, password, role_id, restaurant_id=None, employee_id=None):
    require_admin(session, actor_id)
    validate_assignment(session, role_id, restaurant_id, employee_id)
    email = normalize_email(email)
    if not name.strip() or len(name.strip()) > 150:
        raise ValueError("Ingresá un nombre de hasta 150 caracteres.")
    if session.scalar(select(Usuario.id_usuario).where(Usuario.nombre_usuario == email)):
        raise ValueError("Ya existe un usuario con ese email.")
    user = Usuario(nombre_usuario=email, nombre_completo=name.strip(), password_hash=hash_password(password),
                   id_rol=role_id, cuit_restaurante=restaurant_id, dni_empleado=employee_id)
    session.add(user)
    session.flush()
    return user


def update_user(session, actor_id, user_id, role_id, restaurant_id, employee_id, active):
    require_admin(session, actor_id)
    user = session.get(Usuario, user_id)
    if user is None:
        raise ValueError("El usuario no existe.")
    validate_assignment(session, role_id, restaurant_id, employee_id)
    if user_id == actor_id and (not active or session.get(Rol, role_id).nombre_rol != "ADMIN"):
        raise ValueError("No podés desactivar tu propia cuenta ni quitarte el rol ADMIN.")
    user.id_rol, user.cuit_restaurante, user.dni_empleado, user.activo = role_id, restaurant_id, employee_id, active
    session.flush()
    session.expire(user, ["rol", "restaurante", "empleado"])
