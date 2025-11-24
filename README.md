# API Tienda con SQLModel

## Descripción
Este proyecto es una API Tienda en línea, desarrollada con FastAPI y SQLModel. Permite gestionar categorías y productos, incluyendo operaciones CRUD (Crear, Leer, Actualizar, Eliminar). La base de datos utilizada es SQLite para simplicidad y facilidad de uso.

La API incluye funcionalidades como:
- Gestión de categorías (crear, listar, obtener, actualizar, desactivar, eliminar).
- Gestión de productos (crear, listar, obtener, actualizar, desactivar, eliminar, restar stock).
- Relaciones entre categorías y productos.
- Validaciones con Pydantic para asegurar la integridad de los datos.

## Tecnologías Utilizadas
- **FastAPI**: Framework para construir APIs web rápidas y modernas.
- **SQLModel**: Librería para trabajar con SQLAlchemy y Pydantic, facilitando el manejo de modelos de base de datos.
- **SQLite**: Base de datos ligera y embebida.
- **Pydantic**: Para validación de datos y esquemas.

## Instalación
1. Clona el repositorio:
   ```
   git clone <url-del-repositorio>
   cd tiendaoficial
   ```

2. Instala las dependencias:
   ```
   pip install fastapi sqlmodel uvicorn
   ```

3. Ejecuta la aplicación:
   ```
   uvicorn main:app --reload
   ```

La API estará disponible en `http://127.0.0.1:8000`.

## Uso
Una vez ejecutada, puedes acceder a la documentación interactiva de la API en `http://127.0.0.1:8000/docs` (Swagger UI) o `http://127.0.0.1:8000/redoc` (ReDoc).

### Endpoints Principales
#### Categorías
- `POST /categorias/`: Crear una nueva categoría.
- `GET /categorias/`: Obtener todas las categorías activas.
- `GET /categorias/{id}`: Obtener una categoría por ID.
- `GET /categorias/{id}/productos`: Obtener una categoría con sus productos.
- `PUT /categorias/{id}`: Actualizar una categoría.
- `PATCH /categorias/{id}/desactivar`: Desactivar una categoría.
- `DELETE /categorias/{id}`: Eliminar una categoría.

#### Productos
- `POST /productos/`: Crear un nuevo producto.
- `GET /productos/`: Obtener todos los productos.
- `GET /productos/{id}`: Obtener un producto por ID.
- `GET /productos/{id}/categoria`: Obtener un producto con su categoría.
- `PUT /productos/{id}`: Actualizar un producto.
- `PATCH /productos/{id}/desactivar`: Desactivar un producto.
- `PATCH /productos/{id}/restar-stock`: Restar stock a un producto.
- `DELETE /productos/{id}`: Eliminar un producto.

## Estructura del Proyecto
- `models.py`: Definición de los modelos de base de datos (Categoria, Producto).
- `schemas.py`: Esquemas Pydantic para validación y respuestas.
- `database.py`: Configuración de la base de datos y inicialización.
- `crud.py`: Funciones CRUD para operaciones en la base de datos.
- `main.py`: Punto de entrada de la aplicación FastAPI.

## Modelos y Relaciones

### Clases de Modelos
- **Categoria**:
  - `id`: int (primary key)
  - `nombre`: str (unique, index)
  - `descripcion`: Optional[str]
  - `activa`: bool (default: True)
  - `deleted_at`: Optional[datetime]
  - Relación: `productos` (List[Producto]) - back_populates="categoria"

- **Producto**:
  - `id`: int (primary key)
  - `nombre`: str
  - `descripcion`: Optional[str]
  - `precio`: float
  - `stock`: int
  - `activo`: bool (default: True)
  - `deleted_at`: Optional[datetime]
  - `categoria_id`: int (foreign key to Categoria.id)
  - Relación: `categoria` (Optional[Categoria]) - back_populates="productos"

### Relaciones
- Una **Categoria** puede tener muchos **Producto** (one-to-many).
- Un **Producto** pertenece a una **Categoria** (many-to-one).

## Endpoints Detallados

### Categorías
- `POST /categorias/`: Crear una nueva categoría.
  - Body: `CategoriaCreate` (nombre, descripcion, activa)
  - Response: `Categoria`
- `GET /categorias/`: Obtener todas las categorías activas.
  - Response: `list[Categoria]`
- `GET /categorias/{id}`: Obtener una categoría por ID.
  - Response: `Categoria`
- `GET /categorias/{id}/productos`: Obtener una categoría con sus productos.
  - Response: dict con categoría y lista de productos
- `PUT /categorias/{id}`: Actualizar una categoría.
  - Body: `CategoriaUpdate`
  - Response: `Categoria`
- `PATCH /categorias/{id}/desactivar`: Desactivar una categoría.
  - Response: `Categoria`
- `DELETE /categorias/{id}`: Eliminar una categoría (soft delete).
  - Response: dict con mensaje
- `GET /categorias/eliminadas`: Obtener categorías eliminadas.
  - Response: list[dict]

### Productos
- `POST /productos/`: Crear un nuevo producto.
  - Body: `ProductoCreate` (nombre, descripcion, precio, stock, activo, categoria_id)
  - Response: `Producto`
- `GET /productos/`: Obtener todos los productos.
  - Response: `list[ProductoListResponse]`
- `GET /productos/{id}`: Obtener un producto por ID.
  - Response: `Producto`
- `GET /productos/{id}/categoria`: Obtener un producto con su categoría.
  - Response: `ProductoResponse`
- `PUT /productos/{id}`: Actualizar un producto.
  - Body: `ProductoUpdate`
  - Response: `Producto`
- `PATCH /productos/{id}/desactivar`: Desactivar un producto.
  - Response: `Producto`
- `PATCH /productos/{id}/restar-stock`: Restar stock a un producto.
  - Body: `RestarStock` (cantidad)
  - Response: `Producto`
- `DELETE /productos/{id}`: Eliminar un producto (soft delete).
  - Response: dict con mensaje
- `GET /productos/eliminados`: Obtener productos eliminados.
  - Response: list[dict]

## Autor
- **Nombre**: Omar David Valderrama Gutierrez
- **Código**: 67000516

