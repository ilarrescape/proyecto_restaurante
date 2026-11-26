from decimal import Decimal, InvalidOperation

from sqlalchemy import select

from src.models import Mesa, Pedido, Restaurante
from src.services.auth import has_permission


def _restaurant_for_user(session, actor_id, restaurant_id):
    if not has_permission(session, actor_id, "salon"):
        raise PermissionError("No tenés permisos para administrar mesas.")
    restaurant = session.get(Restaurante, restaurant_id)
    if restaurant is None:
        raise ValueError("El restaurante no existe.")
    from src.models import Usuario
    user = session.get(Usuario, actor_id)
    if user.rol.nombre_rol != "ADMIN" and user.cuit_restaurante != restaurant_id:
        raise PermissionError("Solo podés administrar mesas de tu restaurante.")
    return restaurant


def list_tables(session, actor_id, restaurant_id, include_inactive=True):
    _restaurant_for_user(session, actor_id, restaurant_id)
    query = select(Mesa).where(Mesa.cuit_restaurante == restaurant_id)
    if not include_inactive:
        query = query.where(Mesa.activa.is_(True))
    return list(session.scalars(query.order_by(Mesa.numero_referencia)))


def create_table(session, actor_id, restaurant_id, reference, seats=2, x=None, y=None, description=None):
    _restaurant_for_user(session, actor_id, restaurant_id)
    reference = reference.strip()
    if not reference or len(reference) > 30:
        raise ValueError("La referencia es obligatoria y admite hasta 30 caracteres.")
    if isinstance(seats, bool) or int(seats) < 1:
        raise ValueError("La cantidad de sillas debe ser mayor que cero.")
    if session.scalar(select(Mesa.id_mesa).where(
        Mesa.cuit_restaurante == restaurant_id, Mesa.numero_referencia == reference
    )):
        raise ValueError("Ya existe una mesa con esa referencia en el restaurante.")
    try:
        x = Decimal(str(x)) if x not in (None, "") else None
        y = Decimal(str(y)) if y not in (None, "") else None
    except InvalidOperation as exc:
        raise ValueError("Las coordenadas deben ser números válidos.") from exc
    mesa = Mesa(numero_referencia=reference, cantidad_sillas=int(seats), ubicacion_x=x,
                ubicacion_y=y, descripcion=(description or "").strip() or None,
                cuit_restaurante=restaurant_id, activa=True)
    session.add(mesa)
    session.flush()
    return mesa


def update_table(session, actor_id, table_id, reference, seats, x=None, y=None, description=None):
    mesa = session.get(Mesa, table_id)
    if mesa is None:
        raise ValueError("La mesa no existe.")
    _restaurant_for_user(session, actor_id, mesa.cuit_restaurante)
    reference = reference.strip()
    if not reference or len(reference) > 30:
        raise ValueError("La referencia es obligatoria y admite hasta 30 caracteres.")
    if isinstance(seats, bool) or int(seats) < 1:
        raise ValueError("La cantidad de sillas debe ser mayor que cero.")
    duplicate = session.scalar(select(Mesa.id_mesa).where(
        Mesa.cuit_restaurante == mesa.cuit_restaurante,
        Mesa.numero_referencia == reference, Mesa.id_mesa != table_id
    ))
    if duplicate:
        raise ValueError("Ya existe una mesa con esa referencia en el restaurante.")
    try:
        mesa.ubicacion_x = Decimal(str(x)) if x not in (None, "") else None
        mesa.ubicacion_y = Decimal(str(y)) if y not in (None, "") else None
    except InvalidOperation as exc:
        raise ValueError("Las coordenadas deben ser números válidos.") from exc
    mesa.numero_referencia, mesa.cantidad_sillas = reference, int(seats)
    mesa.descripcion = (description or "").strip() or None
    session.flush()
    return mesa


def set_table_active(session, actor_id, table_id, active):
    mesa = session.get(Mesa, table_id)
    if mesa is None:
        raise ValueError("La mesa no existe.")
    _restaurant_for_user(session, actor_id, mesa.cuit_restaurante)
    mesa.activa = bool(active)
    session.flush()
    return mesa


def delete_table(session, actor_id, table_id):
    mesa = session.get(Mesa, table_id)
    if mesa is None:
        raise ValueError("La mesa no existe.")
    _restaurant_for_user(session, actor_id, mesa.cuit_restaurante)
    if session.scalar(select(Pedido.id_pedido).where(Pedido.id_mesa == table_id).limit(1)):
        raise ValueError("No se puede eliminar una mesa con pedidos asociados; desactivala en su lugar.")
    session.delete(mesa)
    session.flush()
