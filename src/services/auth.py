from datetime import datetime
import bcrypt
from sqlalchemy import select
from src.models import Usuario, Rol

PERMISSIONS = {
    "ADMIN": {"restaurantes", "usuarios", "personal", "carta", "clientes", "salon", "pedidos", "consulta"},
    "GERENTE": {"personal", "carta", "clientes", "salon", "pedidos", "consulta"},
    "CAJERO": {"clientes", "pedidos", "consulta"},
    "MOZO": {"pedidos", "consulta"},
    "CONSULTA": {"consulta"},
}

#Clase que viene: codificación de caracteres, método cesar y hashing. (Clase 50)
def hash_password(password):
    if not password or len(password.encode("utf-8")) > 72:
        raise ValueError("La contraseña debe contener entre 1 y 72 bytes UTF-8.")
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("ascii")


# Se compara la contraseña recibida con el hash; nunca se descifra.
def verify_password(password, stored_hash):
    try:
        return bcrypt.checkpw(password.encode("utf-8"), stored_hash.encode("ascii"))
    except (ValueError, UnicodeError, AttributeError):
        return False


DUMMY_HASH = bcrypt.hashpw(b"invalid-login", bcrypt.gensalt()).decode("ascii")


def authenticate(session, email, password):
    user = session.scalar(select(Usuario).where(Usuario.nombre_usuario == email.strip().lower()))
    valid = verify_password(password, user.password_hash if user else DUMMY_HASH)
    if not user or not valid or not user.activo:
        return None
    user.ultimo_acceso = datetime.now()
    session.flush()
    return user.id_usuario


def require_admin(session, actor_id):
    actor = session.get(Usuario, actor_id)
    if not actor or not actor.activo or actor.rol.nombre_rol != "ADMIN":
        raise PermissionError("Solo un ADMIN puede realizar esta acción.")
    return actor


def has_permission(session, user_id, permission):
    user = session.get(Usuario, user_id)
    return bool(user and user.activo and permission in PERMISSIONS.get(user.rol.nombre_rol, set()))


def normalize_email(email):
    email = email.strip().lower()
    if len(email) > 80 or "@" not in email or not all(email.split("@")) or email.count("@") != 1:
        raise ValueError("Ingresá un email válido de hasta 80 caracteres.")
    return email
