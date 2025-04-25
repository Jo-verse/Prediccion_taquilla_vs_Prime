from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException
import time
from bs4 import BeautifulSoup

def extraer_ids_imdb_ordenado(url_base, archivo_salida="ids_imdb_completo.txt", max_clicks=200, num_scrolls=3):
    """
    Extrae IDs de IMDb de una página de búsqueda, ordenados alfabéticamente,
    optimizando el scroll y la espera de carga de la página.

    Args:
        url_base (str): URL de la página de búsqueda de IMDb.
        archivo_salida (str, opcional): Nombre del archivo para guardar los IDs.
            Por defecto "ids_imdb_completo.txt".
        max_clicks (int, opcional): Máximo número de clics en el botón "Cargar más".
            Por defecto 200.
        num_scrolls (int): Número de scrolls a realizar antes de hacer clic en "Cargar más"
    """
    driver = webdriver.Chrome()
    driver.get(url_base)
    driver.maximize_window()  # Maximiza la ventana para asegurar que el botón sea visible

    try:
        # Intentar aceptar las cookies si la ventana aparece
        try:
            accept_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//button[text()='Accept']"))
            )
            accept_button.click()
            print("Se aceptaron las cookies.")
        except TimeoutException:
            print("La ventana de gestión de cookies no apareció o no se pudo hacer clic en 'Aceptar'.")

        time.sleep(2)  # Espera corta para que la página inicial cargue

        ids_imdb = set()

        # Extraer IDs de la página inicial
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        lista_peliculas = soup.select('.ipc-metadata-list-summary-item')
        nuevos_ids = set()
        for pelicula in lista_peliculas:
            enlace_titulo = pelicula.select_one('a.ipc-title-link-wrapper')
            if enlace_titulo and enlace_titulo.get('href'):
                href = enlace_titulo['href']
                imdb_id = href.split('/title/')[1].split('/')[0]
                if imdb_id.startswith('tt'):
                    nuevos_ids.add(imdb_id)
        ids_imdb.update(nuevos_ids)
        print(f"IDs iniciales encontrados: {len(ids_imdb)}")

        click_count = 0
        while click_count < max_clicks:
            # Scroll un poco antes de buscar elementos
            for _ in range(num_scrolls):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)  # Espera un poco después de cada scroll

            try:
                # Esperar a que el botón "50 más" esté clickable, usando el selector proporcionado
                load_more_button = WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, ".ipc-see-more__button"))
                )
                # Intenta hacer clic, y si falla por estar interceptado, intenta con JavaScript
                try:
                    load_more_button.click()
                except ElementClickInterceptedException:
                    print("ElementClickInterceptedException: Intentando hacer clic con JavaScript.")
                    driver.execute_script("arguments[0].click();", load_more_button)
                except Exception as e:
                    print(f"Error inesperado al hacer clic: {e}")
                    break

                # Esperar a que los nuevos resultados estén presentes (cambio importante)
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '.ipc-metadata-list-summary-item:nth-child(51)'))
                )
                time.sleep(2)

            except (NoSuchElementException, TimeoutException):
                print("El botón '50 más' ya no está presente o no se pudo hacer clic, o los nuevos resultados no cargaron.")
                break  # Salir del bucle si no hay más botón o no se puede clicar
            except Exception as e:
                print(f"Ocurrió un error general: {e}")
                break

            # Extraer IDs de la página actual
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            lista_peliculas = soup.select('.ipc-metadata-list-summary-item')
            nuevos_ids = set()
            for pelicula in lista_peliculas:
                enlace_titulo = pelicula.select_one('a.ipc-title-link-wrapper')
                if enlace_titulo and enlace_titulo.get('href'):
                    href = enlace_titulo['href']
                    imdb_id = href.split('/title/')[1].split('/')[0]
                    if imdb_id.startswith('tt'):
                        nuevos_ids.add(imdb_id)

            ids_imdb.update(nuevos_ids)
            print(f"IDs encontrados después de scroll/clic {click_count}: {len(ids_imdb)} (+{len(nuevos_ids)})")
            click_count += 1

        # Guardar los IDs ordenados en el archivo
        with open(archivo_salida, "w") as f:
            for imdb_id in sorted(list(ids_imdb)):
                f.write(f"{imdb_id}\n")
        print(f"Se guardaron {len(ids_imdb)} IDs de IMDb en {archivo_salida}")

    except Exception as e:
        print(f"Ocurrió un error general: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    url_imdb_busqueda = "https://www.imdb.com/search/title/?title_type=feature&release_date=2000-01-01,2025-12-31"
    extraer_ids_imdb_ordenado(url_imdb_busqueda)
