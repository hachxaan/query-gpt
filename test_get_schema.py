import psycopg2

def obtener_estructura_db():
    """Obtiene la estructura de la base de datos PostgreSQL, incluyendo las relaciones entre tablas."""
    query_tablas = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name in ('companies', 'credits', 'users')"
    query_columnas = lambda tabla: f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{tabla}'"
    query_relaciones = """
    SELECT
        tc.table_name, 
        kcu.column_name, 
        ccu.table_name AS foreign_table_name,
        ccu.column_name AS foreign_column_name 
    FROM 
        information_schema.table_constraints AS tc 
        JOIN information_schema.key_column_usage AS kcu
          ON tc.constraint_name = kcu.constraint_name
          AND tc.table_schema = kcu.table_schema
        JOIN information_schema.constraint_column_usage AS ccu
          ON ccu.constraint_name = tc.constraint_name
          AND ccu.table_schema = tc.table_schema
    WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_schema = 'public';
    """

    # Obtener nombres de tablas
    tablas = consultar_postgres(query_tablas)
    if tablas is None:
        return "No se pudo obtener la estructura de la base de datos."

    # Obtener relaciones entre tablas
    relaciones = consultar_postgres(query_relaciones)
    relaciones_dict = {}
    if relaciones:
        for rel in relaciones:
            tabla, columna, tabla_foranea, columna_foranea = rel
            if tabla not in relaciones_dict:
                relaciones_dict[tabla] = []
            relaciones_dict[tabla].append((columna, tabla_foranea, columna_foranea))

    estructura = {}
    for tabla in tablas:
        nombre_tabla = tabla[0]
        print(tabla)
        columnas = consultar_postgres(query_columnas(nombre_tabla))
        estructura[nombre_tabla] = {
            "columnas": columnas,
            "relaciones": relaciones_dict.get(nombre_tabla, [])
        }

    return estructura


def consultar_postgres(query):
    """Conecta a PostgreSQL y ejecuta una consulta."""
    try:
        # Conexión a la base de datos usando las credenciales proporcionadas
        conn = psycopg2.connect(
            host="localhost",
            user="devadmin",
            password="developtest",
            dbname="develop",
            port="5432"
        )

        # Ejecución de la consulta
        with conn.cursor() as cursor:
            cursor.execute(query)
            resultados = cursor.fetchall()
            return resultados

    except psycopg2.DatabaseError as e:
        print(f"Error de base de datos: {e}")
        return None
    finally:
        if conn:
            conn.close()


if __name__ == '__main__':
    data = obtener_estructura_db()
    print(data)
