from sqlmodel import select, SQLModel # <- [MODIFICADO] Se elimina la importación de 'Session'
from sqlmodel.ext.asyncio.session import AsyncSession
from models import Categoria, Producto
from database import async_engine
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

# Funciones CRUD para Categoria

async def crear_categoria(categoria_data):
    try:
        categoria = Categoria(**categoria_data.dict())
        async with AsyncSession(async_engine) as session:
            session.add(categoria)
            await session.commit()
            await session.refresh(categoria)
            return categoria
    except IntegrityError:
        return None
    
async def obtener_categorias():
    async with AsyncSession(async_engine) as session:
        result = await session.exec(select(Categoria).where(Categoria.activa == True, Categoria.deleted_at == None))
        categorias = result.all()
        return categorias
    
async def obtener_categoria(id: int):
    async with AsyncSession(async_engine) as session:
        result = await session.exec(select(Categoria).where(Categoria.id == id, Categoria.deleted_at == None))
        categoria = result.first()
        return categoria
    
async def eliminar_categoria(id: int):
    async with AsyncSession(async_engine) as session:
        categoria = await session.get(Categoria, id)
        if categoria:
            categoria.deleted_at = datetime.now()
            await session.commit()
            await session.refresh(categoria)
            return True
        return False

async def obtener_categoria_con_productos(id: int):
    async with AsyncSession(async_engine) as session:
        result = await session.exec(select(Categoria).where(Categoria.id == id, Categoria.deleted_at == None).options(selectinload(Categoria.productos)))
        categoria = result.first()
        if categoria:
            # Devolver como dict para evitar lazy loading issues
            return {
                "id": categoria.id,
                "nombre": categoria.nombre,
                "descripcion": categoria.descripcion,
                "activa": categoria.activa,
                "productos": [
                    {
                        "id": p.id,
                        "nombre": p.nombre,
                        "descripcion": p.descripcion,
                        "precio": p.precio,
                        "stock": p.stock,
                        "activo": p.activo,
                        "categoria_id": p.categoria_id,
                        "categoria": {
                            "id": categoria.id,
                            "nombre": categoria.nombre,
                            "descripcion": categoria.descripcion,
                            "activa": categoria.activa
                        }
                    } for p in categoria.productos if p.deleted_at is None
                ]
            }
        return None
    
    
async def actualizar_categoria(id: int, categoria_update):
    async with AsyncSession(async_engine) as session:
        result = await session.exec(select(Categoria).where(Categoria.id == id, Categoria.deleted_at == None))
        categoria = result.first()
        if categoria:
            for key, value in categoria_update.dict(exclude_unset=True).items():
                setattr(categoria, key, value)
            await session.commit()
            await session.refresh(categoria)
            return categoria
        return None
    
async def desactivar_categoria(id: int):
    async with AsyncSession(async_engine) as session:
        result = await session.exec(select(Categoria).where(Categoria.id == id, Categoria.deleted_at == None))
        categoria = result.first()
        if categoria:
            categoria.activa = False
            await session.commit()
            await session.refresh(categoria)
            return categoria
        return None

# Funciones CRUD para producto        

async def crear_producto(producto_data):
    try:
        producto = Producto(**producto_data.dict())
        async with AsyncSession(async_engine) as session:
            session.add(producto)
            await session.commit()
            await session.refresh(producto)
            return producto
    except Exception as e:
        print(f"Error creando producto: {e}")
        return None

async def obtener_productos():
    async with AsyncSession(async_engine) as session:
        result = await session.exec(select(Producto, Categoria.nombre.label("categoria_nombre")).join(Categoria).where(Producto.deleted_at == None))
        productos = result.all()
        # Devolver productos con stock, precio, categoria
        result_list = []
        for producto, categoria_nombre in productos:
            producto_dict = producto.dict()
            producto_dict['categoria'] = categoria_nombre
            result_list.append(producto_dict)
        return result_list

async def obtener_producto(id: int):
    async with AsyncSession(async_engine) as session:
        result = await session.exec(select(Producto).where(Producto.id == id, Producto.deleted_at == None))
        producto = result.first()
        return producto

async def eliminar_producto(id: int):
    async with AsyncSession(async_engine) as session:
        producto = await session.get(Producto, id)
        if producto:
            producto.deleted_at = datetime.now()
            await session.commit()
            await session.refresh(producto)
            return True
        return False

async def obtener_producto_con_categoria(id: int):
    async with AsyncSession(async_engine) as session:
        result = await session.exec(select(Producto).where(Producto.id == id, Producto.deleted_at == None))
        producto = result.first()
        if producto:
            # Cargar la categoría relacionada
            await session.refresh(producto, attribute_names=['categoria'])
            return producto
        return None

async def actualizar_producto(id: int, producto_update):
    async with AsyncSession(async_engine) as session:
        result = await session.exec(select(Producto).where(Producto.id == id, Producto.deleted_at == None))
        producto = result.first()
        if producto:
            for key, value in producto_update.dict(exclude_unset=True).items():
                setattr(producto, key, value)
            await session.commit()
            await session.refresh(producto)
            return producto
        return None

async def desactivar_producto(id: int):
    async with AsyncSession(async_engine) as session:
        result = await session.exec(select(Producto).where(Producto.id == id, Producto.deleted_at == None))
        producto = result.first()
        if producto:
            producto.activo = False
            await session.commit()
            await session.refresh(producto)
            return producto
        return None

async def restar_stock(id: int, cantidad: int):
    async with AsyncSession(async_engine) as session:
        result = await session.exec(select(Producto).where(Producto.id == id, Producto.deleted_at == None))
        producto = result.first()
        if producto and producto.stock >= cantidad:
            producto.stock -= cantidad
            await session.commit()
            await session.refresh(producto)
            return producto
        return None

async def obtener_categorias_eliminadas():
    async with AsyncSession(async_engine) as session:
        result = await session.exec(select(Categoria).where(Categoria.deleted_at != None))
        categorias = result.all()
        result_list = []
        for cat in categorias:
            result_list.append({
                "id": cat.id,
                "nombre": cat.nombre,
                "descripcion": cat.descripcion,
                "activa": cat.activa,
                "deleted_at": cat.deleted_at
            })
        return result_list

async def obtener_productos_eliminados():
    async with AsyncSession(async_engine) as session:
        result = await session.exec(select(Producto).where(Producto.deleted_at != None))
        productos = result.all()
        result_list = []
        for prod in productos:
            result_list.append({
                "id": prod.id,
                "nombre": prod.nombre,
                "descripcion": prod.descripcion,
                "precio": prod.precio,
                "stock": prod.stock,
                "activo": prod.activo,
                "categoria_id": prod.categoria_id,
                "categoria": None,
                "deleted_at": prod.deleted_at
            })
        return result_list