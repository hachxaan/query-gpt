import psycopg2


def obtener_estructura_db():
    """Obtiene la estructura de la base de datos PostgreSQL."""
    query_tablas = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
    query_columnas = lambda tabla: f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{tabla}'"

    # Obtener nombres de tablas
    tablas = consultar_postgres(query_tablas)
    if tablas is None:
        return "No se pudo obtener la estructura de la base de datos."

    estructura = {}
    for tabla in tablas:
        # print(tabla)
        # Obtener detalles de cada tabla
        nombre_tabla = tabla[0]
        columnas = consultar_postgres(query_columnas(nombre_tabla))
        estructura[nombre_tabla] = columnas

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