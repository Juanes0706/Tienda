# models.py (Fragmento con los nuevos modelos)

# Importaciones necesarias
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime

# 1. Tabla de Asociación Muchos a Muchos
# Define los campos de la tabla intermedia que asocia Venta y Producto
class DetalleVenta(SQLModel, table=True):
    venta_id: Optional[int] = Field(default=None, primary_key=True, foreign_key="venta.id")
    producto_id: Optional[int] = Field(default=None, primary_key=True, foreign_key="producto.id")
    
    # Detalle de la transacción
    cantidad: int
    precio_unitario: float # Precio al momento de la venta
    
    # Relaciones para acceder a los objetos
    venta: "Venta" = Relationship(back_populates="detalles")
    producto: "Producto" = Relationship(back_populates="detalles_venta")


# 2. Modelo de Venta/Orden (Tabla Principal)
class Venta(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    fecha_venta: datetime = Field(default_factory=datetime.now)
    total: float
    
    # NUEVO CAMPO: Canal de Venta
    # Puedes usar un valor predeterminado si es más común uno de los dos.
    canal_venta: str = Field(default="presencial", description="Tipo de venta: 'presencial' o 'virtual'")
    
    # Relación a Cliente (Muchos a Uno)
    cliente_id: int = Field(foreign_key="cliente.id")
    cliente: "Cliente" = Relationship(back_populates="ventas")
    
    # Relación a los Productos a través de la tabla intermedia
    detalles: List["DetalleVenta"] = Relationship(back_populates="venta")

# --- Actualizaciones a los modelos existentes ---

# A. Actualizar Cliente para que tenga la relación 'ventas'
class Cliente(SQLModel, table=True):
    # ... (campos existentes) ...
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(index=True)
    ciudad: str
    canal: str
    media_url: Optional[str] = None
    deleted_at: Optional[datetime] = None

    ventas: List[Venta] = Relationship(back_populates="cliente") # <-- Nueva relación


# B. Actualizar Producto para que tenga la relación 'detalles_venta'
class Producto(SQLModel, table=True):
    # ... (campos existentes) ...
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    descripcion: Optional[str] = None
    precio: float
    stock: int
    activo: bool = Field(default=True)
    deleted_at: Optional[datetime] = None
    media_url: Optional[str] = None
    categoria_id: int = Field(foreign_key="categoria.id")
    categoria: Optional[Categoria] = Relationship(back_populates="productos")
    
    detalles_venta: List[DetalleVenta] = Relationship(back_populates="producto") # <-- Nueva relación