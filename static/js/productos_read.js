document.addEventListener("DOMContentLoaded", () => {
    const productosList = document.getElementById('productos-list');
    const filterForm = document.querySelector('form');

    async function fetchProductos(params = {}) {
        const url = new URL(window.location.origin + '/productos/');
        Object.entries(params).forEach(([key, value]) => {
            if (value !== '' && value !== null && value !== undefined) {
                url.searchParams.append(key, value);
            }
        });
        try {
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`Error fetching productos: ${response.statusText}`);
            }
            const productos = await response.json();
            renderProductos(productos);
        } catch (error) {
            productosList.innerHTML = `<p class="error-message">No se pudieron cargar los productos: ${error.message}</p>`;
        }
    }

    function renderProductos(productos) {
        if (productos.length === 0) {
            productosList.innerHTML = '<p>No se encontraron productos.</p>';
            return;
        }
        productosList.innerHTML = '';
        productos.forEach(producto => {
            const productoDiv = document.createElement('div');
            productoDiv.classList.add('result-item');

            productoDiv.innerHTML = `
                <h3>${producto.nombre} ${producto.activo ? '' : '(Inactivo)'}</h3>
                <img src="${producto.media_url || '/static/img/no-image.png'}" alt="${producto.nombre}" style="max-width:150px; max-height:150px;" />
                <p><strong>Descripción:</strong> ${producto.descripcion || 'N/A'}</p>
                <p><strong>Precio:</strong> $${producto.precio.toFixed(2)}</p>
                <p><strong>Stock:</strong> ${producto.stock}</p>
                <p><strong>Categoría:</strong> ${producto.categoria || 'N/A'}</p>
            `;
            productosList.appendChild(productoDiv);
        });
    }

    filterForm.addEventListener('submit', event => {
        event.preventDefault();
        const formData = new FormData(filterForm);
        const params = {};
        formData.forEach((value, key) => {
            params[key] = value;
        });
        fetchProductos(params);
    });

    // Initial load without filters
    fetchProductos();
});
