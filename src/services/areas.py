from sqlalchemy import select

from src.models import Area, AreaCargo, Cargo
from src.services.auth import has_permission


def _require_area_access(session, actor_id):
    if not has_permission(session, actor_id, "personal"):
        raise PermissionError("No tenés permisos para administrar áreas y cargos.")


def list_areas(session, actor_id):
    _require_area_access(session, actor_id)
    return list(session.scalars(select(Area).order_by(Area.nombre_area)))


def get_area(session, actor_id, area_id):
    _require_area_access(session, actor_id)
    area = session.get(Area, area_id)
    if area is None:
        raise ValueError("El área no existe.")
    return area


def create_area(session, actor_id, name):
    _require_area_access(session, actor_id)
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


def list_area_cargos(session, actor_id, area_id):
    area = get_area(session, actor_id, area_id)
    return list(session.scalars(
        select(Cargo).join(AreaCargo, AreaCargo.id_cargo == Cargo.id_cargo)
        .where(AreaCargo.id_area == area.id_area).order_by(Cargo.nombre_cargo)
    ))


def set_area_cargos(session, actor_id, area_id, cargo_ids):
    area = get_area(session, actor_id, area_id)
    ids = set(cargo_ids)
    cargos = list(session.scalars(select(Cargo).where(Cargo.id_cargo.in_(ids)))) if ids else []
    if len(cargos) != len(ids):
        raise ValueError("Uno o más cargos seleccionados no existen.")
    session.execute(AreaCargo.__table__.delete().where(AreaCargo.id_area == area.id_area))
    session.add_all(AreaCargo(id_area=area.id_area, id_cargo=cargo.id_cargo) for cargo in cargos)
    session.flush()
    return cargos
