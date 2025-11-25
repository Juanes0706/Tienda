from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime


# --- Modelos de Tienda (Actualizados y Relaciones Cruzadas) ---

class Categoria(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(index=True, unique=True)
    descripcion: Optional[str] = None
    activa: bool = Field(default=True)
    media_url: Optional[str] = None
    deleted_at: Optional[datetime] = None

    # CORRECCIÓN: Usar "Producto" como string
    productos: List["Producto"] = Relationship(back_populates="categoria")


class ClienteProducto(SQLModel, table=True):
    cliente_id: int = Field(foreign_key="cliente.id", primary_key=True)
    producto_id: int = Field(foreign_key="producto.id", primary_key=True)


class Cliente(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(index=True)
    ciudad: str
    canal: str
    media_url: Optional[str] = None
    deleted_at: Optional[datetime] = None

    # CORRECCIÓN: Usar "Venta" como string
    ventas: List["Venta"] = Relationship(back_populates="cliente")

    # Relación many-to-many con productos favoritos
    productos_favoritos: List["Producto"] = Relationship(
        back_populates="clientes_favoritos",
        link_model=ClienteProducto
    )


class Producto(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    descripcion: Optional[str] = None
    precio: float
    stock: int
    activo: bool = Field(default=True) 
    deleted_at: Optional[datetime] = None
    media_url: Optional[str] = None

    categoria_id: int = Field(foreign_key="categoria.id")
    
    # CORRECCIÓN DE TU ERROR: Usar "Categoria" como string
    categoria: Optional["Categoria"] = Relationship(back_populates="productos")
    
    # CORRECCIÓN: Usar "DetalleVenta" como string
    detalles_venta: List["DetalleVenta"] = Relationship(back_populates="producto")

    # Relación many-to-many con clientes favoritos
    clientes_favoritos: List["Cliente"] = Relationship(
        back_populates="productos_favoritos",
        link_model=ClienteProducto
    )


# --- Modelos de Venta ---

class DetalleVenta(SQLModel, table=True):
    venta_id: Optional[int] = Field(default=None, primary_key=True, foreign_key="venta.id")
    producto_id: Optional[int] = Field(default=None, primary_key=True, foreign_key="producto.id")
    
    cantidad: int
    precio_unitario: float 
    
    # CORRECCIÓN: Usar strings
    venta: "Venta" = Relationship(back_populates="detalles")
    producto: "Producto" = Relationship(back_populates="detalles_venta")


class Venta(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    fecha_venta: datetime = Field(default_factory=datetime.now)
    total: float
    canal_venta: str = Field(default="presencial", description="Tipo de venta: 'presencial' o 'virtual'")
    
    cliente_id: int = Field(foreign_key="cliente.id")
    # CORRECCIÓN: Usar strings
    cliente: "Cliente" = Relationship(back_populates="ventas")
    
    # CORRECCIÓN: Usar strings
    detalles: List["DetalleVenta"] = Relationship(back_populates="venta")