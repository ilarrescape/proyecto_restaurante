
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.models import RestauranteCargoEmpleado


def crear_asignacion(
    db: Session,
    id_cargo: int,
    id_condicion: int,
    cuit_restaurante: int,
    dni_empleado: int
):
    nueva_asignacion = RestauranteCargoEmpleado(
        id_cargo=id_cargo,
        id_condicion=id_condicion,
        cuit_restaurante=cuit_restaurante,
        dni_empleado=dni_empleado
    )

    try:
        db.add(nueva_asignacion)
        db.commit()
        db.refresh(nueva_asignacion)

        return nueva_asignacion

    except IntegrityError as error:
        db.rollback()
        raise error


def listar_asignaciones(db: Session):
    return db.query(RestauranteCargoEmpleado).all()


def buscar_asignacion(
    db: Session,
    id_cargo: int,
    id_condicion: int,
    cuit_restaurante: int,
    dni_empleado: int
):
    return db.query(RestauranteCargoEmpleado).filter_by(
        id_cargo=id_cargo,
        id_condicion=id_condicion,
        cuit_restaurante=cuit_restaurante,
        dni_empleado=dni_empleado
    ).first()


def modificar_asignacion(
    db: Session,
    id_cargo: int,
    id_condicion: int,
    cuit_restaurante: int,
    dni_empleado: int,
    nuevo_id_cargo: int,
    nuevo_id_condicion: int,
    nuevo_cuit_restaurante: int,
    nuevo_dni_empleado: int
):
    asignacion = buscar_asignacion(
        db,
        id_cargo,
        id_condicion,
        cuit_restaurante,
        dni_empleado
    )

    if asignacion is None:
        return None

    try:
        asignacion.id_cargo = nuevo_id_cargo
        asignacion.id_condicion = nuevo_id_condicion
        asignacion.cuit_restaurante = nuevo_cuit_restaurante
        asignacion.dni_empleado = nuevo_dni_empleado

        db.commit()
        db.refresh(asignacion)

        return asignacion

    except IntegrityError:
        db.rollback()
        return None


def eliminar_asignacion(
    db: Session,
    id_cargo: int,
    id_condicion: int,
    cuit_restaurante: int,
    dni_empleado: int
):
    asignacion = buscar_asignacion(
        db,
        id_cargo,
        id_condicion,
        cuit_restaurante,
        dni_empleado
    )

    if asignacion is None:
        return False

    try:
        db.delete(asignacion)
        db.commit()

        return True

    except IntegrityError:
        db.rollback()
        return False
