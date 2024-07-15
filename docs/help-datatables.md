# DataTables Configuración - Ayuda

## Opciones de Configuración de DataTables

DataTables es una poderosa herramienta para crear tablas interactivas y personalizables. A continuación se describen las opciones que puedes pedir al modelo para configurar tu tabla:

### 1. Procesamiento de Datos

- **`processing`**: Muestra un indicador de procesamiento mientras se carga la tabla.
  - **Ejemplo**: "Activa el procesamiento de datos."

### 2. Paginación y Número de Registros

- **`pageLength`**: Número de filas por página.
  - **Ejemplo**: "Establece 10 filas por página."
- **`lengthMenu`**: Opciones para el selector de número de filas por página.
  - **Ejemplo**: "Configura el menú de longitud de página a 5, 10, 25, 50, 100."

### 3. Ordenamiento de Columnas

- **`order`**: Define el orden inicial de la tabla.
  - **Ejemplo**: "Ordena por la columna de apellidos de forma ascendente."

### 4. Búsqueda y Filtrado

- **`searching`**: Habilita la barra de búsqueda global.
  - **Ejemplo**: "Habilita la búsqueda en la tabla."

### 5. Información de la Tabla

- **`info`**: Muestra información sobre la tabla.
  - **Ejemplo**: "Muestra información sobre el número de registros."

### 6. Paginación

- **`paging`**: Habilita la paginación.
  - **Ejemplo**: "Activa la paginación en la tabla."

### 7. Tabla Responsiva

- **`responsive`**: Habilita la tabla responsiva.
  - **Ejemplo**: "Haz la tabla responsiva."

### 8. Textos Personalizados

- **`language`**: Configura textos personalizados para los elementos de la tabla.
  - **Ejemplo**:
    - "Cambia el texto del menú de longitud a 'Mostrar _MENU_ registros por página'."
    - "Establece el mensaje de 'No se encontraron resultados'."
    - "Configura el texto de paginación a 'Primero', 'Último', 'Siguiente', 'Anterior'."

### Ejemplo de Configuración Completa

A continuación se muestra un ejemplo completo de cómo se vería la configuración de DataTables utilizando las opciones anteriores:

```javascript
$('#personTable').DataTable({
    "processing": true,
    "pageLength": 10,
    "lengthMenu": [5, 10, 25, 50, 100],
    "order": [[1, 'asc']],
    "searching": true,
    "paging": true,
    "info": true,
    "responsive": true,
    "language": {
        "lengthMenu": "Mostrar _MENU_ registros por página",
        "zeroRecords": "No se encontraron resultados",
        "info": "Mostrando página _PAGE_ de _PAGES_",
        "infoEmpty": "No hay registros disponibles",
        "infoFiltered": "(filtrado de _MAX_ registros en total)",
        "search": "Buscar:",
        "paginate": {
            "first": "Primero",
            "last": "Último",
            "next": "Siguiente",
            "previous": "Anterior"
        }
    }
});
