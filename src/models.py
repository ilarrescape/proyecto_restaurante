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


class Ciudad(Base):
    __tablename__ = "ciudad"
    id_ciudad: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre_ciudad: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    restaurantes: Mapped[list["Restaurante"]] = relationship(back_populates="ciudad")


class Restaurante(Base):
    __tablename__ = "restaurante"
    cuit: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    razon_social: Mapped[str] = mapped_column(String(150), nullable=False)
    nombre_fantasia: Mapped[str] = mapped_column(String(150), nullable=False)
    direccion: Mapped[str] = mapped_column(String(180), nullable=False)
    id_ciudad: Mapped[int] = mapped_column(ForeignKey("ciudad.id_ciudad"), nullable=False)

    ciudad: Mapped[Ciudad] = relationship(back_populates="restaurantes")
    productos: Mapped[list["Producto"]] = relationship(back_populates="restaurante")
    mesas: Mapped[list["Mesa"]] = relationship(back_populates="restaurante")
    pedidos: Mapped[list["Pedido"]] = relationship(back_populates="restaurante")


class Area(Base):
    __tablename__ = "area"
    id_area: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre_area: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)


class Cargo(Base):
    __tablename__ = "cargo"
    id_cargo: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre_cargo: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)


class AreaCargo(Base):
    __tablename__ = "area_cargo"
    id_area: Mapped[int] = mapped_column(
        ForeignKey("area.id_area", ondelete="CASCADE"), primary_key=True
    )
    id_cargo: Mapped[int] = mapped_column(
        ForeignKey("cargo.id_cargo", ondelete="CASCADE"), primary_key=True
    )
    area: Mapped[Area] = relationship()
    cargo: Mapped[Cargo] = relationship()


class EstadoCondicion(Base):
    __tablename__ = "estado_condicion"
    id_estado_condicion: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre_estado_condicion: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    empresa_de_capacitacion: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    condiciones: Mapped[list["Condicion"]] = relationship(back_populates="estado")


class Condicion(Base):
    __tablename__ = "condicion"
    id_condicion: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre_condicion: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    id_estado_condicion: Mapped[int] = mapped_column(
        ForeignKey("estado_condicion.id_estado_condicion"), nullable=False
    )
    estado: Mapped[EstadoCondicion] = relationship(back_populates="condiciones")


class Empleado(Base):
    __tablename__ = "empleado"
    dni: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    nombre_empleado: Mapped[str] = mapped_column(String(100), nullable=False)
    apellido_empleado: Mapped[str] = mapped_column(String(100), nullable=False)
    fecha_nacimiento: Mapped[date] = mapped_column(Date, nullable=False)
    pedidos: Mapped[list["Pedido"]] = relationship(back_populates="empleado")


class RestauranteCargoEmpleado(Base):
    __tablename__ = "restaurante_cargo_empleado"
    id_cargo: Mapped[int] = mapped_column(ForeignKey("cargo.id_cargo"), primary_key=True)
    id_condicion: Mapped[int] = mapped_column(ForeignKey("condicion.id_condicion"), primary_key=True)
    cuit_restaurante: Mapped[int] = mapped_column(ForeignKey("restaurante.cuit"), primary_key=True)
    dni_empleado: Mapped[int] = mapped_column(ForeignKey("empleado.dni"), primary_key=True)

    cargo: Mapped[Cargo] = relationship()
    condicion: Mapped[Condicion] = relationship()
    restaurante: Mapped[Restaurante] = relationship()
    empleado: Mapped[Empleado] = relationship()


class Categoria(Base):
    __tablename__ = "categoria"
    id_categoria: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre_categoria: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    descripcion_categoria: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    productos: Mapped[list["Producto"]] = relationship(back_populates="categoria")


class Producto(Base):
    __tablename__ = "producto"
    id_producto: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre_producto: Mapped[str] = mapped_column(String(150), nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    precio_unitario: Mapped[Decimal] = mapped_column(DECIMAL(12, 2), nullable=False)
    id_categoria_producto: Mapped[int] = mapped_column(
        ForeignKey("categoria.id_categoria"), nullable=False
    )
    cuit_restaurante: Mapped[int] = mapped_column(ForeignKey("restaurante.cuit"), nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    categoria: Mapped[Categoria] = relationship(back_populates="productos")
    restaurante: Mapped[Restaurante] = relationship(back_populates="productos")
    detalles: Mapped[list["DetallePedido"]] = relationship(back_populates="producto")


class Mesa(Base):
    __tablename__ = "mesa"
    id_mesa: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    numero_referencia: Mapped[str] = mapped_column(String(30), nullable=False)
    cantidad_sillas: Mapped[int] = mapped_column(Integer, default=2, nullable=False)
    ubicacion_x: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(10, 2), nullable=True)
    ubicacion_y: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(10, 2), nullable=True)
    descripcion: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    cuit_restaurante: Mapped[int] = mapped_column(ForeignKey("restaurante.cuit"), nullable=False)
    activa: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    restaurante: Mapped[Restaurante] = relationship(back_populates="mesas")
    pedidos: Mapped[list["Pedido"]] = relationship(back_populates="mesa")


class TipoCliente(Base):
    __tablename__ = "tipo_cliente"
    id_tipo_cliente: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre_tipo_cliente: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    clientes: Mapped[list["Cliente"]] = relationship(back_populates="tipo")


class Cliente(Base):
    __tablename__ = "cliente"
    dni: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    nombre_cliente: Mapped[str] = mapped_column(String(100), nullable=False)
    apellido_cliente: Mapped[str] = mapped_column(String(100), nullable=False)
    fecha_nacimiento: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    id_tipo_cliente: Mapped[int] = mapped_column(ForeignKey("tipo_cliente.id_tipo_cliente"), nullable=False)
    tipo: Mapped[TipoCliente] = relationship(back_populates="clientes")
    pedidos: Mapped[list["Pedido"]] = relationship(back_populates="cliente")


class TipoComprobante(Base):
    __tablename__ = "tipo_comprobante"
    id_tipo_comprobante: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre_tipo_comprobante: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    pedidos: Mapped[list["Pedido"]] = relationship(back_populates="tipo_comprobante")


class EstadoPedido(Base):
    __tablename__ = "estado_pedido"
    id_estado: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre_estado: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    pedidos: Mapped[list["Pedido"]] = relationship(back_populates="estado")


class Pedido(Base):
    __tablename__ = "pedido"
    id_pedido: Mapped[int] = mapped_column(BIGINT, primary_key=True, autoincrement=True)
    id_tipo_comprobante: Mapped[int] = mapped_column(
        ForeignKey("tipo_comprobante.id_tipo_comprobante"), nullable=False
    )
    
    # cuit_restaurante = nombre atributo (tiene que ser el mismo que en la base de datos)
    # Mapped[int] = tipo de dato final que obtiene para python
    # mapped_column = Da inicio a las características que tiene la columna en la base de datos
    # ForeignKey = Indica que es una clave foránea
    # ("restaurante.cuit") = tabla a la que hace referencia
    # nullable = False: Not Null
    cuit_restaurante: Mapped[int] = mapped_column(ForeignKey("restaurante.cuit"), nullable=False)
    dni_empleado: Mapped[int] = mapped_column(ForeignKey("empleado.dni"), nullable=False)
    dni_cliente: Mapped[Optional[int]] = mapped_column(ForeignKey("cliente.dni"), nullable=True)
    id_mesa: Mapped[Optional[int]] = mapped_column(ForeignKey("mesa.id_mesa"), nullable=True)
    id_estado: Mapped[int] = mapped_column(ForeignKey("estado_pedido.id_estado"), nullable=False)
    fecha_hora: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    total_pedido: Mapped[Decimal] = mapped_column(DECIMAL(12, 2), default=Decimal("0.00"), nullable=False)
    observaciones: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)


    # Acá indica como trabajan las relaciones a nivel clase
    # tipo_comprobante: es un atributo que establece la relación con una clase
    # Mapped[TipoComprobante]: indica con qué clase se relaciona
    # relationship(back_populates="pedidos"): etiqueta la relación con la palabra "pedidos"
    tipo_comprobante: Mapped[TipoComprobante] = relationship(back_populates="pedidos")
    restaurante: Mapped[Restaurante] = relationship(back_populates="pedidos")
    empleado: Mapped[Empleado] = relationship(back_populates="pedidos")
    cliente: Mapped[Optional[Cliente]] = relationship(back_populates="pedidos")
    mesa: Mapped[Optional[Mesa]] = relationship(back_populates="pedidos")
    estado: Mapped[EstadoPedido] = relationship(back_populates="pedidos")
    
    #VER EL LUNES
    detalles: Mapped[list["DetallePedido"]] = relationship(
        back_populates="pedido",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class DetallePedido(Base):
    __tablename__ = "detalle_pedido"
    id_producto: Mapped[int] = mapped_column(
        ForeignKey("producto.id_producto"), primary_key=True
    )
    id_pedido: Mapped[int] = mapped_column(
        ForeignKey("pedido.id_pedido", ondelete="CASCADE"), primary_key=True
    )
    cantidad: Mapped[int] = mapped_column(Integer, nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(DECIMAL(12, 2), nullable=False)

    producto: Mapped[Producto] = relationship(back_populates="detalles")
    pedido: Mapped[Pedido] = relationship(back_populates="detalles")


class Rol(Base):
    __tablename__ = "rol"
    id_rol: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre_rol: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    usuarios: Mapped[list["Usuario"]] = relationship(back_populates="rol")


class Usuario(Base):
    __tablename__ = "usuario"
    id_usuario: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre_usuario: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    nombre_completo: Mapped[str] = mapped_column(String(150), nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    id_rol: Mapped[int] = mapped_column(ForeignKey("rol.id_rol"), nullable=False)
    dni_empleado: Mapped[Optional[int]] = mapped_column(ForeignKey("empleado.dni"), unique=True, nullable=True)
    cuit_restaurante: Mapped[Optional[int]] = mapped_column(ForeignKey("restaurante.cuit"), nullable=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, nullable=False)
    ultimo_acceso: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    rol: Mapped[Rol] = relationship(back_populates="usuarios")
    empleado: Mapped[Optional[Empleado]] = relationship()
    restaurante: Mapped[Optional[Restaurante]] = relationship()
