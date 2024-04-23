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



    def recurse(self, menu_link, parent_level):
        
        if(menu_link.get_attribute('href') == None):
            return

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

        self.wait.until(EC.element_to_be_clickable(menu_link))
        
        try:
            menu_link.click()
        except Exception as e:
             self.logger.warning(str(e))
             self.driver.execute_script("arguments[0].click()", menu_link)
            

        time.sleep(5)

        list(map(lambda x: self.logger.debug(x.get_attribute('href')), self.driver.find_elements(By.TAG_NAME,'a')))
        
        for link in list(filter(lambda x: x.get_attribute('href') is not None, self.driver.find_elements(By.TAG_NAME,'a'))):

            if link.get_attribute('href').endswith('.pdf'):
                
                self.read_count +=1

                self.logger.debug('- request vs click()...:'+link.get_attribute('href'))

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
                            self.logger.debug(last_doc)
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

        for child_menu_link in self.driver.find_element(By.CLASS_NAME, "sidemenu").find_elements(By.TAG_NAME,'a'):
                self.recurse(child_menu_link, level1)   
        

        self.driver.back()                         



    def run(self):

        self.driver.get("https://www.comune.roma.it/web/it/amministrazione-trasparente.page")

        time.sleep(5)

        self.recurse(self.driver.find_element(By.CLASS_NAME, "sidemenu").find_elements(By.TAG_NAME,'a')[1], None)
        '''
        for menu_link in self.driver.find_element(By.CLASS_NAME, "sidemenu").find_elements(By.TAG_NAME,'a'):
            self.recurse(menu_link, None)
        '''
        self.driver.quit()



    def contents(self):

        self.driver.get("https://www.comune.roma.it/web/it/amministrazione-trasparente-piano-triennale-per-la-prevenzione-della-corruzione-e-della-trasparenza.page")
      
        time.sleep(5)

        list(map(lambda x: self.logger.debug(x.get_attribute('href')), self.driver.find_element(By.CLASS_NAME, 'Grid-cell').find_elements(By.TAG_NAME,'a')))

        self.logger.debug('######################################################')

        list(map(lambda x: self.logger.debug(x.get_attribute('href')), self.driver.find_elements(By.TAG_NAME,'a')))
        


        acc_links = []
        for accordion in container_el.find_elements(By.CSS_SELECTOR, "div[class*=Accordion-panel]"):
            # accordion.click() # expand
            acc_links = accordion.find_elements(By.TAG_NAME, "a")
                
        content_link_els = container_el.find_elements(By.TAG_NAME, "a").append(acc_links)
        # content_link_els = container_el.find_elements(By.TAG_NAME, "a")
        
        if content_link_els is not None:
            print(map(lambda x: self.logger.debug(x), content_link_els))
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
        

job = RomaTrasparenteJob("1","COMUNE_DI_ROMA", "1", "AMMINISTRAZIONE_TRASPARENTE")
# job.contents()
job.run()
job.report()        

