# Análisis de datos meteorológicos del SMN

Programa que lee los datos meteorológicos del SMN (Servicio Meteorológico Nacional) desde un archivo de texto, y calcula algunas estadísticas: cuántas ciudades hay, cuáles tienen datos faltantes, cuál es la más calurosa y la más fría, cuál tiene más viento y cuál menos, entre otras cosas.

## Cómo ejecutarlo

python smn.py datos/observaciones_smn.txt

Si se pasa un archivo .json desde obs_json/, muestra las cantidades.

## De dónde sacar el archivo de datos

1. Entrar a https://smn.gob.ar
2. Descargar el archivo comprimido (.rar) de observaciones actuales
3. Descomprimirlo con Winrar o 7-Zip
4. Poner el .txt que queda dentro de la carpeta datos/, con el nombre observaciones_smn.txt

## Ejemplo sencillo de lo que muestra al ejecutarlo

Se leyeron 121 ciudades.
-Ciudades con todos los datos completos: 25
-Temperatura máxima: Rivadavia (28°C)
-Temperatura mínima: Base Belgrano II (-28.6°C)
