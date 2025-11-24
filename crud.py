from sqlmodel import Session, select
from models import Categoria, Producto
from database import engine
from datetime import datetime
from sqlalchemy.exc import IntegrityError

# Funciones CRUD para Categoria

async def crear_categoria(categoria_data):
    try:
        categoria = Categoria(**categoria_data.dict())
        with Session(engine) as session:
            session.add(categoria)
            session.commit()
            session.refresh(categoria)
            return categoria
    except IntegrityError:
        return None
    
async def obtener_categorias():
    with Session(engine) as session:
        categorias = session.exec(select(Categoria).where(Categoria.activa == True, Categoria.deleted_at == None)).all()
        return categorias
    
async def obtener_categoria(id: int):
    with Session(engine) as session:
        categoria = session.exec(select(Categoria).where(Categoria.id == id, Categoria.deleted_at == None)).first()
        return categoria
    
async def eliminar_categoria(id: int):
    with Session(engine) as session:
        categoria = session.get(Categoria, id)
        if categoria:
            categoria.deleted_at = datetime.now()
            session.commit()
            session.refresh(categoria)
            return True
        return False

async def obtener_categoria_con_productos(id: int):
    from sqlalchemy.orm import selectinload
    with Session(engine) as session:
        categoria = session.exec(select(Categoria).where(Categoria.id == id, Categoria.deleted_at == None).options(selectinload(Categoria.productos))).first()
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
    with Session(engine) as session:
        categoria = session.exec(select(Categoria).where(Categoria.id == id, Categoria.deleted_at == None)).first()
        if categoria:
            for key, value in categoria_update.dict(exclude_unset=True).items():
                setattr(categoria, key, value)
            session.commit()
            session.refresh(categoria)
            return categoria
        return None
    
async def desactivar_categoria(id: int):
    with Session(engine) as session:
        categoria = session.exec(select(Categoria).where(Categoria.id == id, Categoria.deleted_at == None)).first()
        if categoria:
            categoria.activa = False
            session.commit()
            session.refresh(categoria)
            return categoria
        return None

# Funciones CRUD para producto        

async def crear_producto(producto_data):
    try:
        producto = Producto(**producto_data.dict())
        with Session(engine) as session:
            session.add(producto)
            session.commit()
            session.refresh(producto)
            return producto
    except Exception as e:
        print(f"Error creando producto: {e}")
        return None

async def obtener_productos():
    with Session(engine) as session:
        productos = session.exec(select(Producto, Categoria.nombre.label("categoria_nombre")).join(Categoria).where(Producto.deleted_at == None)).all()
        # Devolver productos con stock, precio, categoria
        result = []
        for producto, categoria_nombre in productos:
            producto_dict = producto.dict()
            producto_dict['categoria'] = categoria_nombre
            result.append(producto_dict)
        return result

async def obtener_producto(id: int):
    with Session(engine) as session:
        producto = session.exec(select(Producto).where(Producto.id == id, Producto.deleted_at == None)).first()
        return producto

async def eliminar_producto(id: int):
    with Session(engine) as session:
        producto = session.get(Producto, id)
        if producto:
            producto.deleted_at = datetime.now()
            session.commit()
            session.refresh(producto)
            return True
        return False

async def obtener_producto_con_categoria(id: int):
    with Session(engine) as session:
        producto = session.exec(select(Producto).where(Producto.id == id, Producto.deleted_at == None)).first()
        if producto:
            # Cargar la categoría relacionada
            session.refresh(producto, attribute_names=['categoria'])
            return producto
        return None

async def actualizar_producto(id: int, producto_update):
    with Session(engine) as session:
        producto = session.exec(select(Producto).where(Producto.id == id, Producto.deleted_at == None)).first()
        if producto:
            for key, value in producto_update.dict(exclude_unset=True).items():
                setattr(producto, key, value)
            session.commit()
            session.refresh(producto)
            return producto
        return None

async def desactivar_producto(id: int):
    with Session(engine) as session:
        producto = session.exec(select(Producto).where(Producto.id == id, Producto.deleted_at == None)).first()
        if producto:
            producto.activo = False
            session.commit()
            session.refresh(producto)
            return producto
        return None

async def restar_stock(id: int, cantidad: int):
    with Session(engine) as session:
        producto = session.exec(select(Producto).where(Producto.id == id, Producto.deleted_at == None)).first()
        if producto and producto.stock >= cantidad:
            producto.stock -= cantidad
            session.commit()
            session.refresh(producto)
            return producto
        return None

async def obtener_categorias_eliminadas():
    with Session(engine) as session:
        categorias = session.exec(select(Categoria).where(Categoria.deleted_at != None)).all()
        result = []
        for cat in categorias:
            result.append({
                "id": cat.id,
                "nombre": cat.nombre,
                "descripcion": cat.descripcion,
                "activa": cat.activa,
                "deleted_at": cat.deleted_at
            })
        return result

async def obtener_productos_eliminados():
    with Session(engine) as session:
        productos = session.exec(select(Producto).where(Producto.deleted_at != None)).all()
        result = []
        for prod in productos:
            result.append({
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
        return result
