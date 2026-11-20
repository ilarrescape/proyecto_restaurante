from sqlalchemy import select

from src.models import Pedido, TipoComprobante
from src.services.auth import require_admin


def list_tipos_comprobante(session, actor_id):
    require_admin(session, actor_id)
    return list(session.scalars(select(TipoComprobante).order_by(TipoComprobante.nombre_tipo_comprobante)))


def create_tipo_comprobante(session, actor_id, nombre):
    require_admin(session, actor_id)
    nombre = nombre.strip()
    if not nombre or len(nombre) > 100:
        raise ValueError("Ingresá un tipo de comprobante de hasta 100 caracteres.")
    if session.scalar(select(TipoComprobante.id_tipo_comprobante).where(
        TipoComprobante.nombre_tipo_comprobante == nombre
    )):
        raise ValueError("Ya existe un tipo de comprobante con ese nombre.")
    tipo = TipoComprobante(nombre_tipo_comprobante=nombre)
    session.add(tipo)
    session.flush()
    return tipo


def update_tipo_comprobante(session, actor_id, tipo_id, nombre):
    require_admin(session, actor_id)
    tipo = session.get(TipoComprobante, tipo_id)
    if tipo is None:
        raise ValueError("El tipo de comprobante no existe.")
    nombre = nombre.strip()
    if not nombre or len(nombre) > 100:
        raise ValueError("Ingresá un tipo de comprobante de hasta 100 caracteres.")
    duplicate = session.scalar(select(TipoComprobante.id_tipo_comprobante).where(
        TipoComprobante.nombre_tipo_comprobante == nombre,
        TipoComprobante.id_tipo_comprobante != tipo_id,
    ))
    if duplicate:
        raise ValueError("Ya existe otro tipo de comprobante con ese nombre.")
    tipo.nombre_tipo_comprobante = nombre
    session.flush()
    return tipo


def delete_tipo_comprobante(session, actor_id, tipo_id):
    require_admin(session, actor_id)
    tipo = session.get(TipoComprobante, tipo_id)
    if tipo is None:
        raise ValueError("El tipo de comprobante no existe.")
    used = session.scalar(select(Pedido.id_pedido).where(
        Pedido.id_tipo_comprobante == tipo_id
    ).limit(1))
    if used is not None:
        raise ValueError("No se puede eliminar el tipo porque está utilizado en uno o más pedidos.")
    session.delete(tipo)
    session.flush()

