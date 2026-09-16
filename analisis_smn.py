import sys

CAMPOS_ESPERADOS = [
    "ciudad", "fecha", "hora", "condicion", "visibilidad",
    "temperatura", "sensacion_termica", "humedad",
    "viento", "presion"
]


def separar_viento(campo_viento):
    """Convierte 'Norte  3' en ('Norte', 3.0). Contempla 'Calma'."""
    campo_viento = campo_viento.strip()
    if campo_viento.lower() == "calma":
        return ("Calma", 0.0)

    partes = campo_viento.split()
    velocidad = partes[-1]
    direccion = " ".join(partes[:-1])

    try:
        velocidad = float(velocidad)
    except ValueError:
        velocidad = None

    return (direccion, velocidad)


def leer_observaciones(ruta):
    """Lee el archivo de observaciones del SMN y devuelve un diccionario
    {ciudad: datos}."""
    observaciones = {}
    lineas_invalidas = 0

    try:
        with open(ruta, "r", encoding="latin-1") as archivo:
            for numero_linea, linea in enumerate(archivo, start=1):
                linea = linea.strip()
                if not linea:
                    continue

                if linea.endswith("/"):
                    linea = linea[:-1].strip()

                campos = [c.strip() for c in linea.split(";")]

                if len(campos) != 10:
                    lineas_invalidas += 1
                    continue

                ciudad = campos[0]
                fecha = campos[1]
                hora = campos[2]
                condicion = campos[3]
                visibilidad = campos[4]
                temp_texto = campos[5]
                sensacion_texto = campos[6]
                humedad_texto = campos[7]
                viento_texto = campos[8]
                presion_texto = campos[9]

                try:
                    temperatura = float(temp_texto)
                except ValueError:
                    temperatura = None

                if sensacion_texto.lower() == "no se calcula":
                    sensacion_termica = None
                else:
                    try:
                        sensacion_termica = float(sensacion_texto)
                    except ValueError:
                        sensacion_termica = None

                try:
                    humedad = float(humedad_texto)
                except ValueError:
                    humedad = None

                direccion_viento, velocidad_viento = separar_viento(viento_texto)

                try:
                    presion = float(presion_texto)
                except ValueError:
                    presion = None

                observaciones[ciudad] = {
                    "fecha": fecha,
                    "hora": hora,
                    "condicion": condicion,
                    "visibilidad": visibilidad,
                    "temperatura": temperatura,
                    "sensacion_termica": sensacion_termica,
                    "humedad": humedad,
                    "direccion_viento": direccion_viento,
                    "velocidad_viento": velocidad_viento,
                    "presion": presion,
                }

    except FileNotFoundError:
        print(f"Error: no se encontró el archivo '{ruta}'")
        sys.exit(1)

    if lineas_invalidas > 0:
        print(f"Aviso: se encontraron {lineas_invalidas} línea(s) mal formadas, ignoradas.")

    return observaciones


def cantidad_ciudades(observaciones):
    """Devuelve la cantidad total de ciudades leídas."""
    return len(observaciones)


def cantidad_ciudades_completas(observaciones):
    """Devuelve la cantidad de ciudades sin ningún dato faltante."""
    completas = 0
    for datos in observaciones.values():
        if datos["temperatura"] is not None and \
           datos["sensacion_termica"] is not None and \
           datos["humedad"] is not None and \
           datos["velocidad_viento"] is not None and \
           datos["presion"] is not None:
            completas += 1
    return completas


def ciudad_temperatura_maxima(observaciones):
    """Devuelve la ciudad (o ciudades) con la temperatura más alta."""
    validas = {c: d for c, d in observaciones.items() if d["temperatura"] is not None}
    if not validas:
        return []
    maxima = max(d["temperatura"] for d in validas.values())
    return [c for c, d in validas.items() if d["temperatura"] == maxima]


def ciudad_temperatura_minima(observaciones):
    """Devuelve la ciudad (o ciudades) con la temperatura más baja."""
    validas = {c: d for c, d in observaciones.items() if d["temperatura"] is not None}
    if not validas:
        return []
    minima = min(d["temperatura"] for d in validas.values())
    return [c for c, d in validas.items() if d["temperatura"] == minima]


def ciudad_viento_maximo(observaciones):
    """Devuelve la ciudad (o ciudades) con la velocidad de viento más alta."""
    validas = {c: d for c, d in observaciones.items() if d["velocidad_viento"] is not None}
    if not validas:
        return []
    maxima = max(d["velocidad_viento"] for d in validas.values())
    return [c for c, d in validas.items() if d["velocidad_viento"] == maxima]


def ciudad_viento_minimo(observaciones):
    """Devuelve la ciudad (o ciudades) con la velocidad de viento más baja."""
    validas = {c: d for c, d in observaciones.items() if d["velocidad_viento"] is not None}
    if not validas:
        return []
    minima = min(d["velocidad_viento"] for d in validas.values())
    return [c for c, d in validas.items() if d["velocidad_viento"] == minima]


def top_n_ciudades(observaciones, campo, n, descendente=True):
    """Devuelve las n ciudades ordenadas según 'campo', de mayor a menor
    (o al revés si descendente=False). Reutilizable para temperatura o viento."""
    validas = [(c, d[campo]) for c, d in observaciones.items() if d[campo] is not None]
    validas.sort(key=lambda par: par[1], reverse=descendente)
    return validas[:n]


def columnas_ausentes(observaciones):
    """Devuelve el conjunto de campos esperados que no aparecen en ninguna
    observación leída."""
    campos_presentes = set()
    for datos in observaciones.values():
        campos_presentes.update(datos.keys())

    esperados = set(CAMPOS_ESPERADOS[1:])
    equivalencias = {
        "viento": {"direccion_viento", "velocidad_viento"}
    }

    faltantes = set()
    for campo in esperados:
        if campo in equivalencias:
            if not equivalencias[campo].issubset(campos_presentes):
                faltantes.add(campo)
        elif campo not in campos_presentes:
            faltantes.add(campo)

    return faltantes


def datos_faltantes_por_campo(observaciones):
    """Devuelve un diccionario {campo: [ciudades]} con el listado de
    estaciones donde ese campo vino faltante (None)."""
    campos_a_revisar = [
        "temperatura", "sensacion_termica", "humedad",
        "direccion_viento", "velocidad_viento", "presion"
    ]
    faltantes = {campo: [] for campo in campos_a_revisar}

    for ciudad, datos in observaciones.items():
        for campo in campos_a_revisar:
            if datos.get(campo) is None:
                faltantes[campo].append(ciudad)

    return faltantes


def mostrar_resumen(observaciones):
    """Imprime por pantalla un resumen con todas las características
    calculadas sobre las observaciones."""
    print("=" * 50)
    print("RESUMEN DE OBSERVACIONES METEOROLÓGICAS - SMN")
    print("=" * 50)

    print(f"\nCantidad total de ciudades leídas: {cantidad_ciudades(observaciones)}")
    print(f"Ciudades con todos los datos completos: {cantidad_ciudades_completas(observaciones)}")

    ausentes = columnas_ausentes(observaciones)
    if ausentes:
        print(f"\nColumnas esperadas ausentes en el archivo: {ausentes}")
    else:
        print("\nNo hay columnas esperadas ausentes.")

    print("\nDatos faltantes por campo:")
    faltantes = datos_faltantes_por_campo(observaciones)
    for campo, ciudades in faltantes.items():
        print(f"  - {campo}: {len(ciudades)} ciudad(es)")

    print(f"\nTemperatura máxima: {ciudad_temperatura_maxima(observaciones)}")
    print(f"Temperatura mínima: {ciudad_temperatura_minima(observaciones)}")
    print(f"Viento máximo: {ciudad_viento_maximo(observaciones)}")
    print(f"Viento mínimo: {ciudad_viento_minimo(observaciones)}")

    print("\nTop 5 ciudades más cálidas:")
    for ciudad, temp in top_n_ciudades(observaciones, "temperatura", 5):
        print(f"  {ciudad}: {temp}°C")

    print("\nTop 5 ciudades más frías:")
    for ciudad, temp in top_n_ciudades(observaciones, "temperatura", 5, descendente=False):
        print(f"  {ciudad}: {temp}°C")

    print("\nTop 5 ciudades con más viento:")
    for ciudad, vel in top_n_ciudades(observaciones, "velocidad_viento", 5):
        print(f"  {ciudad}: {vel} km/h")

    print("\nTop 5 ciudades con menos viento:")
    for ciudad, vel in top_n_ciudades(observaciones, "velocidad_viento", 5, descendente=False):
        print(f"  {ciudad}: {vel} km/h")

    print("\n" + "=" * 50)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python analisis_smn.py <ruta_archivo>")
        sys.exit(1)

    ruta = sys.argv[1]
    datos = leer_observaciones(ruta)
    mostrar_resumen(datos)