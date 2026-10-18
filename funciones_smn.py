import sys
import os
import json
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
    """Separa 'Norte  3' en direccion y velocidad."""
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
    """Junta fecha y hora en un solo datetime."""
    partes_fecha = fecha_texto.split("-")
    dia = int(partes_fecha[0])
    mes = MESES[partes_fecha[1].lower()]
    anio = int(partes_fecha[2])

    partes_hora = hora_texto.split(":")
    hora = int(partes_hora[0])
    minuto = int(partes_hora[1])

    return datetime.datetime(anio, mes, dia, hora, minuto)


def detectar_codificacion(ruta):
    """Devuelve utf-8 si el archivo se puede leer asi, sino latin-1."""
    with open(ruta, "rb") as archivo:
        contenido = archivo.read()
    try:
        contenido.decode("utf-8")
        return "utf-8"
    except UnicodeDecodeError:
        return "latin-1"


def leer_observaciones(ruta, codificacion=None):
    """Lee el txt del SMN y devuelve un diccionario {ciudad: datos}."""
    if codificacion is None:
        codificacion = detectar_codificacion(ruta)
    observaciones = {}
    lineas_invalidas = 0

    try:
        with open(ruta, "r", encoding=codificacion) as archivo:
            for linea in archivo:
                linea = linea.strip()
                if linea == "":
                    continue

                if linea.endswith("/"):
                    linea = linea[:-1].strip()

                campos = []
                for c in linea.split(";"):
                    campos.append(c.strip())

                if len(campos) != 10:
                    lineas_invalidas += 1
                    continue

                ciudad = campos[0]
                fecha_y_hora = parsear_fecha_hora(campos[1], campos[2])

                try:
                    temperatura = float(campos[5])
                except ValueError:
                    temperatura = None

                if campos[6].lower() == "no se calcula":
                    sensacion_termica = None
                else:
                    try:
                        sensacion_termica = float(campos[6])
                    except ValueError:
                        sensacion_termica = None

                try:
                    humedad = float(campos[7])
                except ValueError:
                    humedad = None

                direccion_viento, velocidad_viento = separar_viento(campos[8])

                try:
                    presion = float(campos[9])
                except ValueError:
                    presion = None

                observaciones[ciudad] = {
                    "fecha_y_hora": fecha_y_hora,
                    "condicion": campos[3],
                    "visibilidad": campos[4],
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
        print(f"Aviso: {lineas_invalidas} línea(s) mal formadas, ignoradas.")

    return observaciones


def cantidad_ciudades(observaciones):
    """Cantidad total de ciudades leidas."""
    return len(observaciones)


def cantidad_ciudades_completas(observaciones):
    """Cantidad de ciudades sin ningun dato faltante."""
    completas = 0
    for datos in observaciones.values():
        if datos["temperatura"] is None:
            continue
        if datos["sensacion_termica"] is None:
            continue
        if datos["humedad"] is None:
            continue
        if datos["velocidad_viento"] is None:
            continue
        if datos["presion"] is None:
            continue
        completas += 1
    return completas


def obtener_valor_del_par(par):
    """Devuelve el segundo elemento del par, para ordenar."""
    return par[1]


def top_n_ciudades(observaciones, campo, n, descendente=True):
    """Devuelve las n ciudades ordenadas segun el campo."""
    validas = []
    for ciudad, datos in observaciones.items():
        if datos[campo] is not None:
            validas.append((ciudad, datos[campo]))
    validas.sort(key=obtener_valor_del_par, reverse=descendente)
    return validas[:n]


def extremos(observaciones, campo, descendente=True):
    """Devuelve todas las ciudades empatadas en el maximo (o minimo)."""
    ordenadas = top_n_ciudades(observaciones, campo, len(observaciones), descendente)
    if len(ordenadas) == 0:
        return []
    mejor_valor = ordenadas[0][1]
    resultado = []
    for par in ordenadas:
        if par[1] == mejor_valor:
            resultado.append(par)
    return resultado


def columnas_ausentes(observaciones):
    """Devuelve los campos esperados que no aparecen en ninguna observacion."""
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
    """Devuelve {campo: [ciudades]} con las estaciones donde falta el dato."""
    campos_a_revisar = [
        "temperatura", "sensacion_termica", "humedad",
        "direccion_viento", "velocidad_viento", "presion"
    ]
    faltantes = {}
    for campo in campos_a_revisar:
        faltantes[campo] = []

    for ciudad, datos in observaciones.items():
        for campo in campos_a_revisar:
            if datos.get(campo) is None:
                faltantes[campo].append(ciudad)

    return faltantes


def horarios_reportados(observaciones):
    """Lista de horarios HH:MM sin repetir y ordenados."""
    horarios = []
    for datos in observaciones.values():
        hora_texto = datos["fecha_y_hora"].strftime("%H:%M")
        if hora_texto not in horarios:
            horarios.append(hora_texto)
    horarios.sort()
    return horarios


def mostrar_resumen(observaciones):
    """Imprime el resumen con todas las caracteristicas."""
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

    print(f"\nTemperatura máxima: {extremos(observaciones, 'temperatura')}")
    print(f"Temperatura mínima: {extremos(observaciones, 'temperatura', descendente=False)}")
    print(f"Viento máximo: {extremos(observaciones, 'velocidad_viento')}")
    print(f"Viento mínimo: {extremos(observaciones, 'velocidad_viento', descendente=False)}")

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


def observaciones_a_json(observaciones):
    """Pasa la fecha de datetime a texto, porque json no guarda fechas."""
    resultado = {}
    for ciudad, datos in observaciones.items():
        copia = dict(datos)
        copia["fecha_y_hora"] = datos["fecha_y_hora"].isoformat(timespec="minutes")
        resultado[ciudad] = copia
    return resultado


def mostrar_cantidades(observaciones):
    """Imprime la cantidad de ciudades y las informadas."""
    print("Ciudades en el archivo:", cantidad_ciudades(observaciones))
    print("Ciudades informadas:", cantidad_ciudades_completas(observaciones))


def procesar_txt(ruta):
    """Convierte un txt del SMN a json dentro de obs_json."""
    print("archivo del SMN, convirtiendo a json...")

    try:
        codificacion = detectar_codificacion(ruta)
    except FileNotFoundError:
        print("no se encontró el archivo, no se completó")
        return
    print(f"codificación detectada: {codificacion}")

    observaciones = leer_observaciones(ruta, codificacion)
    print("lectura completada")

    if not os.path.exists("obs_json"):
        print("el directorio obs_json no existe, creándolo...")
        try:
            os.makedirs("obs_json")
            print("directorio creado")
        except OSError:
            print("no se pudo crear el directorio, no se completó")
            return

    nombre = os.path.splitext(os.path.basename(ruta))[0] + ".json"
    ruta_json = os.path.join("obs_json", nombre)

    print(f"guardando {ruta_json}...")
    try:
        with open(ruta_json, "w", encoding="utf-8") as archivo:
            json.dump(observaciones_a_json(observaciones), archivo,
                      ensure_ascii=False, indent=2)
        print("archivo json guardado")
    except OSError:
        print("no se pudo guardar el archivo json, no se completó")
        return

    mostrar_cantidades(observaciones)


def procesar_json(ruta):
    """Lee un json e imprime las cantidades de ciudades."""
    print("archivo json, leyendo...")
    try:
        with open(ruta, "r", encoding="utf-8") as archivo:
            observaciones = json.load(archivo)
        print("lectura completada")
    except FileNotFoundError:
        print("no se encontró el archivo, no se completó")
        return
    except ValueError:
        print("el json está mal formado, no se completó")
        return

    mostrar_cantidades(observaciones)


def contar_archivos(carpeta, extension):
    """Cuenta los archivos con esa extension en la carpeta."""
    if not os.path.isdir(carpeta):
        return 0
    cantidad = 0
    for nombre in os.listdir(carpeta):
        if nombre.endswith(extension):
            cantidad += 1
    return cantidad


def main(argumentos):
    """Decide que hacer segun los parametros que se pasaron."""
    if len(argumentos) > 2:
        print("Se pasó más de un parámetro. Uso: python smn.py <ruta_archivo>")
        return

    if len(argumentos) == 1:
        print("No se indicó ningún archivo. Uso: python smn.py <ruta_archivo>")
        print("Archivos .txt en datos/:", contar_archivos("datos", ".txt"))
        print("Archivos .json en obs_json/:", contar_archivos("obs_json", ".json"))
        return

    ruta = argumentos[1]
    if ruta.endswith(".txt"):
        procesar_txt(ruta)
    elif ruta.endswith(".json"):
        procesar_json(ruta)
    else:
        print("Extensión no soportada, se esperaba un archivo .txt o .json")