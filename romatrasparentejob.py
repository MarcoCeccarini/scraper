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
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import ElementClickInterceptedException

class RomaTrasparenteJob(BaseJob):

    def __init__(self, id_struttura, nome_pa, id_sezione, nome_sezione):
        super().__init__(id_struttura, nome_pa, id_sezione, nome_sezione)

        self.dao = Dao(nome_pa='COMUNE DI ROMA',nome_sezione='AMMINISTRAZIONE TRASPARENTE',id_sezione=1,id_struttura=1)


    def click_element_retry(self, parent_locator, locator, sel_idx, max_retries=5):
        retries = 0
        while retries < max_retries:
            try:
                self.driver.execute_script("window.scrollTo(0, 0);")

                parent_ele =  self.driver.find_element(*parent_locator)

                ele = parent_ele.find_elements(*locator)[sel_idx]
                
                # ele.click()

                return ele
            except Exception as e:
                time.sleep(5)
                retries += 1
                self.logger.error(f"ElementClickInterceptedException occurred. Retrying attempt {retries}/{max_retries}")
        raise ElementClickInterceptedException(f"Max retries exceeded. Element could not be clicked.")


    def recurse(self, parent_locator, locator, sel_idx, parent_level=None):

        menu_link = self.click_element_retry(parent_locator, locator, sel_idx)

        if parent_level == None:
            level1 = menu_link.text
            level2 = ''
        else:
            level1 = parent_level
            level2 = menu_link.text

        path_level = level1 if parent_level == None else level1+'/'+level2

        last_struttura = self.dao.get_struttura(level1, level2)
        if last_struttura == None :
            self.dao.create_struttura(id_sezione=self.dao.id_sezione,level1=level1,level2=level2)
            last_struttura = self.dao.get_struttura(level1, level2)

        # self.wait.until(EC.element_to_be_clickable(menu_link))
        
        try:
            self.logger.debug('#'+menu_link.text)
            if(menu_link.get_attribute('href') == None):
                return
            menu_link.click()
        except Exception as e:
            self.logger.warning(str(e))
            self.click_element_retry(parent_locator=parent_locator, locator=locator,sel_idx=sel_idx).click()

        time.sleep(5)

        list(map(lambda x: self.logger.debug(x.get_attribute('href')), list(filter(lambda x: x.get_attribute('href') is not None and x.get_attribute('href').endswith('.pdf') , self.driver.find_elements(By.TAG_NAME,'a')))))
        
        for link in list(filter(lambda x: x.get_attribute('href') is not None, self.driver.find_elements(By.TAG_NAME,'a'))):

            if link.get_attribute('href').endswith('.pdf'):
                
                self.read_count +=1

                self.logger.debug('- '+link.get_attribute('href'))

                n_atto = None

                utente_data_inserimento = datetime.now().date().strftime('%d/%m/%Y')

                utente_data_fine_val =  datetime.now().date().strftime('%d/%m/%Y')

                contenuto = link.get_attribute('href').split('/')[len(link.get_attribute('href').split('/')) -1]

                try:
                    response = requests.request("GET", link.get_attribute('href'))

                    if response.status_code == 200:

                        file_path = self.dao.nome_pa+"/"+self.dao.nome_sezione+"/"+path_level+"/"+contenuto

                        Path(self.dao.nome_pa+"/"+self.dao.nome_sezione+'/'+path_level).mkdir(parents=True, exist_ok=True)

                        with open(file_path, 'wb') as f:
                            f.write(response.content)

                        last_doc = self.dao.get_doc(contenuto=contenuto, link_pubblico=link.get_attribute('href'))    

                        if(last_doc): #skip double
                            if(last_doc[5] <= datetime.strptime(utente_data_inserimento, '%d/%m/%Y').date()):
                                logging.warning(f"{link.get_attribute('href')}: DOUBLE SKIPPED!!!")
                                self.double_skipped_count +=1
                                continue
                            else:
                                self.dao.delete_doc(contenuto=contenuto, link_pubblico=link.get_attribute('href'))    
                                logging.warning(f"{link.get_attribute('href')}: DOUBLE REPLACED!!!")
                                self.double_replaced_count +=1

                        self.dao.create_doc(dir=self.dao.nome_pa+"/"+self.dao.nome_sezione+'/'+path_level,file_path=file_path, contenuto=contenuto, link_pubblico=link.get_attribute('href'), n_atto=n_atto, utente_data_fine_val=datetime.strptime(utente_data_fine_val, '%d/%m/%Y'), utente_data_inserimento=datetime.strptime(utente_data_inserimento, '%d/%m/%Y'), id_struttura=last_struttura[0])

                        self.write_count +=1
                    else:
                        self.logger.warning(f"Request failed with status code: {response.status_code}")
                        self.logger.warning(f"An error occurred: {str(e)}")
                        raise e
                except Exception as e:
                    self.logger.error(f"An error occurred: {str(e)}")
        
        self.dao.commit()

        child_menu = self.driver.find_element(By.CLASS_NAME, "sidemenu")

        for sel_idx, child_menu_link in enumerate(child_menu.find_elements(By.TAG_NAME,'a')):

            self.recurse(parent_locator=(By.CLASS_NAME, "sidemenu"), locator=(By.TAG_NAME,'a'), sel_idx=sel_idx, parent_level=level1)
        

        self.driver.back()                         
        time.sleep(5)



    def run(self):

        self.driver.get("https://www.comune.roma.it/web/it/amministrazione-trasparente.page")

        time.sleep(5)

        self.recurse((By.CLASS_NAME, "sidemenu"), (By.TAG_NAME,'a'), sel_idx=1) # test disposizioni generali

        '''
        for menu_link in self.driver.find_element(By.CLASS_NAME, "sidemenu").find_elements(By.TAG_NAME,'a'):
            self.recurse(menu_link, None)
        '''
        self.driver.quit()



job = RomaTrasparenteJob("1","COMUNE_DI_ROMA", "1", "AMMINISTRAZIONE_TRASPARENTE")
job.run()        
job.report()

