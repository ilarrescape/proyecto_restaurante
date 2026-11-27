from sqlalchemy import select

from src.models import Condicion, EstadoCondicion, RestauranteCargoEmpleado
from src.services.auth import require_admin


def list_condiciones(session, actor_id):
    require_admin(session, actor_id)
    return list(session.scalars(select(Condicion).order_by(Condicion.nombre_condicion)))


def get_condicion(session, actor_id, condicion_id):
    require_admin(session, actor_id)
    condicion = session.get(Condicion, condicion_id)
    if condicion is None:
        raise ValueError("La condición no existe.")
    return condicion


def create_condicion(session, actor_id, nombre, estado_id):
    require_admin(session, actor_id)
    nombre = nombre.strip()
    if not nombre or len(nombre) > 120:
        raise ValueError("Ingresá un nombre de condición de hasta 120 caracteres.")
    if session.get(EstadoCondicion, estado_id) is None:
        raise ValueError("El estado de condición seleccionado no existe.")
    if session.scalar(select(Condicion.id_condicion).where(Condicion.nombre_condicion == nombre)):
        raise ValueError("Ya existe una condición con ese nombre.")
    condicion = Condicion(nombre_condicion=nombre, id_estado_condicion=estado_id)
    session.add(condicion)
    session.flush()
    return condicion


def update_condicion(session, actor_id, condicion_id, nombre, estado_id):
    condicion = get_condicion(session, actor_id, condicion_id)
    nombre = nombre.strip()
    if not nombre or len(nombre) > 120:
        raise ValueError("Ingresá un nombre de condición de hasta 120 caracteres.")
    if session.get(EstadoCondicion, estado_id) is None:
        raise ValueError("El estado de condición seleccionado no existe.")
    duplicate = session.scalar(select(Condicion.id_condicion).where(
        Condicion.nombre_condicion == nombre,
        Condicion.id_condicion != condicion_id,
    ))
    if duplicate:
        raise ValueError("Ya existe otra condición con ese nombre.")
    condicion.nombre_condicion = nombre
    condicion.id_estado_condicion = estado_id
    session.flush()
    return condicion


def delete_condicion(session, actor_id, condicion_id):
    condicion = get_condicion(session, actor_id, condicion_id)
    asignada = session.scalar(select(RestauranteCargoEmpleado.id_condicion).where(
        RestauranteCargoEmpleado.id_condicion == condicion_id
    ).limit(1))
    if asignada is not None:
        raise ValueError("No se puede eliminar la condición porque está asignada a empleados.")
    session.delete(condicion)
    session.flush()
