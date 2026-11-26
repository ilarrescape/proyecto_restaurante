from sqlalchemy import select

from src.models import Cargo, RestauranteCargoEmpleado
from src.services.auth import require_admin


def list_cargos(session, actor_id):
    require_admin(session, actor_id)
    return list(session.scalars(select(Cargo).order_by(Cargo.nombre_cargo)))


def create_cargo(session, actor_id, nombre):
    require_admin(session, actor_id)
    nombre = nombre.strip()
    if not nombre or len(nombre) > 100:
        raise ValueError("Ingresá un nombre de cargo de hasta 100 caracteres.")
    if session.scalar(select(Cargo.id_cargo).where(Cargo.nombre_cargo == nombre)):
        raise ValueError("Ya existe un cargo con ese nombre.")
    cargo = Cargo(nombre_cargo=nombre)
    session.add(cargo)
    session.flush()
    return cargo


def update_cargo(session, actor_id, cargo_id, nombre):
    require_admin(session, actor_id)
    cargo = session.get(Cargo, cargo_id)
    if cargo is None:
        raise ValueError("El cargo no existe.")
    nombre = nombre.strip()
    if not nombre or len(nombre) > 100:
        raise ValueError("Ingresá un nombre de cargo de hasta 100 caracteres.")
    duplicate = session.scalar(select(Cargo.id_cargo).where(
        Cargo.nombre_cargo == nombre, Cargo.id_cargo != cargo_id
    ))
    if duplicate:
        raise ValueError("Ya existe otro cargo con ese nombre.")
    cargo.nombre_cargo = nombre
    session.flush()
    return cargo


def delete_cargo(session, actor_id, cargo_id):
    require_admin(session, actor_id)
    cargo = session.get(Cargo, cargo_id)
    if cargo is None:
        raise ValueError("El cargo no existe.")
    assigned = session.scalar(select(RestauranteCargoEmpleado.id_cargo).where(
        RestauranteCargoEmpleado.id_cargo == cargo_id
    ).limit(1))
    if assigned is not None:
        raise ValueError("No se puede eliminar el cargo porque está asignado a uno o más empleados.")
    session.delete(cargo)
    session.flush()

