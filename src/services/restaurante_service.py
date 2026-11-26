
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.models import Restaurante


def crear_restaurante(
    db: Session,
    cuit: int,
    razon_social: str,
    nombre_fantasia: str,
    direccion: str,
    id_ciudad: int
):
    nuevo_restaurante = Restaurante(
        cuit=cuit,
        razon_social=razon_social,
        nombre_fantasia=nombre_fantasia,
        direccion=direccion,
        id_ciudad=id_ciudad
    )

    try:
        db.add(nuevo_restaurante)
        db.commit()
        db.refresh(nuevo_restaurante)

        return nuevo_restaurante

    except IntegrityError:
        db.rollback()
        return None


def listar_restaurantes(db: Session):
    return db.query(Restaurante).all()


def buscar_restaurante(db: Session, cuit: int):
    return db.query(Restaurante).filter_by(cuit=cuit).first()


def modificar_restaurante(
    db: Session,
    cuit: int,
    razon_social: str,
    nombre_fantasia: str,
    direccion: str,
    id_ciudad: int
):
    restaurante = buscar_restaurante(db, cuit)

    if restaurante is None:
        return None

    restaurante.razon_social = razon_social
    restaurante.nombre_fantasia = nombre_fantasia
    restaurante.direccion = direccion
    restaurante.id_ciudad = id_ciudad

    try:
        db.commit()
        db.refresh(restaurante)

        return restaurante

    except IntegrityError:
        db.rollback()
        return None


def eliminar_restaurante(db: Session, cuit: int):
    restaurante = buscar_restaurante(db, cuit)

    if restaurante is None:
        return False

    try:
        db.delete(restaurante)
        db.commit()

        return True

    except IntegrityError:
        db.rollback()
        return False
