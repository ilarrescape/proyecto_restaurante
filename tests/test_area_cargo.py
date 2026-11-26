import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from src.models import Base, Rol, Usuario
from src.services.area_cargo import (
    associate_area_cargo,
    list_area_cargos,
    remove_area_cargo,
)
from src.services.areas import create_area
from src.services.auth import hash_password
from src.services.cargo import create_cargo, delete_cargo, list_cargos, update_cargo
from src.services.tipo_comprobante import (
    create_tipo_comprobante,
    delete_tipo_comprobante,
    list_tipos_comprobante,
    update_tipo_comprobante,
)


@pytest.fixture
def session():
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        db.add(Rol(id_rol=1, nombre_rol="ADMIN"))
        db.flush()
        db.add(Usuario(
            id_usuario=1,
            nombre_usuario="admin@example.com",
            password_hash=hash_password("clave"),
            nombre_completo="Admin",
            id_rol=1,
        ))
        db.commit()
        yield db


def test_area_cargo_associate_filter_and_remove(session):
    area = create_area(session, 1, "Cocina")
    other_area = create_area(session, 1, "Salón")
    cargo = create_cargo(session, 1, "Cocinero")
    other_cargo = create_cargo(session, 1, "Ayudante")

    associate_area_cargo(session, 1, area.id_area, cargo.id_cargo)
    associate_area_cargo(session, 1, other_area.id_area, other_cargo.id_cargo)

    assert len(list_area_cargos(session, 1)) == 2
    assert [row.id_cargo for row in list_area_cargos(session, 1, area.id_area)] == [cargo.id_cargo]
    assert [row.id_area for row in list_area_cargos(session, 1, cargo_id=other_cargo.id_cargo)] == [other_area.id_area]
    assert [row.id_area for row in list_area_cargos(session, 1, area.id_area, cargo.id_cargo)] == [area.id_area]

    with pytest.raises(ValueError, match="ya está asociado"):
        associate_area_cargo(session, 1, area.id_area, cargo.id_cargo)
    with pytest.raises(ValueError, match="área seleccionada no existe"):
        associate_area_cargo(session, 1, 999, cargo.id_cargo)
    with pytest.raises(ValueError, match="cargo seleccionado no existe"):
        associate_area_cargo(session, 1, area.id_area, 999)

    remove_area_cargo(session, 1, area.id_area, cargo.id_cargo)
    assert list_area_cargos(session, 1, area.id_area) == []


def test_cargo_and_tipo_comprobante_crud_regression(session):
    cargo = create_cargo(session, 1, "Recepcionista")
    assert [row.nombre_cargo for row in list_cargos(session, 1)] == ["Recepcionista"]
    update_cargo(session, 1, cargo.id_cargo, "Encargado")
    assert list_cargos(session, 1)[0].nombre_cargo == "Encargado"
    delete_cargo(session, 1, cargo.id_cargo)
    assert list_cargos(session, 1) == []

    tipo = create_tipo_comprobante(session, 1, "Comprobante de prueba")
    assert [row.nombre_tipo_comprobante for row in list_tipos_comprobante(session, 1)] == [
        "Comprobante de prueba"
    ]
    update_tipo_comprobante(session, 1, tipo.id_tipo_comprobante, "Comprobante editado")
    assert list_tipos_comprobante(session, 1)[0].nombre_tipo_comprobante == "Comprobante editado"
    delete_tipo_comprobante(session, 1, tipo.id_tipo_comprobante)
    assert list_tipos_comprobante(session, 1) == []
