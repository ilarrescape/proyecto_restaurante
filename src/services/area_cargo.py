from sqlalchemy import select

from src.models import Area, AreaCargo, Cargo
from src.services.auth import require_admin


def list_area_cargos(session, actor_id, area_id=None, cargo_id=None):
    require_admin(session, actor_id)
    if area_id is not None and session.get(Area, area_id) is None:
        raise ValueError("El área seleccionada no existe.")
    if cargo_id is not None and session.get(Cargo, cargo_id) is None:
        raise ValueError("El cargo seleccionado no existe.")

    query = select(AreaCargo).join(Area, AreaCargo.id_area == Area.id_area).join(
        Cargo, AreaCargo.id_cargo == Cargo.id_cargo
    )
    if area_id is not None:
        query = query.where(AreaCargo.id_area == area_id)
    if cargo_id is not None:
        query = query.where(AreaCargo.id_cargo == cargo_id)
    query = query.order_by(Area.nombre_area, Cargo.nombre_cargo)
    return list(session.scalars(query))


def associate_area_cargo(session, actor_id, area_id, cargo_id):
    require_admin(session, actor_id)
    if session.get(Area, area_id) is None:
        raise ValueError("El área seleccionada no existe.")
    if session.get(Cargo, cargo_id) is None:
        raise ValueError("El cargo seleccionado no existe.")
    association_key = (area_id, cargo_id)
    if session.get(AreaCargo, association_key) is not None:
        raise ValueError("Ese cargo ya está asociado al área seleccionada.")

    association = AreaCargo(id_area=area_id, id_cargo=cargo_id)
    session.add(association)
    session.flush()
    return association


def remove_area_cargo(session, actor_id, area_id, cargo_id):
    require_admin(session, actor_id)
    association = session.get(AreaCargo, (area_id, cargo_id))
    if association is None:
        raise ValueError("La asociación seleccionada no existe.")
    session.delete(association)
    session.flush()
