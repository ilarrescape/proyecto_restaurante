import os
from pathlib import Path
from sqlalchemy import select
from src.models import Usuario, Rol
from src.services.auth import hash_password, normalize_email


def bootstrap(factory):
    """Carga la semilla antes de crear el ADMIN; no modifica usuarios existentes."""
    email = normalize_email(os.environ["EMAIL_SUPER"])
    password = os.environ["PASSWORD_SUPER"]
    with factory.kw["bind"].connect() as connection, factory(bind=connection) as session:
        # Serializa arranques concurrentes en MySQL. La clave única también evita duplicados.
        from sqlalchemy import text
        locked = session.scalar(text("SELECT GET_LOCK('restaurante_bootstrap', 30)"))
        if locked != 1:
            raise RuntimeError("No se pudo bloquear la inicialización.")
        try:
            seed = Path(__file__).resolve().parents[2] / "sql" / "seed.sql"
            for statement in seed.read_text().split(";"):
                if statement.strip() and not statement.strip().upper().startswith("USE "):
                    session.execute(text(statement))
            user = session.scalar(select(Usuario).where(Usuario.nombre_usuario == email))
            created = user is None
            if created:
                role = session.scalar(select(Rol).where(Rol.nombre_rol == "ADMIN"))
                session.add(Usuario(nombre_usuario=email, password_hash=hash_password(password),
                                    nombre_completo="Superusuario", id_rol=role.id_rol))
            session.commit()
            return created
        finally:
            # RELEASE_LOCK necesita ejecutarse incluso si la transacción falló.
            session.rollback()
            session.execute(text("SELECT RELEASE_LOCK('restaurante_bootstrap')"))
