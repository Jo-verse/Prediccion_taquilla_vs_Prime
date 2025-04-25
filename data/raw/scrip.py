import pandas as pd

ruta_archivo = '../Prediccion_taquilla_vs_Prime/data/raw/title.basics.tsv.gz'
ruta_guardado = '../Prediccion_taquilla_vs_Prime/data/interim/lista_ids_imdb.txt'

try:
    df = pd.read_csv(ruta_archivo, sep='\t', compression='gzip', low_memory=False)
    peliculas_df = df[df['titleType'] == 'movie']
    lista_ids_imdb = peliculas_df['tconst'].tolist()
    print(f"Se encontraron {len(lista_ids_imdb)} películas.")

    # Guardar la lista de IDs en un archivo de texto, un ID por línea
    with open(ruta_guardado, 'w') as f:
        for imdb_id in lista_ids_imdb:
            f.write(f"{imdb_id}\n")

    print(f"La lista de IDs de IMDb se ha guardado en: {ruta_guardado}")

except Exception as e:
    print(f"Error al leer o guardar el archivo: {e}")