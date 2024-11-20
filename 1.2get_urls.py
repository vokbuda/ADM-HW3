import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time
from selenium.webdriver.common.by import By


# create a folder to store text file with urls
folder_path = 'urls'

if not os.path.exists(folder_path):
    os.makedirs(folder_path)
    file_path = os.path.join(folder_path, 'urls.txt')
    if not os.path.exists(file_path):
        with open(file_path, 'w') as file:
            pass


def webscrap_michelin_page():
    # create a webdriver object for running the script
    chrome_options = Options()
    chrome_options.add_argument('--kiosk-printing')  # Enable silent printing
    chrome_options.add_argument("--log-level=3")  # Set log level to severe
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service,options=chrome_options)
    # link to the michelin page
    restaurant_page='https://guide.michelin.com/en/it/restaurants/page/'
    # loop over 100 pages
    for i in range(1,101):
    #driver = webdriver.Chrome(ChromeDriverManager().install())
        driver.get(restaurant_page+str(i))
        # remove cookies
        if i==1:
            # this we need to accept the cookies
            agree_button = driver.find_element(By.XPATH,'//*[@id="didomi-notice-agree-button"]')
            agree_button.click()
        data_field = driver.find_element(By.XPATH, "//div[@class='row restaurant__list-row js-restaurant__list_items']")
        
        child_elements = data_field.find_elements(By.XPATH, "./*") 
        for element in child_elements:
            # here i find elements related to 'a' tag
            element_next_page=element.find_element(By.XPATH, ".//a[@class='link']")
            # get link and then write it to the file
            href = element_next_page.get_attribute('href')
            with open(file_path, 'a') as file:
                file.write(href + '\n')
        # below we can adjust the time to wait for the next page because of the website block
        time.sleep(6)
        
    
# explicitly declare the filepath 
   
file_path = 'urls/urls.txt'

webscrap_michelin_page()





