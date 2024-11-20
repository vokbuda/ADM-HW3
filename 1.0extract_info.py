from bs4 import BeautifulSoup
import json
import os
file_counter=1
glob_control=dict()
def create_directory_with_pages(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

# function to extract telephone number from html file
def extract_telephone(html_file):
    with open(html_file, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')
        script_tag = soup.find('script', type='application/ld+json')
        if script_tag:
            data = json.loads(script_tag.string)
            if 'telephone' in data:
                return data['telephone']
# function to extract payment methods from html file        
def extract_payment(html_file):
    with open(html_file, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')
        script_tag = soup.find('script', type='application/ld+json')
        if script_tag:
            data = json.loads(script_tag.string)
            if 'paymentAccepted' in data:
                return [data['paymentAccepted']]
# function to extract restaurant name
def name_restaurant(html_file):
    with open(html_file, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')
        script_tag = soup.find('script', type='application/ld+json')
        if script_tag:
            data = json.loads(script_tag.string)
            if 'name' in data:
                return [data['name']]  
# function to extract address of the restaurant
def address_restaurant(html_file):
    with open(html_file, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')
        script_tag = soup.find('script', type='application/ld+json')
        if script_tag:
            data = json.loads(script_tag.string)
            if 'address' in data:
                return [data['address']]
# function to extract description of the restaurant
def description_restaurant(html_file):
    with open(html_file, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')
        data_sheet_description = soup.find('div', class_='data-sheet__description')
        data_sheet_texts = ''
        if data_sheet_description:
            data_sheet_texts=data_sheet_description.get_text(strip=True).replace('\n', '')
        return data_sheet_texts
            
# function to extract services from html file
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
                        
                    return ""
# function to extract website link from html file
def extract_links(html_file):
                        with open(html_file, 'r', encoding='utf-8') as file:
                            soup = BeautifulSoup(file, 'html.parser')
                            links = soup.find_all('div', class_='collapse__block-item link-item')
                            hrefs = [link.find('a')['href'] for link in links if link.find('a')]
                            if hrefs:
                                return hrefs[0]
                            else:
                                return ""
# function to write extracted data to tsv file                       
def write_data_to_file(html_file):
    # file_counter is a global variable which i used to skip some files

    global file_counter
    global glob_control
    # below we extract the data from html file
    telephones = extract_telephone(html_file)
    if telephones==None:
         telephones=''
    
    payments = extract_payment(html_file)
    if payments!=None:
        payments=payments[0].split(",")
    
    # below we extract the data from html file
    names=name_restaurant(html_file)
    name_rest=names[0]
    addresses=address_restaurant(html_file)[0]
    street=addresses['streetAddress']
    postal_code=addresses['postalCode']
    address_locality=addresses['addressLocality']
    review=description_restaurant(html_file)
    description=review
    finder_services=extract_services(html_file)
    data_sheet=extract_data_sheet_block_text(html_file)
    country=data_sheet[0].split(", ")[-1]
    cuisine_price=data_sheet[1]
    cuisine_price=cuisine_price.split("  ")
    cuisine_price = [item.strip() for item in cuisine_price if item!='' and item!='·']
    price=cuisine_price[0]
    cuisine=cuisine_price[1]
    links=extract_links(html_file)
    namer=name_rest.replace('"',"").replace("|","").replace("/","").replace("*","")
    if namer not in glob_control:
        glob_control[namer]=1
    else:
        glob_control[namer]+=1
        namer=namer+str(glob_control[namer])
  
    # below we elaborate on the data
    street=" ".join(street.replace('\n', '').strip().split())
    address_locality=address_locality.replace('\n', '').strip()
    description=description.replace('\n', '').strip()
    
    # below we write the data to the file using requested tsv format
    
    with open('restaurants_tsv/'+'restaurant_'+str(file_counter)+'.tsv', 'w',encoding='utf-8') as file:
        file.write(f"restaurantName\taddress\tCity\tpostalCode\tcountry\tpriceRange\tcuisineType\tdescription\tfacilitiesServices\tcreditCards\tphoneNumber\twebsite\n")
        file.write(f"{name_rest}\t{street}\t{address_locality}\t{postal_code}\t{country}\t{price}\t{cuisine}\t{description}\t{finder_services}\t{payments}\t{telephones}\t{links}\n")
        file_counter+=1
        
if __name__ == "__main__":
    counter=0
    # loop over 100 downloaded pages because on the website we have 100 pages

    for i in range(1,101):
        directory = f'html_code/page_{i}'
        if os.path.exists(directory):
            for filename in os.listdir(directory):
                if filename.endswith('.html'):
                    html_file = os.path.join(directory, filename)
                    write_data_to_file(html_file)
                    counter+=1

                    


