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
from pathlib import Path
from datetime import datetime
import logging
from basejob import BaseJob

class RomaTrasparenteJob(BaseJob):

    def __init__(self, id_struttura, nome_pa, id_sezione, nome_sezione):
        super().__init__(id_struttura, nome_pa, id_sezione, nome_sezione)

        self.dao = Dao(nome_pa='COMUNE DI ROMA',nome_sezione='AMMINISTRAZIONE TRASPARENTE',id_sezione=1,id_struttura=1)

    def recurse(self, menu_link):
        
        self.logger.debug("# menu:"+menu_link.get_attribute('href'))
        
        menu_link.click()
        time.sleep(5)
        
        container_el = self.driver.find_element(By.CSS_SELECTOR,'div.Grid')
        
        for accordion in container_el.find_elements(By.CLASS_NAME, "Accordion"):
            accordion.click() # expand
            acc_links = accordion.find_elements(By.TAG_NAME, "a")
                
        # content_link_els = container_el.find_elements(By.TAG_NAME, "a").append(acc_links)
        content_link_els = container_el.find_elements(By.TAG_NAME, "a")
        
        map(lambda x: self.logger.debug(x), content_link_els)

        for content_link_el in content_link_els:
            
            self.read_count +=1
            
            self.logger.debug("- href:"+content_link_el.get_attribute('href'))
            
            if content_link_el.get_attribute('href').endswith('.pdf') :
                content_link_el.click() # Download...
                # self.dao.create_doc(contenuto=dir=file_path=link_pubblico=n_atto=utente_data_fine_val=utente_data_inserimento=)
                self.write_count+=1
                
            else:
                if content_link_el.get_attribute('href').find('www.comune.roma.it') != -1:
                    if content_link_el.get_attribute('href').find('home.page') == -1:
                        if content_link_el.get_attribute('href').find('#') == -1:
                            self.recurse(content_link_el)
        

        for menu_link in self.driver.find_element(By.CLASS_NAME, "sidemenu").find_elements(By.TAG_NAME,'a'):
                self.recurse(menu_link)                            

    def run(self):

        self.driver.get("https://www.comune.roma.it/web/it/amministrazione-trasparente.page")
        time.sleep(5)

        sidemenu = self.driver.find_element(By.ID, "sidemenu")
        self.logger.debug(str(sidemenu))

        for menu_link in self.driver.find_element(By.CLASS_NAME, "sidemenu").find_elements(By.TAG_NAME,'a'):
            self.recurse(menu_link)

        self.driver.quit()              
