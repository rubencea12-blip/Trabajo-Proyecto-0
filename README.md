\# Análisis de datos meteorológicos del SMN



Programa que lee los datos meteorológicos del SMN (Servicio Meteorológico Nacional) desde un archivo de texto, y calcula algunas estadísticas: cuántas ciudades hay, cuáles tienen datos faltantes, cuál es la más calurosa y la más fría, cuál tiene más viento y cuál menos, entre otras cosas.



\## Cómo ejecutarlo



python analisis\_smn.py datos/observaciones\_smn.txt



\## De dónde sacar el archivo de datos



1\. Entrar a https://www.smn.gob.ar/descarga-de-datos

2\. Descargar el archivo comprimido (.rar) de observaciones actuales

3\. Descomprimirlo con Winrar o 7-Zip

4\. Poner el .txt que queda dentro de la carpeta `datos/`, con el nombre `observaciones\_smn.txt`



\## Ejemplo de lo que muestra al ejecutarlo



Se leyeron 121 ciudades.

Ciudades con todos los datos completos: 25

Temperatura máxima: Rivadavia (28°C)

Temperatura mínima: Base Belgrano II (-28.6°C)

