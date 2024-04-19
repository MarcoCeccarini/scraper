from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from dotenv import load_dotenv
import os
import csv
import os
import time
from dao import Dao
import requests
import base64
import json


class Trasparente:

    def recurse(self, menu_link):
        
        print("- menu:"+menu_link.get_attribute('href'))
        
        menu_link.click()
        time.sleep(5)
        
        container_el = driver.find_element(By.CSS_SELECTOR,'div.Grid')
        
        for accordion in container_el.find_elements(By.CLASS_NAME, "Accordion"):
            accordion.click() # expand
            acc_links = accordion.find_elements(By.TAG_NAME, "a")
                
            # content_link_els = container_el.find_elements(By.TAG_NAME, "a").append(acc_links)
            content_link_els = container_el.find_elements(By.TAG_NAME, "a")
            print(content_link_els)
        for content_link_el in content_link_els: 
            print("- href:"+content_link_el.get_attribute('href'))
            if content_link_el.get_attribute('href').endswith('.pdf') :
                content_link_el.click() # Download...
            else:
                if content_link_el.get_attribute('href').find('www.comune.roma.it') != -1:
                    if content_link_el.get_attribute('href').find('home.page') == -1:
                        if content_link_el.get_attribute('href').find('#') == -1:
                            self.recurse(content_link_el)
        

        for menu_link in driver.find_elements(By.XPATH, "//*[@id='main']/div[2]/div/aside/div[2]/ul//li/a"):
                self.recurse(menu_link)                            


chrome_driver = ChromeDriverManager().install()
driver = Chrome(service=Service(chrome_driver)) 
driver.implicitly_wait(30)
driver.set_page_load_timeout(30) 

driver.get("https://www.comune.roma.it/web/it/amministrazione-trasparente.page")
time.sleep(5)

t = Trasparente()

for menu_link in driver.find_elements(By.XPATH, "//*[@id='main']/div[2]/div/aside/div[2]/ul//li/a"):
   t.recurse(menu_link)
    

driver.quit()              
print('END')