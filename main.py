from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from models import Categoria, Producto
import crud
from schemas import (
    CategoriaUpdate, ProductoUpdate, CategoriaConProductos, ProductoResponse,
    ProductoListResponse, RestarStock, CategoriaEliminada, ProductoEliminado,
    CategoriaCreate, ProductoCreate
)
from supabase_utils import upload_image_to_supabase
from typing import Optional
from database import init_db # <- ¡NUEVA IMPORTACIÓN CLAVE!

app = FastAPI(title="API Tienda con SQLModel")

@app.on_event("startup")
async def on_startup():
    """
    Inicializa la base de datos (crea tablas si no existen) 
    al iniciar la aplicación.
    """
    await init_db() # <- Llamada a la función asíncrona de database.py

# ---------------------------
#  ENDPOINTS DE CATEGORÍAS
# ---------------------------

@app.post("/categorias/", response_model=Categoria)
async def crear_categoria(
    nombre: str = Form(...),
    descripcion: Optional[str] = Form(None),
    activa: Optional[bool] = Form(True),
    imagen: Optional[UploadFile] = File(None)
):
    imagen_url = None
    if imagen and imagen.filename:
        imagen_url = await upload_image_to_supabase(imagen)

    categoria_data = CategoriaCreate(
        nombre=nombre,
        descripcion=descripcion,
        activa=activa,
        media_url=imagen_url
    )
    categoria_creada = await crud.crear_categoria(categoria_data)
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

@app.get("/categorias/{id}/productos", response_model=CategoriaConProductos)
async def obtener_categoria_con_productos(id: int):
    categoria = await crud.obtener_categoria_con_productos(id)
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return categoria

@app.put("/categorias/{id}", response_model=Categoria)
async def actualizar_categoria(
    id: int,
    nombre: Optional[str] = Form(None),
    descripcion: Optional[str] = Form(None),
    activa: Optional[bool] = Form(None),
    imagen: Optional[UploadFile] = File(None)
):
    imagen_url = None
    if imagen and imagen.filename:
        imagen_url = await upload_image_to_supabase(imagen)

    categoria_update_data = CategoriaUpdate(
        nombre=nombre,
        descripcion=descripcion,
        activa=activa,
        media_url=imagen_url
    )

    # Filtrar campos que son None para no sobrescribir valores existentes
    categoria_update_data_filtered = categoria_update_data.dict(exclude_unset=True)

    if imagen_url is not None:
        categoria_update_data_filtered['media_url'] = imagen_url
    elif imagen and imagen.filename == "":
        categoria_update_data_filtered['media_url'] = None  # Permite eliminar URL existente

    categoria = await crud.actualizar_categoria(id, CategoriaUpdate(**categoria_update_data_filtered))
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return categoria

@app.patch("/categorias/{id}/desactivar", response_model=Categoria)
async def desactivar_categoria(id: int):
    categoria = await crud.desactivar_categoria(id)
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return categoria

@app.delete("/categorias/{id}")
async def eliminar_categoria(id: int):
    eliminada = await crud.eliminar_categoria(id)
    if not eliminada:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return {"message": "Categoría eliminada (soft delete) exitosamente"}

@app.get("/categorias/eliminadas", response_model=list[CategoriaEliminada])
async def obtener_categorias_eliminadas():
    return await crud.obtener_categorias_eliminadas()

# --------------------------
#  ENDPOINTS DE PRODUCTOS
# --------------------------

@app.post("/productos/", response_model=Producto)
async def crear_producto(
    nombre: str = Form(...),
    descripcion: Optional[str] = Form(None),
    precio: float = Form(...),
    stock: int = Form(0),
    activo: Optional[bool] = Form(True),
    categoria_id: int = Form(...),
    imagen: Optional[UploadFile] = File(None)
):
    imagen_url = None
    if imagen and imagen.filename:
        # Aquí se asume que upload_image_to_supabase devuelve una URL
        imagen_url = await upload_image_to_supabase(imagen)

    producto_data = ProductoCreate(
        nombre=nombre,
        descripcion=descripcion,
        precio=precio,
        stock=stock,
        activo=activo,
        categoria_id=categoria_id,
        media_url=imagen_url
    )
    
    producto_creado = await crud.crear_producto(producto_data)
    if not producto_creado:
        raise HTTPException(status_code=400, detail="Error en la creación del producto")
    return producto_creado

@app.get("/productos/", response_model=list[ProductoListResponse])
async def obtener_productos():
    return await crud.obtener_productos()

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
    
    # Asignar la categoría al esquema de respuesta
    return ProductoResponse.model_validate(producto)

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
    # Solo actualiza la URL si se subió un nuevo archivo
    if imagen and imagen.filename: 
        imagen_url = await upload_image_to_supabase(imagen)

    producto_update_data = ProductoUpdate(
        nombre=nombre,
        descripcion=descripcion,
        precio=precio,
        stock=stock,
        activo=activo,
        categoria_id=categoria_id,
        media_url=imagen_url # Esto solo actualizará si se proporcionó una imagen o es None
    )
    
    # Filtrar campos que son None para no sobrescribir valores existentes
    producto_update_data_filtered = producto_update_data.dict(exclude_unset=True)

    # Si se subió una imagen, su URL debe ser incluida explícitamente si existe
    if imagen_url is not None:
         producto_update_data_filtered['media_url'] = imagen_url
    elif imagen and imagen.filename == "": # Caso donde se envía el campo pero vacío
         producto_update_data_filtered['media_url'] = None # Permite eliminar la URL existente

    producto_actualizado = await crud.actualizar_producto(id, ProductoUpdate(**producto_update_data_filtered))
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
    return {"message": "Producto eliminado (soft delete) exitosamente"}

@app.get("/productos/eliminados", response_model=list[ProductoEliminado])
async def obtener_productos_eliminados():
    return await crud.obtener_productos_eliminados()