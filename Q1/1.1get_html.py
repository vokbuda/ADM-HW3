import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
def create_directory_with_pages(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
def read_lines_from_file(file_path,page):
    # start from page 1 but if u will blocked it is also possible to change this parameter
    
    dict_of_pages=dict()
    list_of_urls=[]
    chrome_options = Options()
    chrome_options.add_argument('--kiosk-printing')  # Enable silent printing
    chrome_options.add_argument("--log-level=3")  # Set log level to severe
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service,options=chrome_options)
   
    iterator=0
   
    
    with open(file_path, 'r') as file:
            
            list_of_urls.append(line.strip())
            # check if elements are 20 or if we reached the end of page
            if len(list_of_urls)==20 or line==None:
                                
                for element in list_of_urls:
                    driver.get(element)
                    if iterator==0:
                        # click accept button for cookies
                        agree_button = driver.find_element(By.XPATH,'//*[@id="didomi-notice-agree-button"]')
                        agree_button.click()
                        iterator+=1 
                    html_code=driver.page_source
                    create_directory_with_pages('html_code/page_'+str(page))
                    name_rest=element.replace('https://guide.michelin.com/en/','')
                    name_rest=name_rest.replace('/','_')
                    # below we save html code to the file
                    with open(f'html_code/page_{page}/'+name_rest+'.html', 'w',encoding='utf-8') as file:
                        file.write(html_code)
                dict_of_pages[page]=list_of_urls
                list_of_urls=[]
                page+=1
                if page==101:
                    break


            # each page contains 20 restaurants and then save maybe 4 pages at a time

# Example usage
if __name__ == "__main__":
    create_directory_with_pages('html_code')
    read_lines_from_file('urls/urls.txt',page=1)
    