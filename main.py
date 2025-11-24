from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from models import Categoria, Producto
from database import init_db
import crud
from schemas import CategoriaUpdate, ProductoUpdate, CategoriaConProductos, ProductoResponse, ProductoListResponse, RestarStock, CategoriaEliminada, ProductoEliminado, CategoriaCreate, ProductoCreate
from supabase_utils import upload_image_to_supabase
from typing import Optional

app = FastAPI(title="API Tienda con SQLModel")

# Crear la base de datos al iniciar
@app.on_event("startup")
def startup_event():
    init_db()


# Endpoints de categorias

@app.post("/categorias/", response_model=Categoria)
async def crear_categoria(categoria: CategoriaCreate):
    categoria_creada = await crud.crear_categoria(categoria)
    if not categoria_creada:
        raise HTTPException(status_code=400, detail="Categoría ya existe o error en la creación")
    return categoria_creada

@app.get("/categorias/", response_model=list[Categoria])
async def obtener_categorias():
    return await crud.obtener_categorias()    

@app.get("/categorias/{id}", response_model=Categoria)
async def obtener_categoria(id: int):
    categoria = await crud.obtener_categoria(id)
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return categoria

@app.get("/categorias/{id}/productos")
async def obtener_categoria_con_productos(id: int):
    categoria = await crud.obtener_categoria_con_productos(id)
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return categoria

@app.put("/categorias/{id}", response_model=Categoria)
async def actualizar_categoria(id: int, categoria: CategoriaUpdate):
    categoria_actualizada = await crud.actualizar_categoria(id, categoria)
    if not categoria_actualizada:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return categoria_actualizada

@app.patch("/categorias/{id}/desactivar", response_model=Categoria)
async def desactivar_categoria(id: int):
    categoria = await crud.desactivar_categoria(id)
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return categoria

@app.delete("/categorias/{id}")
async def eliminar_categoria(id: int):
    eliminado = await crud.eliminar_categoria(id)
    if not eliminado:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return {"mensaje": "Categoría eliminada correctamente"}

@app.get("/categorias/eliminadas")
async def obtener_categorias_eliminadas():
    return await crud.obtener_categorias_eliminadas()

# Endpoints de productos

@app.post("/productos/", response_model=Producto)
async def crear_producto(
    nombre: str = Form(...),
    descripcion: Optional[str] = Form(None),
    precio: float = Form(...),
    stock: int = Form(...),
    activo: bool = Form(True),
    categoria_id: int = Form(...),
    imagen: Optional[UploadFile] = File(None)
):
    imagen_url = None
    if imagen:
        imagen_url = await upload_image_to_supabase(imagen)
    producto_data = ProductoCreate(
        nombre=nombre,
        descripcion=descripcion,
        precio=precio,
        stock=stock,
        activo=activo,
        categoria_id=categoria_id,
        imagen_url=imagen_url
    )
    producto_creado = await crud.crear_producto(producto_data)
    if not producto_creado:
        raise HTTPException(status_code=400, detail="Producto no pudo ser creado")
    return producto_creado

@app.get("/productos/", response_model=list[ProductoListResponse])
async def obtener_productos():
    return await crud.obtener_productos()

@app.get("/productos/eliminados", response_model=list[ProductoEliminado])
async def obtener_productos_eliminados():
    productos = await crud.obtener_productos_eliminados()
    return productos

@app.get("/productos/{id}", response_model=Producto)
async def obtener_producto(id: int):
    producto = await crud.obtener_producto(id)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto

@app.get("/productos/{id}/categoria", response_model=ProductoResponse)
async def obtener_producto_con_categoria(id: int):
    producto = await crud.obtener_producto_con_categoria(id)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto    

@app.put("/productos/{id}", response_model=Producto)
async def actualizar_producto(
    id: int,
    nombre: Optional[str] = Form(None),
    descripcion: Optional[str] = Form(None),
    precio: Optional[float] = Form(None),
    stock: Optional[int] = Form(None),
    activo: Optional[bool] = Form(None),
    categoria_id: Optional[int] = Form(None),
    imagen: Optional[UploadFile] = File(None)
):
    imagen_url = None
    if imagen:
        imagen_url = await upload_image_to_supabase(imagen)
    producto_update_data = ProductoUpdate(
        nombre=nombre,
        descripcion=descripcion,
        precio=precio,
        stock=stock,
        activo=activo,
        categoria_id=categoria_id,
        imagen_url=imagen_url
    )
    producto_actualizado = await crud.actualizar_producto(id, producto_update_data)
    if not producto_actualizado:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto_actualizado    

@app.patch("/productos/{id}/desactivar", response_model=Producto)
async def desactivar_producto(id: int):
    producto = await crud.desactivar_producto(id)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto    

@app.patch("/productos/{id}/restar-stock", response_model=Producto)
async def restar_stock(id: int, restar: RestarStock):
    producto = await crud.restar_stock(id, restar.cantidad)
    if not producto:
        raise HTTPException(status_code=400, detail="Producto no encontrado o stock insuficiente")
    return producto    


@app.delete("/productos/{id}")
async def eliminar_producto(id: int):
    eliminado = await crud.eliminar_producto(id)
    if not eliminado:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return {"mensaje": "Producto eliminado correctamente"}
