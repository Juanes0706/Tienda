from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Query, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from models import Categoria, Producto, Cliente, Venta
import crud
from schemas import (
    CategoriaUpdate, ProductoUpdate, CategoriaConProductos, ProductoResponse,
    ProductoListResponse, RestarStock, CategoriaEliminada, ProductoEliminado,
    CategoriaCreate, ProductoCreate,
    # Nuevos esquemas de Cliente y Venta
    ClienteCreate, ClienteUpdate, ClienteResponse,
    VentaCreate, VentaResponse
)
from supabase_utils import upload_image_to_supabase
from typing import Optional, List
from database import init_db
from datetime import datetime

app = FastAPI(title="API Tienda con SQLModel y Supabase")

# Configurar archivos estáticos y templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.on_event("startup")
async def on_startup():
    """
    Inicializa la base de datos (crea tablas si no existen)
    al iniciar la aplicación.
    """
    await init_db()

# -----------------------------------------------------------------------
#                       ENDPOINTS PARA SERVIR HTML
# -----------------------------------------------------------------------

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/categorias/create")
async def categorias_create(request: Request):
    return templates.TemplateResponse("categorias/create.html", {"request": request})

@app.get("/categorias/read")
async def categorias_read(request: Request):
    return templates.TemplateResponse("categorias/read.html", {"request": request})

@app.get("/categorias/update")
async def categorias_update(request: Request):
    id_str = request.query_params.get("id")
    error_message = None
    categoria_data = None
    if not id_str:
        # Permite cargar la página sin ID
        pass 
    else:
        try:
            id_int = int(id_str)
            categoria_data = await crud.obtener_categoria(id_int)
            if not categoria_data:
                # === MODIFICACIÓN PARA MOSTRAR MENSAJE CLARO ===
                error_message = f"La Categoría con ID {id_int} no fue encontrada."
            # ================================================
        except ValueError:
            # === MODIFICACIÓN PARA MOSTRAR MENSAJE CLARO ===
            error_message = "ID inválido. Debe ser un número entero."
            # ================================================
    return templates.TemplateResponse("categorias/update.html", {"request": request, "categoria": categoria_data, "error_message": error_message})

@app.get("/categorias/delete")
async def categorias_delete(request: Request):
    return templates.TemplateResponse("categorias/delete.html", {"request": request})

@app.get("/productos/create")
async def productos_create(request: Request):
    return templates.TemplateResponse("productos/create.html", {"request": request})

@app.get("/productos/read")
async def productos_read(request: Request):
    return templates.TemplateResponse("productos/read.html", {"request": request})

@app.get("/productos/update")
async def productos_update(request: Request, id: Optional[int] = None):
    error_message = None
    producto_data = None
    if id is None:
        error_message = None # No es un error si se carga sin ID inicialmente
    else:
        # Note: Si 'id' no puede convertirse a int (por ejemplo, id='abc'), 
        # FastAPI ya maneja esto como un error 422 antes de llegar a esta función.
        # Asumimos que si llega aquí, 'id' es None o un int válido.
        producto_data = await crud.obtener_producto(id)
        if not producto_data:
            # === MODIFICACIÓN PARA MOSTRAR MENSAJE CLARO ===
            error_message = f"El Producto con ID {id} no fue encontrado."
            # ================================================
    return templates.TemplateResponse("productos/update.html", {"request": request, "producto": producto_data, "error_message": error_message})


@app.get("/productos/delete")
async def productos_delete(request: Request):
    return templates.TemplateResponse("productos/delete.html", {"request": request})

@app.get("/clientes/create")
async def clientes_create(request: Request):
    return templates.TemplateResponse("clientes/create.html", {"request": request})

@app.get("/clientes/read")
async def clientes_read(request: Request):
    return templates.TemplateResponse("clientes/read.html", {"request": request})

@app.get("/clientes/update")
async def clientes_update(request: Request):
    cliente_data = None
    error_message = None
    id_str = request.query_params.get("id")
    if id_str:
        try:
            id_int = int(id_str)
            cliente_data = await crud.obtener_cliente(id_int)
            if not cliente_data:
                error_message = "Cliente no encontrado"
        except ValueError:
            error_message = "ID inválido"
    return templates.TemplateResponse("clientes/update.html", {"request": request, "cliente": cliente_data, "error_message": error_message})

@app.get("/clientes/delete")
async def clientes_delete(request: Request):
    return templates.TemplateResponse("clientes/delete.html", {"request": request})

@app.get("/ventas/create")
async def ventas_create(request: Request):
    return templates.TemplateResponse("ventas/create.html", {"request": request})

@app.get("/ventas/read")
async def ventas_read(request: Request):
    return templates.TemplateResponse("ventas/read.html", {"request": request})

@app.get("/historial")
async def historial(request: Request):
    return templates.TemplateResponse("historial.html", {"request": request})

@app.get("/developer-info")
async def developer_info(request: Request):
    return templates.TemplateResponse("developer-info.html", {"request": request})

@app.get("/planning")
async def planning(request: Request):
    return templates.TemplateResponse("planning.html", {"request": request})

@app.get("/design")
async def design(request: Request):
    return templates.TemplateResponse("design.html", {"request": request})

@app.get("/informacion-del-proyecto")
async def informacion_del_proyecto(request: Request):
    return templates.TemplateResponse("informacion-del-proyecto.html", {"request": request})

# -----------------------------------------------------------------------
#                       ENDPOINTS DE CATEGORÍAS
# -----------------------------------------------------------------------

# Endpoint para crear categoría (usando Form data y upload)
@app.post("/categorias/")
async def crear_categoria(
    request: Request,
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

    return templates.TemplateResponse("categorias/create.html", {"request": request, "success": True, "categoria": categoria_creada})

@app.get("/categorias/", response_model=list[Categoria])
async def obtener_categorias(
    nombre: Optional[str] = Query(None, description="Filtrar por nombre parcial"),
    activa: Optional[str] = Query(None, description="Filtrar por estado activa")
):
    # Convertir el parámetro activa de str a bool o None
    activa_bool = None
    if activa is not None:
        if activa.lower() in ('true', '1', 'yes'):
            activa_bool = True
        elif activa.lower() in ('false', '0', 'no'):
            activa_bool = False
    return await crud.obtener_categorias(nombre=nombre, activa=activa_bool)

# === RUTA ESPECÍFICA DEBE IR ANTES DE LA RUTA DINÁMICA ===
@app.get("/categorias/eliminadas", response_model=list[CategoriaEliminada])
async def obtener_categorias_eliminadas():
    return await crud.obtener_categorias_eliminadas()
# =========================================================

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

# Endpoint para actualizar categoría (API: PUT para REST)
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

    categoria_update_data_filtered = categoria_update_data.model_dump(exclude_unset=True)

    if imagen_url is not None:
        categoria_update_data_filtered['media_url'] = imagen_url
    elif imagen and imagen.filename == "":
        # Permite borrar la imagen si se envía el campo 'imagen' vacío
        categoria_update_data_filtered['media_url'] = None 

    categoria = await crud.actualizar_categoria(id, CategoriaUpdate(**categoria_update_data_filtered))
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    return categoria # Devuelve JSON

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


# -----------------------------------------------------------------------
#                       ENDPOINTS DE PRODUCTOS
# -----------------------------------------------------------------------

# Endpoint para crear producto (usando Form data y upload)
@app.post("/productos/") # Cambiado a /productos/ para ser más RESTful
async def crear_producto(
    request: Request,
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

    return templates.TemplateResponse("productos/create.html", {"request": request, "success": True, "producto": producto_creado})


@app.get("/productos/", response_model=list[ProductoListResponse])
async def obtener_productos(
    id: Optional[str] = Query(None),
    nombre: Optional[str] = Query(None),
    precio: Optional[str] = Query(None),
    precio_min: Optional[str] = Query(None),
    precio_max: Optional[str] = Query(None),
    categoria_id: Optional[str] = Query(None),
    stock: Optional[str] = Query(None),
    stock_min: Optional[str] = Query(None),
    stock_max: Optional[str] = Query(None),
    activo: Optional[str] = Query(None)
):
    # Convertir parámetros de str a tipos apropiados
    id_int = int(id) if id and id.isdigit() else None
    precio_float = float(precio) if precio else None
    precio_min_float = float(precio_min) if precio_min else None
    precio_max_float = float(precio_max) if precio_max else None
    categoria_id_int = int(categoria_id) if categoria_id and categoria_id.isdigit() else None
    stock_int = int(stock) if stock and stock.isdigit() else None
    stock_min_int = int(stock_min) if stock_min and stock_min.isdigit() else None
    stock_max_int = int(stock_max) if stock_max and stock_max.isdigit() else None
    activo_bool = None
    if activo is not None:
        if activo.lower() in ('true', '1', 'yes'):
            activo_bool = True
        elif activo.lower() in ('false', '0', 'no'):
            activo_bool = False
        # Si está vacío o no reconocido, dejar como None

    return await crud.obtener_productos(
        id=id_int,
        nombre=nombre,
        precio=precio_float,
        precio_min=precio_min_float,
        precio_max=precio_max_float,
        categoria_id=categoria_id_int,
        stock=stock_int,
        stock_min=stock_min_int,
        stock_max=stock_max_int,
        activo=activo_bool
    )

# === RUTA ESPECÍFICA DEBE IR ANTES DE LA RUTA DINÁMICA ===
@app.get("/productos/eliminados", response_model=list[ProductoEliminado])
async def obtener_productos_eliminados():
    return await crud.obtener_productos_eliminados()
# =========================================================

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
    
    return ProductoResponse.model_validate(producto)

# Endpoint PUT para actualización de producto (API, devuelve JSON)
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
    if imagen and imagen.filename: 
        imagen_url = await upload_image_to_supabase(imagen)

    producto_update_data = ProductoUpdate(
        nombre=nombre,
        descripcion=descripcion,
        precio=precio,
        stock=stock,
        activo=activo,
        categoria_id=categoria_id,
        media_url=imagen_url
    )
    
    producto_update_data_filtered = producto_update_data.model_dump(exclude_unset=True)

    if imagen_url is not None:
          producto_update_data_filtered['media_url'] = imagen_url
    elif imagen and imagen.filename == "":
          producto_update_data_filtered['media_url'] = None 

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


# -----------------------------------------------------------------------
#                       ENDPOINTS DE CLIENTES 👤 (NUEVOS)
# -----------------------------------------------------------------------
@app.post("/clientes/", response_model=ClienteResponse)
async def crear_cliente(
    nombre: str = Form(...),
    ciudad: str = Form(...),
    canal: str = Form(...),
    imagen: Optional[UploadFile] = File(None)
):
    imagen_url = None
    if imagen and imagen.filename:
        imagen_url = await upload_image_to_supabase(imagen) 

    cliente_data = ClienteCreate(
        nombre=nombre,
        ciudad=ciudad,
        canal=canal,
        media_url=imagen_url
    )
    cliente_creado = await crud.crear_cliente(cliente_data)
    if not cliente_creado:
        raise HTTPException(status_code=400, detail="Error en la creación del cliente")
    return cliente_creado

@app.get("/clientes/", response_model=list[ClienteResponse])
async def obtener_clientes(
    nombre: Optional[str] = Query(None, description="Filtrar por nombre parcial"),
    ciudad: Optional[str] = Query(None, description="Filtrar por ciudad parcial"),
    canal: Optional[str] = Query(None, description="Filtrar por canal (e.g., 'web', 'tienda')")
):
    nombre_filter = nombre if nombre else None
    ciudad_filter = ciudad if ciudad else None
    canal_filter = canal if canal else None

    clientes = await crud.obtener_clientes(nombre=nombre_filter, ciudad=ciudad_filter, canal=canal_filter)
    return clientes

# === RUTA ESPECÍFICA DEBE IR ANTES DE LA RUTA DINÁMICA ===
@app.get("/clientes/eliminados", response_model=list[ClienteResponse])
async def obtener_clientes_eliminados():
    return await crud.obtener_clientes_eliminados()
# =========================================================

@app.get("/clientes/{id}", response_model=ClienteResponse)
async def obtener_cliente(id: int):
    cliente = await crud.obtener_cliente(id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente

@app.put("/clientes/{id}", response_model=ClienteResponse)
async def actualizar_cliente(
    id: int,
    nombre: Optional[str] = Form(None),
    ciudad: Optional[str] = Form(None),
    canal: Optional[str] = Form(None),
    imagen: Optional[UploadFile] = File(None)
):
    imagen_url = None
    if imagen and imagen.filename:
        imagen_url = await upload_image_to_supabase(imagen)

    cliente_update_data = ClienteUpdate(
        nombre=nombre,
        ciudad=ciudad,
        canal=canal,
        media_url=imagen_url
    )
    
    cliente_update_data_filtered = cliente_update_data.model_dump(exclude_unset=True)

    if imagen_url is not None:
          cliente_update_data_filtered['media_url'] = imagen_url
    elif imagen and imagen.filename == "":
          cliente_update_data_filtered['media_url'] = None 
    
    cliente_actualizado = await crud.actualizar_cliente(id, ClienteUpdate(**cliente_update_data_filtered))
    if not cliente_actualizado:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return cliente_actualizado

@app.delete("/clientes/{id}")
async def eliminar_cliente(id: int):
    eliminado = await crud.eliminar_cliente(id)
    if not eliminado:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return {"message": "Cliente eliminado (soft delete) exitosamente"}


# -----------------------------------------------------------------------
#                       ENDPOINTS DE VENTAS 🛒 (NUEVOS)
# -----------------------------------------------------------------------

@app.post("/ventas/", response_model=VentaResponse)
async def crear_venta(venta_data: VentaCreate):
    """
    Crea una nueva venta, sus detalles y actualiza el stock de productos.
    Recibe el cuerpo como JSON (VentaCreate).
    """
    venta_creada = await crud.crear_venta(venta_data)
    if not venta_creada:
        # El error 400 ya puede venir de stock insuficiente o cliente_id inválido
        raise HTTPException(status_code=400, detail="Error al crear la venta. Verifique stock o cliente_id.")
    return venta_creada

@app.get("/ventas/", response_model=List[VentaResponse])
async def obtener_ventas(
    cliente_id: Optional[int] = Query(None, description="Filtrar por ID de cliente"),
    canal: Optional[str] = Query(None, description="Filtrar por canal de venta ('presencial' o 'virtual')"),
    fecha_inicio: Optional[datetime] = Query(None, description="Fecha de inicio (ISO 8601)"),
    fecha_fin: Optional[datetime] = Query(None, description="Fecha de fin (ISO 8601)")
):
    ventas = await crud.obtener_ventas(
        cliente_id=cliente_id,
        canal_venta=canal,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin
    )
    return ventas

@app.get("/ventas/{id}", response_model=VentaResponse)
async def obtener_venta(id: int):
    venta = await crud.obtener_venta(id)
    if not venta:
        raise HTTPException(status_code=404, detail="Venta no encontrada")
    return venta