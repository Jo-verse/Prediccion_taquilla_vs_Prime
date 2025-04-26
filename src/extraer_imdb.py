from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException
import time
from bs4 import BeautifulSoup
import csv  # Importar la librería csv

def extraer_info_imdb_ordenado(url_base, archivo_salida="../Prediccion_taquilla_vs_Prime/data/raw/peliculas_imdb_completo.csv", max_clicks=200, num_scrolls=3):
    """
    Extrae ID, nombre, año, duración y Metascore de películas de una página de búsqueda de IMDb,
    ordenados alfabéticamente por nombre y guarda los resultados en un archivo CSV.

    Args:
        url_base (str): URL de la página de búsqueda de IMDb.
        archivo_salida (str, opcional): Nombre del archivo CSV para guardar la información.
            Por defecto "peliculas_imdb_completo.csv".
        max_clicks (int, opcional): Máximo número de clics en el botón "Cargar más".
            Por defecto 200.
        num_scrolls (int): Número de scrolls a realizar antes de hacer clic en "Cargar más"
    """
    driver = webdriver.Chrome()
    driver.get(url_base)
    driver.maximize_window()

    try:
        # Intentar aceptar las cookies
        try:
            accept_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//button[text()='Accept']"))
            )
            accept_button.click()
            print("Se aceptaron las cookies.")
        except TimeoutException:
            print("La ventana de gestión de cookies no apareció o no se pudo hacer clic en 'Aceptar'.")

        time.sleep(2)

        peliculas_info = {}

        def extraer_info_pagina(html_source):
            if html_source is None:
                print("Error: Recibido html_source None. Ignorando esta iteración.")
                return {}
            soup = BeautifulSoup(html_source, 'html.parser')
            lista_peliculas = soup.select('.ipc-metadata-list-summary-item')
            nuevas_peliculas = {}
            for pelicula in lista_peliculas:
                enlace_titulo = pelicula.select_one('a.ipc-title-link-wrapper')
                titulo_elemento = pelicula.select_one('.ipc-title__text')
                metadata_contenedor = pelicula.select_one('.sc-5179a348-6')  # Contenedor del año y duración
                metascore_elemento = pelicula.select_one('.metacritic-score-box')

                año_publicacion = "N/A"
                duracion = "N/A"

                if metadata_contenedor:
                    año_elemento = metadata_contenedor.select_one('.sc-5179a348-7:nth-child(1)')  # El primer span suele ser el año
                    duracion_elemento = metadata_contenedor.select_one('.sc-5179a348-7:nth-child(2)')  # El segundo span suele ser la duración
                    if año_elemento:
                        año_publicacion = año_elemento.text.strip()
                    if duracion_elemento:
                        duracion = duracion_elemento.text.strip()

                if enlace_titulo and enlace_titulo.get('href') and titulo_elemento:
                    href = enlace_titulo['href']
                    imdb_id = href.split('/title/')[1].split('/')[0]
                    nombre_pelicula = titulo_elemento.text
                    metascore = metascore_elemento.text.strip() if metascore_elemento else "N/A"

                    if imdb_id.startswith('tt'):
                        nuevas_peliculas[imdb_id] = {'nombre': nombre_pelicula, 'año': año_publicacion, 'duracion': duracion, 'metascore': metascore}
            return nuevas_peliculas

        # Extraer información de la página inicial
        peliculas_info.update(extraer_info_pagina(driver.page_source))
        print(f"Películas iniciales encontradas: {len(peliculas_info)}")

        click_count = 0
        while click_count < max_clicks:
            for _ in range(num_scrolls):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)

            try:
                load_more_button = WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, ".ipc-see-more__button"))
                )
                try:
                    load_more_button.click()
                except ElementClickInterceptedException:
                    print("ElementClickInterceptedException: Intentando hacer clic con JavaScript.")
                    driver.execute_script("arguments[0].click();", load_more_button)
                except Exception as e:
                    print(f"Error inesperado al hacer clic: {e}")
                    break

                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '.ipc-metadata-list-summary-item:nth-child(51)'))
                )
                time.sleep(2)

            except (NoSuchElementException, TimeoutException):
                print("El botón '50 más' ya no está presente o no se pudo hacer clic, o los nuevos resultados no cargaron.")
                break
            except Exception as e:
                print(f"Ocurrió un error general: {e}")
                break

            nuevas_peliculas_info = extraer_info_pagina(driver.page_source)
            peliculas_info.update(nuevas_peliculas_info)
            print(f"Películas encontradas después de scroll/clic {click_count}: {len(peliculas_info)} (+{len(nuevas_peliculas_info)})")
            click_count += 1

        # Guardar la información de las películas en un archivo CSV ordenado por nombre
        with open(archivo_salida, "w", encoding="utf-8", newline='') as csvfile:
            fieldnames = ['ID', 'Nombre', 'Año', 'Duración', 'Metascore']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for imdb_id, info in sorted(peliculas_info.items(), key=lambda item: item[1]['nombre']):
                writer.writerow({
                    'ID': imdb_id,
                    'Nombre': info['nombre'],
                    'Año': info['año'],
                    'Duración': info['duracion'],
                    'Metascore': info['metascore']
                })
        print(f"Se guardó la información de {len(peliculas_info)} películas en {archivo_salida} (CSV)")

    except Exception as e:
        print(f"Ocurrió un error general: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    url_imdb_busqueda = "https://www.imdb.com/search/title/?title_type=feature&release_date=2000-01-01,2025-12-31"
    extraer_info_imdb_ordenado(url_imdb_busqueda)