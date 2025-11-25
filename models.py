from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime


class Categoria(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(index=True, unique=True)
    descripcion: Optional[str] = None
    activa: bool = Field(default=True)
    media_url: Optional[str] = None
    deleted_at: Optional[datetime] = None

    productos: List["Producto"] = Relationship(back_populates="categoria")


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
    categoria: Optional[Categoria] = Relationship(back_populates="productos")
