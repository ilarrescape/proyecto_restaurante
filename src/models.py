
from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    String,
    CheckConstraint,
    Index,
    UniqueConstraint,
    Integer,
)
from sqlalchemy.dialects.mysql import INTEGER, BIGINT
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship
)


class Base(DeclarativeBase):
    pass

# Modelos de la tabla de usuarios y roles

class Rol(Base):
    __tablename__ = "rol"

    id_rol: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    nombre_rol: Mapped[str] = mapped_column(
        String(40),
        unique=True,
        nullable=False
    )

    descripcion: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True
    )

    usuarios: Mapped[list["Usuario"]] = relationship(
        back_populates="rol"
    )


class Usuario(Base):
    __tablename__ = "usuario"

    id_usuario: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    nombre_usuario: Mapped[str] = mapped_column(
        String(80),
        unique=True,
        nullable=False
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    nombre_completo: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    activo: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    id_rol: Mapped[int] = mapped_column(
        ForeignKey("rol.id_rol"),
        nullable=False
    )

    dni_empleado: Mapped[Optional[int]] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("empleado.dni"),
        unique=True,
        nullable=True
    )

    cuit_restaurante: Mapped[Optional[int]] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("restaurante.cuit"),
        nullable=True
    )

    creado_en: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        nullable=False
    )

    ultimo_acceso: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True
    )

    rol: Mapped["Rol"] = relationship(
        back_populates="usuarios"
    )

    empleado: Mapped[Optional["Empleado"]] = relationship()

    restaurante: Mapped[Optional["Restaurante"]] = relationship()



# modelos de mis modulos aña


class Ciudad(Base):
    __tablename__ = "ciudad"

    __table_args__ = (
        UniqueConstraint(
            "nombre_ciudad",
            name="uq_ciudad_nombre"
        ),
    )

    id_ciudad: Mapped[int] = mapped_column(
        INTEGER(unsigned=True),
        primary_key=True,
        autoincrement=True
    )

    nombre_ciudad: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    restaurantes: Mapped[list["Restaurante"]] = relationship(
        back_populates="ciudad"
    )


class Cargo(Base):
    __tablename__ = "cargo"

    __table_args__ = (
        UniqueConstraint(
            "nombre_cargo",
            name="uq_cargo_nombre"
        ),
    )

    id_cargo: Mapped[int] = mapped_column(
        INTEGER(unsigned=True),
        primary_key=True,
        autoincrement=True
    )

    nombre_cargo: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    asignaciones: Mapped[list["RestauranteCargoEmpleado"]] = relationship(
        back_populates="cargo"
    )


class EstadoCondicion(Base):
    __tablename__ = "estado_condicion"

    __table_args__ = (
        UniqueConstraint(
            "nombre_estado_condicion",
            name="uq_estado_condicion_nombre"
        ),
    )

    id_estado_condicion: Mapped[int] = mapped_column(
        INTEGER(unsigned=True),
        primary_key=True,
        autoincrement=True
    )

    nombre_estado_condicion: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    empresa_de_capacitacion: Mapped[Optional[str]] = mapped_column(
        String(150),
        nullable=True
    )

    condiciones: Mapped[list["Condicion"]] = relationship(
        back_populates="estado"
    )


class Restaurante(Base):
    __tablename__ = "restaurante"

    __table_args__ = (
        CheckConstraint(
            "cuit BETWEEN 10000000000 AND 99999999999",
            name="chk_restaurante_cuit"
        ),
        Index("idx_restaurante_ciudad", "id_ciudad"),
        Index("idx_restaurante_nombre", "nombre_fantasia")
    )

    cuit: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        primary_key=True
    )

    razon_social: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    nombre_fantasia: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    direccion: Mapped[str] = mapped_column(
        String(180),
        nullable=False
    )

    id_ciudad: Mapped[int] = mapped_column(
        INTEGER(unsigned=True),
        ForeignKey(
            "ciudad.id_ciudad",
            name="fk_restaurante_ciudad",
            onupdate="CASCADE",
            ondelete="RESTRICT"
        ),
        nullable=False
    )

    ciudad: Mapped["Ciudad"] = relationship(
        back_populates="restaurantes"
    )

    asignaciones: Mapped[list["RestauranteCargoEmpleado"]] = relationship(
        back_populates="restaurante"
    )


class RestauranteCargoEmpleado(Base):
    __tablename__ = "restaurante_cargo_empleado"

    __table_args__ = (
        Index("idx_rce_restaurante", "cuit_restaurante"),
        Index("idx_rce_empleado", "dni_empleado")
    )

    id_cargo: Mapped[int] = mapped_column(
        INTEGER(unsigned=True),
        ForeignKey(
            "cargo.id_cargo",
            name="fk_rce_cargo",
            onupdate="CASCADE",
            ondelete="RESTRICT"
        ),
        primary_key=True
    )

    id_condicion: Mapped[int] = mapped_column(
        INTEGER(unsigned=True),
        ForeignKey(
            "condicion.id_condicion",
            name="fk_rce_condicion",
            onupdate="CASCADE",
            ondelete="RESTRICT"
        ),
        primary_key=True
    )

    cuit_restaurante: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey(
            "restaurante.cuit",
            name="fk_rce_restaurante",
            onupdate="CASCADE",
            ondelete="CASCADE"
        ),
        primary_key=True
    )

    dni_empleado: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey(
            "empleado.dni",
            name="fk_rce_empleado",
            onupdate="CASCADE",
            ondelete="CASCADE"
        ),
        primary_key=True
    )

    cargo: Mapped["Cargo"] = relationship(
        back_populates="asignaciones"
    )

    condicion: Mapped["Condicion"] = relationship(
        back_populates="asignaciones"
    )

    restaurante: Mapped["Restaurante"] = relationship(
        back_populates="asignaciones"
    )

    empleado: Mapped["Empleado"] = relationship(
        back_populates="asignaciones"
    )


class Condicion(Base):
    __tablename__ = "condicion"

    __table_args__ = (
        UniqueConstraint(
            "nombre_condicion",
            name="uq_condicion_nombre"
        ),
    )

    id_condicion: Mapped[int] = mapped_column(
        INTEGER(unsigned=True),
        primary_key=True,
        autoincrement=True
    )

    nombre_condicion: Mapped[str] = mapped_column(
        String(120),
        nullable=False
    )

    id_estado_condicion: Mapped[int] = mapped_column(
        INTEGER(unsigned=True),
        ForeignKey(
            "estado_condicion.id_estado_condicion",
            name="fk_condicion_estado",
            onupdate="CASCADE",
            ondelete="RESTRICT"
        ),
        nullable=False
    )

    estado: Mapped["EstadoCondicion"] = relationship(
        back_populates="condiciones"
    )

    asignaciones: Mapped[list["RestauranteCargoEmpleado"]] = relationship(
        back_populates="condicion"
    )


class Empleado(Base):
    __tablename__ = "empleado"

    __table_args__ = (
        CheckConstraint(
            "dni BETWEEN 1000000 AND 999999999",
            name="chk_empleado_dni"
        ),
    )

    dni: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        primary_key=True
    )

    nombre_empleado: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    apellido_empleado: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    fecha_nacimiento: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )

    asignaciones: Mapped[list["RestauranteCargoEmpleado"]] = relationship(
        back_populates="empleado"
    )
