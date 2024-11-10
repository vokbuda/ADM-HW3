import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

# Configurazione del driver
options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# Usa il percorso assoluto per ChromeDriver
service = Service('/Users/fabrizioferrara/Desktop/Progetti DataScience/ADM/michelin_scraper/chromedriver')
driver = webdriver.Chrome(service=service, options=options)

# Percorso del file con gli URL e della cartella di destinazione per gli HTML
url_file = "/Users/fabrizioferrara/Desktop/michelin_restaurants_urls.txt"
output_folder = "/Users/fabrizioferrara/Desktop/michelin_restaurant_pages"

# Crea la cartella principale per gli HTML, se non esiste
os.makedirs(output_folder, exist_ok=True)

# Carica gli URL dal file
with open(url_file, "r") as f:
    urls = [line.strip() for line in f.readlines()]

# Scarica e salva le pagine HTML
for i, url in enumerate(urls, start=1):
    page_num = (i - 1) // 20 + 1  # Ogni cartella conterrà 20 ristoranti
    page_folder = os.path.join(output_folder, f"page_{page_num}")
    os.makedirs(page_folder, exist_ok=True)  # Crea la cartella per il batch corrente, se non esiste

    try:
        # Accedi alla pagina del ristorante
        driver.get(url)
        time.sleep(3)  # Pausa per permettere il caricamento della pagina

        # Salva l'HTML in un file nella cartella corrispondente
        html_content = driver.page_source
        filename = f"restaurant_{i}.html"
        filepath = os.path.join(page_folder, filename)

        with open(filepath, "w", encoding="utf-8") as file:
            file.write(html_content)

        print(f"Salvato: {filepath}")

    except Exception as e:
        print(f"Errore nel download di {url}: {e}")

driver.quit()
print("Download completato!")