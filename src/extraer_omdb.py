import csv
import requests
import time
from dotenv import load_dotenv
import os

# Cargar las variables de entorno desde el archivo .env
dotenv_path = '../Prediccion_taquilla_vs_Prime/.env'
load_dotenv(dotenv_path=dotenv_path)
omdb_api_key = os.getenv("OMDb_API_KEY")

if not omdb_api_key:
    print("Error: No se encontró la clave API de OMDb en el archivo .env")
    exit()

def obtener_info_omdb(imdb_id, omdb_api_key):
    # (La función obtener_info_omdb que ya definimos)
    url = f"http://www.omdbapi.com/?i={imdb_id}&apikey={omdb_api_key}&plot=short&r=json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data.get('Response') == 'True':
            return {
                'Genre': data.get('Genre', 'N/A'),
                'Director': data.get('Director', 'N/A'),
                'Actors': data.get('Actors', 'N/A'),
                'Plot': data.get('Plot', 'N/A')
            }
        else:
            print(f"Error al obtener información para el ID {imdb_id}: {data.get('Error')}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión al API de OMDb para el ID {imdb_id}: {e}")
        return None
    except ValueError:
        print(f"Error al decodificar la respuesta JSON para el ID {imdb_id}")
        return None

def enriquecer_peliculas_csv(archivo_entrada="peliculas_imdb_completo.csv", archivo_salida="../Prediccion_taquilla_vs_Prime/data/raw/peliculas_enriquecidas.csv"):
    """
    Lee un archivo CSV con información de películas (incluyendo el ID de IMDb) y
    añade información de género, director, actores y sinopsis desde la API de OMDb.

    Args:
        archivo_entrada (str): El nombre del archivo CSV de entrada.
        archivo_salida (str): El nombre del archivo CSV de salida enriquecido.
    """
    with open(archivo_entrada, 'r', encoding='utf-8') as infile, \
            open(archivo_salida, 'w', encoding='utf-8', newline='') as outfile:

        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ['Género', 'Director', 'Actores', 'Sinopsis']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        writer.writeheader()

        for row in reader:
            imdb_id = row.get('ID')
            if imdb_id:
                omdb_info = obtener_info_omdb(imdb_id, omdb_api_key)
                if omdb_info:
                    row['Género'] = omdb_info.get('Genre', 'N/A')
                    row['Director'] = omdb_info.get('Director', 'N/A')
                    row['Actores'] = omdb_info.get('Actors', 'N/A')
                    row['Sinopsis'] = omdb_info.get('Plot', 'N/A')
                else:
                    row['Género'] = 'N/A'
                    row['Director'] = 'N/A'
                    row['Actores'] = 'N/A'
                    row['Sinopsis'] = 'N/A'
                time.sleep(1)  # Respetar el límite de la API de OMDb
            writer.writerow(row)

    print(f"Se ha creado el archivo enriquecido: {archivo_salida}")

if __name__ == "__main__":
    enriquecer_peliculas_csv()