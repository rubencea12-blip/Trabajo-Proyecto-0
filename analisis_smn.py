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

                # saca el " /" final si aparece (artefacto del archivo)
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


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python analisis_smn.py <ruta_archivo>")
        sys.exit(1)

    ruta = sys.argv[1]
    datos = leer_observaciones(ruta)
    print(f"Se leyeron {len(datos)} ciudades.")