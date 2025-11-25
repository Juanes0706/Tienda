from pydantic import BaseModel, Field, conint, constr
from typing import Optional, List
from datetime import datetime

# =======================================================================
# Esquemas de Categoria
# =======================================================================

class CategoriaBase(BaseModel):
    nombre: constr(min_length=1, max_length=100)
    descripcion: Optional[str] = None
    activa: Optional[bool] = True
    media_url: Optional[str] = None

class CategoriaCreate(CategoriaBase):
    """Esquema para crear una categoría"""
    pass

class CategoriaUpdate(BaseModel):
    """Esquema para actualizar una categoría"""
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    activa: Optional[bool] = None
    media_url: Optional[str] = None

class CategoriaResponse(CategoriaBase):
    """Esquema de respuesta que incluye ID"""
    id: int
    media_url: Optional[str] = None

    class Config:
        from_attributes = True

# =======================================================================
# Esquemas de Producto
# =======================================================================

class ProductoBase(BaseModel):
    nombre: constr(min_length=1, max_length=100)
    descripcion: Optional[str] = None
    precio: float = Field(gt=0, description="El precio debe ser mayor que 0")
    stock: conint(ge=0) = 0
    activo: Optional[bool] = True
    categoria_id: int
    media_url: Optional[str] = None


class ProductoCreate(ProductoBase):
    """Esquema para crear un producto"""
    pass


class ProductoUpdate(BaseModel):
    """Esquema para actualizar un producto"""
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    precio: Optional[float] = Field(None, gt=0)
    stock: Optional[int] = Field(None, ge=0)
    activo: Optional[bool] = None
    categoria_id: Optional[int] = None
    media_url: Optional[str] = None


class ProductoResponse(ProductoBase):
    """Esquema de respuesta de producto con ID y categoría"""
    id: int
    categoria: Optional[CategoriaResponse] = None

    class Config:
        from_attributes = True

# =======================================================================
# Esquemas de Cliente 👤 (NUEVOS)
# =======================================================================

class ClienteBase(BaseModel):
    nombre: constr(min_length=1, max_length=100)
    ciudad: constr(min_length=1)
    canal: constr(min_length=1)
    media_url: Optional[str] = None

class ClienteCreate(ClienteBase):
    """Esquema para crear un cliente"""
    pass

class ClienteUpdate(BaseModel):
    """Esquema para actualizar un cliente"""
    nombre: Optional[str] = None
    ciudad: Optional[str] = None
    canal: Optional[str] = None
    media_url: Optional[str] = None

class ClienteResponse(ClienteBase):
    """Esquema de respuesta de cliente"""
    id: int
    
    class Config:
        from_attributes = True

# =======================================================================
# Esquemas de Venta y DetalleVenta (NUEVOS)
# =======================================================================

class DetalleVentaBase(BaseModel):
    producto_id: int
    cantidad: conint(gt=0)
    precio_unitario: float = Field(gt=0) # El precio al momento de la venta

class DetalleVentaCreate(DetalleVentaBase):
    """Esquema para crear una línea de detalle de venta"""
    pass

class DetalleVentaResponse(DetalleVentaBase):
    """Esquema de respuesta del detalle de venta"""
    # Incluye los IDs compuestos
    venta_id: int
    producto_id: int
    
    # Opcionalmente, puedes anidar el producto para una respuesta rica
    producto: Optional[ProductoResponse] = None 
    
    class Config:
        from_attributes = True

class VentaBase(BaseModel):
    cliente_id: int
    total: float = Field(gt=0)
    canal_venta: constr(pattern=r"^(presencial|virtual)$", strict=True) = 'presencial'

class VentaCreate(VentaBase):
    """Esquema para crear una venta con sus detalles"""
    # La lista de detalles es necesaria al crear la venta
    detalles: List[DetalleVentaCreate]

class VentaResponse(VentaBase):
    """Esquema de respuesta de venta"""
    id: int
    fecha_venta: datetime
    
    # Anida la lista de detalles y el cliente para la respuesta completa
    cliente: Optional[ClienteResponse] = None
    detalles: List[DetalleVentaResponse] = []

    class Config:
        from_attributes = True

# =======================================================================
# Esquemas de Respuesta Agregados / Eliminados
# =======================================================================

class CategoriaConProductos(CategoriaResponse):
    """Devuelve la categoría con todos sus productos"""
    productos: List[ProductoResponse] = []

    class Config:
        from_attributes = True


class ProductoListResponse(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str] = None
    precio: float
    stock: int
    activo: bool
    categoria_id: int
    categoria: str # Nombre de la categoría
    media_url: Optional[str] = None # Añadido para consistencia

    class Config:
        from_attributes = True


class RestarStock(BaseModel):
    cantidad: conint(gt=0)

class CategoriaEliminada(CategoriaResponse):
    deleted_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ProductoEliminado(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str] = None
    precio: float
    stock: int
    activo: bool
    categoria_id: int
    # No se incluye la categoría en el modelo eliminado ya que el objeto podría no existir
    categoria: Optional[CategoriaResponse] = None 
    deleted_at: Optional[datetime] = None
    media_url: Optional[str] = None # Añadido para consistencia

    class Config:
        from_attributes = True