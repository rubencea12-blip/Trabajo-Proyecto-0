import sys
from funciones_smn import leer_observaciones, mostrar_resumen

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python analisis_smn.py <ruta_archivo>")
        sys.exit(1)
    datos = leer_observaciones(sys.argv[1])
    mostrar_resumen(datos)