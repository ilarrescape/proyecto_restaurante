from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    BIGINT,
    Boolean,
    Date,
    DateTime,
    DECIMAL,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class Producto(Base):
    __tablename__ = "producto"

    #nombre_atributo: mapped[valor obtenido] = mapped_column(tipo de valor en SQLAlchemy O ForeignKey("tabla.atributo"), primarykey=True/False, unique=True/False, nullable=True/False)
    id_producto: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre_producto: Mapped[str] = mapped_column(String, nullable=False)
    descripcion: Mapped[str] = mapped_column(String(200), nullable=True)
    precio_unitario: Mapped[float] = mapped_column(DECIMAL, nullable=False)
    fk_categoria: Mapped[int] = mapped_column(ForeignKey("categoria.id_categoria"), nullable=False)
    fk_cuit_restaurante: Mapped[int] = mapped_column(ForeignKey("restaurante.cuit"), nullable=False)

    categoria: Mapped[Categoria] = relationship(back_populates="productos")
    restaurante: Mapped[list"Restaurante"] = relationship(back_populates="productos")


class Categoria(Base):
    __tablename__ = "categoria"

    id_categoria: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre_categoria: Mapped[str] = mapped_column(String, nullable=False)
    descripcion_categoria: Mapped[str] = mapped_column(String(200), nullable=True)












