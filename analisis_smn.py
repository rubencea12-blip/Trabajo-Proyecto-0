import sys
import datetime

CAMPOS_ESPERADOS = [
    "ciudad", "fecha_y_hora", "condicion", "visibilidad",
    "temperatura", "sensacion_termica", "humedad",
    "viento", "presion"
]

MESES = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4,
    "mayo": 5, "junio": 6, "julio": 7, "agosto": 8,
    "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12
}


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


def parsear_fecha_hora(fecha_texto, hora_texto):
    """Convierte una fecha 'dd-mes-aaaa' (en español) y una hora 'HH:MM'
    en un único objeto datetime.datetime."""
    partes_fecha = fecha_texto.split("-")
    dia = int(partes_fecha[0])
    mes_texto = partes_fecha[1].lower()
    anio = int(partes_fecha[2])
    mes = MESES[mes_texto]

    partes_hora = hora_texto.split(":")
    hora = int(partes_hora[0])
    minuto = int(partes_hora[1])

    return datetime.datetime(anio, mes, dia, hora, minuto)


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
                fecha_texto = campos[1]
                hora_texto = campos[2]
                condicion = campos[3]
                visibilidad = campos[4]
                temp_texto = campos[5]
                sensacion_texto = campos[6]
                humedad_texto = campos[7]
                viento_texto = campos[8]
                presion_texto = campos[9]

                fecha_y_hora = parsear_fecha_hora(fecha_texto, hora_texto)

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
                    "fecha_y_hora": fecha_y_hora,
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


def obtener_valor_del_par(par):
    """Función auxiliar para ordenar: devuelve el segundo elemento del par."""
    return par[1]


def top_n_ciudades(observaciones, campo, n, descendente=True):
    """Devuelve las n ciudades ordenadas según 'campo', de mayor a menor
    (o al revés si descendente=False). Reutilizable para temperatura o viento."""
    validas = [(c, d[campo]) for c, d in observaciones.items() if d[campo] is not None]
    validas.sort(key=obtener_valor_del_par, reverse=descendente)
    return validas[:n]


def columnas_ausentes(observaciones):
    """Devuelve la lista de campos esperados que no aparecen en ninguna
    observación leída."""
    campos_presentes = []
    for datos in observaciones.values():
        for campo in datos.keys():
            if campo not in campos_presentes:
                campos_presentes.append(campo)

    faltantes = []
    for campo in CAMPOS_ESPERADOS[1:]:
        if campo == "viento":
            if "direccion_viento" not in campos_presentes or "velocidad_viento" not in campos_presentes:
                faltantes.append(campo)
        elif campo not in campos_presentes:
            faltantes.append(campo)

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


def horarios_reportados(observaciones):
    """Devuelve una lista de los horarios a los que las estaciones
    reportaron la observación, en formato 'HH:MM', sin repetir y
    ordenados de menor a mayor."""
    horarios = []
    for datos in observaciones.values():
        hora_texto = datos["fecha_y_hora"].strftime("%H:%M")
        if hora_texto not in horarios:
            horarios.append(hora_texto)
    horarios.sort()
    return horarios


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

    print(f"\nHorarios reportados: {horarios_reportados(observaciones)}")

    temp_max = top_n_ciudades(observaciones, "temperatura", 1)
    temp_min = top_n_ciudades(observaciones, "temperatura", 1, descendente=False)
    viento_max = top_n_ciudades(observaciones, "velocidad_viento", 1)
    viento_min = top_n_ciudades(observaciones, "velocidad_viento", 1, descendente=False)

    print(f"\nTemperatura máxima: {temp_max}")
    print(f"Temperatura mínima: {temp_min}")
    print(f"Viento máximo: {viento_max}")
    print(f"Viento mínimo: {viento_min}")

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