from bs4 import BeautifulSoup
import json
import os

# Configurazione della cartella di output
output_folder = '/Users/fabrizioferrara/Desktop/michelin_restaurant_data/'
os.makedirs(output_folder, exist_ok=True)

# Variabili globali
file_counter = 1
glob_control = dict()

def extract_telephone(html_file):
    with open(html_file, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')
        script_tag = soup.find('script', type='application/ld+json')
        if script_tag:
            data = json.loads(script_tag.string)
            if 'telephone' in data:
                return data['telephone']
    return ''

def extract_payment(html_file):
    with open(html_file, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')
        script_tag = soup.find('script', type='application/ld+json')
        if script_tag:
            data = json.loads(script_tag.string)
            if 'paymentAccepted' in data:
                return data['paymentAccepted'].split(", ")
    return []

def name_restaurant(html_file):
    with open(html_file, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')
        script_tag = soup.find('script', type='application/ld+json')
        if script_tag:
            data = json.loads(script_tag.string)
            if 'name' in data:
                return data['name']
    return ''

def address_restaurant(html_file):
    with open(html_file, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')
        script_tag = soup.find('script', type='application/ld+json')
        if script_tag:
            data = json.loads(script_tag.string)
            if 'address' in data:
                address = data['address']
                return (address.get('streetAddress', ''), 
                        address.get('addressLocality', ''), 
                        address.get('postalCode', ''),
                        address.get('addressCountry', ''))
    return ('', '', '', '')

def description_restaurant(html_file):
    with open(html_file, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')
        script_tag = soup.find('script', type='application/ld+json')
        if script_tag:
            data = json.loads(script_tag.string)
            if 'review' in data:
                return data['review']['description']
    return ''

def extract_services(html_file):
    with open(html_file, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')
        services_div = soup.find('div', class_='restaurant-details__services')
        if services_div:
            ul_tag = services_div.find('ul')
            if ul_tag:
                li_tags = ul_tag.find_all('li')
                return [li.get_text(strip=True) for li in li_tags]
    return []

def extract_data_sheet_block_text(html_file):
    with open(html_file, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')
        data_sheet_div = soup.find('div', class_='data-sheet__block')
        data_sheet_texts = []
        for div in data_sheet_div.find_all('div', class_='data-sheet__block--text'):
            data_sheet_texts.append(div.get_text(strip=True).replace('\n', ''))
        return data_sheet_texts

def extract_links(html_file):
    with open(html_file, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')
        links = soup.find_all('div', class_='collapse__block-item link-item')
        hrefs = [link.find('a')['href'] for link in links if link.find('a')]
        if hrefs:
            return hrefs[0]
    return ''

def write_data_to_file(html_file):
    global file_counter
    global glob_control
    
    name = name_restaurant(html_file)
    street, city, postal_code, country = address_restaurant(html_file)
    description = description_restaurant(html_file)
    services = extract_services(html_file)
    data_sheet = extract_data_sheet_block_text(html_file)
    telephone = extract_telephone(html_file)
    payments = extract_payment(html_file)
    website = extract_links(html_file)

    # Estrarre prezzo e tipo di cucina dalla scheda dati
    price = data_sheet[1].split("  ")[0].strip() if len(data_sheet) > 1 else ''
    cuisine = data_sheet[1].split("  ")[-1].strip() if len(data_sheet) > 1 else ''

    # Salva i dati in un file .tsv
    output_file_path = os.path.join(output_folder, f'restaurant_{file_counter}.tsv')
    with open(output_file_path, 'w', encoding='utf-8') as file:
        file.write("restaurantName\taddress\tcity\tpostalCode\tcountry\tpriceRange\tcuisineType\tdescription\tfacilitiesServices\tcreditCards\tphoneNumber\twebsite\n")
        file.write(f"{name}\t{street}\t{city}\t{postal_code}\t{country}\t{price}\t{cuisine}\t{description}\t{', '.join(services)}\t{', '.join(payments)}\t{telephone}\t{website}\n")
    
    file_counter += 1
    print(f"File salvato: {output_file_path}")

# Esecuzione del parser sui file HTML scaricati
if __name__ == "__main__":
    for i in range(1, 101):
        directory = f'/Users/fabrizioferrara/Desktop/michelin_restaurant_pages/page_{i}'
        if os.path.exists(directory):
            for filename in os.listdir(directory):
                if filename.endswith('.html'):
                    html_file = os.path.join(directory, filename)
                    write_data_to_file(html_file)