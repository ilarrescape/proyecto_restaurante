from sqlalchemy import select

from src.models import Area, AreaCargo
from src.services.auth import require_admin


def list_areas(session, actor_id):
    require_admin(session, actor_id)
    return list(session.scalars(select(Area).order_by(Area.nombre_area)))


def get_area(session, actor_id, area_id):
    require_admin(session, actor_id)
    area = session.get(Area, area_id)
    if area is None:
        raise ValueError("El área no existe.")
    return area


def create_area(session, actor_id, name):
    require_admin(session, actor_id)
    name = name.strip()
    if not name or len(name) > 100:
        raise ValueError("El nombre del área es obligatorio y admite hasta 100 caracteres.")
    if session.scalar(select(Area.id_area).where(Area.nombre_area == name)):
        raise ValueError("Ya existe un área con ese nombre.")
    area = Area(nombre_area=name)
    session.add(area)
    session.flush()
    return area


def update_area(session, actor_id, area_id, name):
    area = get_area(session, actor_id, area_id)
    name = name.strip()
    if not name or len(name) > 100:
        raise ValueError("El nombre del área es obligatorio y admite hasta 100 caracteres.")
    duplicate = session.scalar(select(Area.id_area).where(
        Area.nombre_area == name, Area.id_area != area_id
    ))
    if duplicate:
        raise ValueError("Ya existe un área con ese nombre.")
    area.nombre_area = name
    session.flush()
    return area


def delete_area(session, actor_id, area_id):
    area = get_area(session, actor_id, area_id)
    session.execute(AreaCargo.__table__.delete().where(AreaCargo.id_area == area_id))
    session.delete(area)
    session.flush()
