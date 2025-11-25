from sqlmodel import select, SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from models import Categoria, Producto, Cliente, Venta, DetalleVenta 
from database import async_engine
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from typing import Optional, List
from sqlalchemy import and_, or_ 

# =======================================================================
# 📦 Funciones CRUD para Categoria
# =======================================================================

async def crear_categoria(categoria_data):
    try:
        categoria_dict = categoria_data.dict()
        categoria = Categoria(**categoria_dict)
        async with AsyncSession(async_engine) as session:
            session.add(categoria)
            await session.commit()
            await session.refresh(categoria)
            return categoria
    except IntegrityError:
        return None
    
async def obtener_categorias(nombre: Optional[str] = None, activa: Optional[bool] = None):
    async with AsyncSession(async_engine) as session:
        query = select(Categoria).where(Categoria.deleted_at == None)

        if nombre is not None:
            query = query.where(Categoria.nombre.ilike(f"%{nombre}%"))
        if activa is not None:
            query = query.where(Categoria.activa == activa)
        else:
            # Default to active categories if activa filter is not specified
            query = query.where(Categoria.activa == True)

        result = await session.exec(query)
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
                "media_url": categoria.media_url,
                "productos": [
                    {
                        "id": p.id,
                        "nombre": p.nombre,
                        "descripcion": p.descripcion,
                        "precio": p.precio,
                        "stock": p.stock,
                        "activo": p.activo,
                        "categoria_id": p.categoria_id,
                        "media_url": p.media_url,
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
            update_data = categoria_update.dict(exclude_unset=True)
            for key, value in update_data.items():
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

# =======================================================================
# 🏷️ Funciones CRUD para Producto
# =======================================================================
        
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

async def obtener_productos(
    id: Optional[int] = None,
    nombre: Optional[str] = None,
    precio: Optional[float] = None,
    precio_min: Optional[float] = None,
    precio_max: Optional[float] = None,
    categoria_id: Optional[int] = None,
    stock: Optional[int] = None,
    stock_min: Optional[int] = None,
    stock_max: Optional[int] = None,
    activo: Optional[bool] = None
):
    async with AsyncSession(async_engine) as session:
        query = select(Producto, Categoria.nombre.label("categoria_nombre")).join(Categoria).where(Producto.deleted_at == None)

        # Aplicar filtros dinámicos
        if id is not None:
            query = query.where(Producto.id == id)
        if nombre is not None:
            query = query.where(Producto.nombre.ilike(f"%{nombre}%")) 
        if precio is not None:
            query = query.where(Producto.precio == precio)
        elif precio_min is not None or precio_max is not None:
            if precio_min is not None and precio_max is not None:
                query = query.where(and_(Producto.precio >= precio_min, Producto.precio <= precio_max))
            elif precio_min is not None:
                query = query.where(Producto.precio >= precio_min)
            elif precio_max is not None:
                query = query.where(Producto.precio <= precio_max)
        if categoria_id is not None:
            query = query.where(Producto.categoria_id == categoria_id)
        if stock is not None:
            query = query.where(Producto.stock == stock)
        elif stock_min is not None or stock_max is not None:
            if stock_min is not None and stock_max is not None:
                query = query.where(and_(Producto.stock >= stock_min, Producto.stock <= stock_max))
            elif stock_min is not None:
                query = query.where(Producto.stock >= stock_min)
            elif stock_max is not None:
                query = query.where(Producto.stock <= stock_max)
        if activo is not None:
            query = query.where(Producto.activo == activo)

        result = await session.exec(query)
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

# =======================================================================
# 👤 Funciones CRUD para Cliente
# =======================================================================

async def crear_cliente(cliente_data):
    """Crea un nuevo cliente."""
    try:
        cliente = Cliente(**cliente_data.dict())
        async with AsyncSession(async_engine) as session:
            session.add(cliente)
            await session.commit()
            await session.refresh(cliente)
            return cliente
    except Exception as e:
        print(f"Error creando cliente: {e}")
        return None

async def obtener_clientes(
    nombre: Optional[str] = None,
    ciudad: Optional[str] = None,
    canal: Optional[str] = None,
):
    """Obtiene clientes activos, con filtros opcionales."""
    async with AsyncSession(async_engine) as session:
        query = select(Cliente).where(Cliente.deleted_at == None)

        if nombre is not None:
            query = query.where(Cliente.nombre.ilike(f"%{nombre}%"))
        if ciudad is not None:
            query = query.where(Cliente.ciudad.ilike(f"%{ciudad}%"))
        if canal is not None:
            query = query.where(Cliente.canal == canal)

        result = await session.exec(query)
        clientes = result.all()
        return clientes

async def obtener_cliente(id: int):
    """Obtiene un cliente por ID (activo)."""
    async with AsyncSession(async_engine) as session:
        result = await session.exec(select(Cliente).where(Cliente.id == id, Cliente.deleted_at == None))
        cliente = result.first()
        return cliente
    
async def actualizar_cliente(id: int, cliente_update):
    """Actualiza los datos de un cliente."""
    async with AsyncSession(async_engine) as session:
        cliente = await session.get(Cliente, id)
        if cliente and cliente.deleted_at is None:
            update_data = cliente_update.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(cliente, key, value)
            await session.commit()
            await session.refresh(cliente)
            return cliente
        return None

async def eliminar_cliente(id: int):
    """Realiza un borrado suave (soft delete) de un cliente."""
    async with AsyncSession(async_engine) as session:
        cliente = await session.get(Cliente, id)
        if cliente and cliente.deleted_at is None:
            cliente.deleted_at = datetime.now()
            await session.commit()
            await session.refresh(cliente)
            return True
        return False

# =======================================================================
# 🛒 Funciones CRUD para Venta (y DetalleVenta)
# =======================================================================

async def crear_venta(venta_data):
    """
    Crea una nueva venta y sus detalles, y actualiza el stock de los productos.
    Asume que venta_data incluye una lista de 'detalles'.
    """
    async with AsyncSession(async_engine) as session:
        try:
            # 1. Validar y restar stock antes de crear la venta
            for detalle in venta_data.detalles:
                producto = await session.get(Producto, detalle.producto_id)
                # Verifica que el producto exista, no esté eliminado y tenga suficiente stock
                if not producto or producto.deleted_at is not None or producto.stock < detalle.cantidad:
                    raise ValueError(f"Stock insuficiente o producto inválido ID {detalle.producto_id}")
            
            # 2. Crear la Venta (excluyendo la lista de detalles para la tabla Venta)
            venta_dict = venta_data.dict(exclude={'detalles'})
            venta = Venta(**venta_dict)
            session.add(venta)
            await session.flush() 
            
            # 3. Crear los Detalles de Venta y actualizar el stock
            for detalle_data in venta_data.detalles:
                # Restar stock
                producto = await session.get(Producto, detalle_data.producto_id)
                producto.stock -= detalle_data.cantidad
                
                # Crear DetalleVenta
                detalle_dict = detalle_data.dict()
                detalle_dict['venta_id'] = venta.id
                detalle = DetalleVenta(**detalle_dict)
                session.add(detalle)
            
            await session.commit()
            
            # Refrescar y cargar relaciones para la respuesta
            await session.refresh(venta, attribute_names=['cliente', 'detalles'])
            for detalle in venta.detalles:
                await session.refresh(detalle, attribute_names=['producto'])
            
            return venta
            
        except ValueError as ve:
            await session.rollback()
            print(f"Error al procesar venta: {ve}")
            return None
        except Exception as e:
            await session.rollback()
            print(f"Error desconocido creando venta: {e}")
            return None

async def obtener_ventas(
    cliente_id: Optional[int] = None,
    canal_venta: Optional[str] = None,
    fecha_inicio: Optional[datetime] = None,
    fecha_fin: Optional[datetime] = None
):
    """Obtiene ventas, con filtros opcionales."""
    async with AsyncSession(async_engine) as session:
        query = select(Venta).options(selectinload(Venta.cliente), selectinload(Venta.detalles).selectinload(DetalleVenta.producto))

        if cliente_id is not None:
            query = query.where(Venta.cliente_id == cliente_id)
        if canal_venta is not None:
            query = query.where(Venta.canal_venta == canal_venta)
        if fecha_inicio is not None:
            query = query.where(Venta.fecha_venta >= fecha_inicio)
        if fecha_fin is not None:
            query = query.where(Venta.fecha_venta <= fecha_fin)

        result = await session.exec(query)
        ventas = result.all()
        return ventas

async def obtener_venta(id: int):
    """Obtiene una venta específica por ID."""
    async with AsyncSession(async_engine) as session:
        query = select(Venta).where(Venta.id == id).options(
            selectinload(Venta.cliente), 
            selectinload(Venta.detalles).selectinload(DetalleVenta.producto)
        )
        result = await session.exec(query)
        venta = result.first()
        return venta

# =======================================================================
# 🗑️ Funciones de Historial de Eliminados (Soft Delete)
# =======================================================================

async def obtener_categorias_eliminadas():
    """Obtiene la lista de categorías con borrado suave."""
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
                "media_url": cat.media_url, 
                "deleted_at": cat.deleted_at
            })
        return result_list

async def obtener_productos_eliminados():
    """Obtiene la lista de productos con borrado suave."""
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
                "media_url": prod.media_url, 
                "deleted_at": prod.deleted_at
            })
        return result_list

async def obtener_clientes_eliminados():
    """Obtiene la lista de clientes con borrado suave."""
    async with AsyncSession(async_engine) as session:
        result = await session.exec(select(Cliente).where(Cliente.deleted_at != None))
        clientes = result.all()
        result_list = []
        for cli in clientes:
            result_list.append({
                "id": cli.id,
                "nombre": cli.nombre,
                "ciudad": cli.ciudad,
                "canal": cli.canal,
                "media_url": cli.media_url,
                "deleted_at": cli.deleted_at
            })
        return result_list