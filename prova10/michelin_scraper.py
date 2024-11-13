from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException
import time

# Configura il WebDriver per Chrome
options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# Usa il percorso assoluto per ChromeDriver
service = Service('/Users/fabrizioferrara/Desktop/Progetti DataScience/ADM/michelin_scraper/chromedriver')
driver = webdriver.Chrome(service=service, options=options)

# URL base della pagina dei ristoranti Michelin con paginazione
BASE_URL = "https://guide.michelin.com/en/it/restaurants/page/"

urls = set()
page_number = 1  # Inizia dalla prima pagina

while True:
    # Genera l'URL per la pagina corrente
    page_url = BASE_URL + str(page_number)
    driver.get(page_url)
    time.sleep(5)  # Attendere il caricamento della pagina

    # Raccogliere i link dei ristoranti visibili con gestione dell'errore
    initial_count = len(urls)
    try:
        restaurant_links = driver.find_elements(By.CSS_SELECTOR, "a.link")
        for link in restaurant_links:
            retry_count = 0
            while retry_count < 3:  # Fino a 3 tentativi per ogni link
                try:
                    href = link.get_attribute("href")
                    if "/restaurant/" in href:
                        urls.add(href)
                    break  # Esci dal ciclo di ritentativi se riesce
                except StaleElementReferenceException:
                    print("Stale element, ritentando...")
                    retry_count += 1
                    time.sleep(1)  # Pausa breve prima di ritentare
    except StaleElementReferenceException:
        print("Errore: elemento non trovato, riprovando la pagina...")
        time.sleep(2)
        continue

    # Stampa il numero di URL raccolti finora
    print(f"Pagina {page_number}: {len(urls)} URL raccolti")

    # Verifica se sono stati aggiunti nuovi URL
    if len(urls) == initial_count:
        print("Fine della paginazione raggiunta.")
        break

    # Incrementa il numero di pagina per passare alla successiva
    page_number += 1

driver.quit()

# Verifica finale del numero di URL raccolti
print(f"Numero totale di URL raccolti: {len(urls)}")

# Salva tutti gli URL in un file (assicurati di specificare il percorso corretto)
output_path = "/Users/fabrizioferrara/Desktop/michelin_restaurants_urls.txt"
with open(output_path, "w") as file:
    for url in urls:
        file.write(url + "\n")

print(f"File salvato con successo in {output_path}")