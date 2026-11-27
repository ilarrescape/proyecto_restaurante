from sqlalchemy import select

from src.models import Condicion, EstadoCondicion
from src.services.auth import require_admin


def list_estados_condicion(session, actor_id):
    require_admin(session, actor_id)
    return list(session.scalars(select(EstadoCondicion).order_by(EstadoCondicion.nombre_estado_condicion)))


def get_estado_condicion(session, actor_id, estado_id):
    require_admin(session, actor_id)
    estado = session.get(EstadoCondicion, estado_id)
    if estado is None:
        raise ValueError("El estado de condición no existe.")
    return estado


def create_estado_condicion(session, actor_id, nombre, empresa_de_capacitacion=None):
    require_admin(session, actor_id)
    nombre = nombre.strip()
    empresa_de_capacitacion = (empresa_de_capacitacion or "").strip() or None
    if not nombre or len(nombre) > 100:
        raise ValueError("Ingresá un nombre de estado de hasta 100 caracteres.")
    if empresa_de_capacitacion and len(empresa_de_capacitacion) > 150:
        raise ValueError("La empresa de capacitación admite hasta 150 caracteres.")
    if session.scalar(select(EstadoCondicion.id_estado_condicion).where(
        EstadoCondicion.nombre_estado_condicion == nombre
    )):
        raise ValueError("Ya existe un estado de condición con ese nombre.")
    estado = EstadoCondicion(
        nombre_estado_condicion=nombre,
        empresa_de_capacitacion=empresa_de_capacitacion,
    )
    session.add(estado)
    session.flush()
    return estado


def update_estado_condicion(session, actor_id, estado_id, nombre, empresa_de_capacitacion=None):
    estado = get_estado_condicion(session, actor_id, estado_id)
    nombre = nombre.strip()
    empresa_de_capacitacion = (empresa_de_capacitacion or "").strip() or None
    if not nombre or len(nombre) > 100:
        raise ValueError("Ingresá un nombre de estado de hasta 100 caracteres.")
    if empresa_de_capacitacion and len(empresa_de_capacitacion) > 150:
        raise ValueError("La empresa de capacitación admite hasta 150 caracteres.")
    duplicate = session.scalar(select(EstadoCondicion.id_estado_condicion).where(
        EstadoCondicion.nombre_estado_condicion == nombre,
        EstadoCondicion.id_estado_condicion != estado_id,
    ))
    if duplicate:
        raise ValueError("Ya existe otro estado de condición con ese nombre.")
    estado.nombre_estado_condicion = nombre
    estado.empresa_de_capacitacion = empresa_de_capacitacion
    session.flush()
    return estado


def delete_estado_condicion(session, actor_id, estado_id):
    estado = get_estado_condicion(session, actor_id, estado_id)
    relacionado = session.scalar(select(Condicion.id_condicion).where(
        Condicion.id_estado_condicion == estado_id
    ).limit(1))
    if relacionado is not None:
        raise ValueError("No se puede eliminar el estado porque tiene condiciones asociadas.")
    session.delete(estado)
    session.flush()
