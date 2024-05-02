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

        self.menuFilterFn = lambda x: x.get_attribute('href') != None

        self.pdfFilterFn = lambda x: (
            x.get_attribute('href') is not None 
            and x.get_attribute('href').find("#") == -1
            and x.get_attribute('href').find("www.comune.roma.it") != -1
            and x.text != ""
            and x.get_attribute('href').endswith('.pdf')
        )

        self.sublinkFilterFn = lambda x: ( x.get_attribute('href') is not None 
            and x.get_attribute('href').find("#") == -1
            and x.get_attribute('href').find("www.comune.roma.it") != -1
            and x.get_attribute('href').find("amministrazione-trasparente") != -1
            and x.text != ""
            and not x.get_attribute('href').endswith('.pdf')
        )

    
    def get_date_by_label(self, label, res='31/12/9999'):
        
        try:
            ele = self.driver.find_element(By.XPATH,f"//*[text()='{label}']")

            ele = ele.find_element(By.XPATH,"..")

            res = ele.text.split(f"{label}:")[1].strip()
        except Exception as e:
            self.logger.warning(f"str{e}")

        return res

    def click_element_retry(self, parent_locator, locator, sel_idx, retryFilterFn, max_retries=5):
        retries = 0
        while retries < max_retries:
            try:
                self.driver.execute_script("window.scrollTo(0, 0);")
                
                self.driver.execute_script("arguments[0].parentNode.removeChild(arguments[0]);", self.driver.find_element(By.ID,"cookieIcon"))
                
                if parent_locator:
                    parent_ele =  self.driver.find_element(*parent_locator)

                    ele = list(filter(retryFilterFn, parent_ele.find_elements(*locator)))[sel_idx]

                if not parent_locator:
                    ele =  self.driver.find_elements(*locator)[sel_idx]

                # ele.click()
                href = ele.get_attribute('href')
                self.logger.info(f"# {href}")

                return ele
            except Exception as e:
                time.sleep(5)
                retries += 1
                self.logger.error(f"ElementClickInterceptedException occurred. Retrying attempt {retries}/{max_retries}")
                self.logger.warning(f'str{e}')
        raise ElementClickInterceptedException(f"Max retries exceeded. Element could not be clicked.")


    def recurse(self, parent_locator=None, locator=None, sel_idx=None, parent_level=None, retryfilterFn=None):
        
        menu_link = self.click_element_retry(parent_locator, locator, sel_idx, retryfilterFn)

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
            menu_link.click()
        except Exception as e:
            self.logger.warning(str(e))
            self.click_element_retry(parent_locator=parent_locator, locator=locator,sel_idx=sel_idx, retryFilterFn=retryfilterFn).click()

        time.sleep(5)

        main_div = self.driver.find_element(By.XPATH,"//div[@id='main']")
        content_links = main_div.find_elements(By.XPATH,".//a[ not(ancestor::div[contains(@class,'menu')]) and not(ancestor::nav) and not(ancestor::div[@class='Feedback']) and not(ancestor::div[@class='u-background-grey-80']) ]")
        
        # pdf content
        for link in  list(filter(self.pdfFilterFn, content_links)):
                
            self.read_count +=1

            self.logger.debug('- '+link.get_attribute('href'))

            n_atto = None

            utente_data_inserimento = self.get_date_by_label("data di pubblicazione")   

            utente_data_fine_val =  self.get_date_by_label("data di aggiornamento")

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
                            self.logger.warning(f"{link.get_attribute('href')}: DOUBLE SKIPPED!!!")
                            self.double_skipped_count +=1
                            continue
                        else:
                            self.dao.delete_doc(contenuto=contenuto, link_pubblico=link.get_attribute('href'))    
                            self.logger.warning(f"{link.get_attribute('href')}: DOUBLE REPLACED!!!")
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


        # sublinks content
        for sel_idx, content_sublink in enumerate(list(filter(self.sublinkFilterFn, content_links))):

            self.logger.debug(f"-> #..: {content_sublink.text}={content_sublink.get_attribute('href')} ")
            
            if self.driver.current_url.find(content_sublink.get_attribute("href")) != -1: # skip bacK
                self.logger.debug("<---------------Avoiding BACK!!!")
                continue

            self.recurse(parent_locator=(By.XPATH,"//div[@id='main']"), locator=(By.XPATH,".//a[ not(ancestor::div[contains(@class,'menu')]) and not(ancestor::nav) and not(ancestor::div[@class='Feedback']) and not(ancestor::div[@class='u-background-grey-80']) ]")
                        , sel_idx=sel_idx, parent_level=level1)
        
        # submenu
        for sel_idx, submenu_link in enumerate(list(filter(self.menuFilterFn, self.driver.find_element(By.CLASS_NAME, "sidemenu").find_elements(By.TAG_NAME,'a')))):
            self.recurse(parent_locator=(By.CLASS_NAME, "sidemenu"), locator=(By.TAG_NAME,'a'), sel_idx=sel_idx, parent_level=level1, retryfilterFn=self.menuFilterFn)

        self.driver.back()
        time.sleep(5)



    def run(self):

        # self.driver.get("https://www.comune.roma.it/web/it/amministrazione-trasparente.page")

        self.driver.get("https://www.comune.roma.it/web/it/amministrazione-trasparente-organizzazione.page")

        time.sleep(5)

        self.driver.find_element(By.ID,'cookie-bar-button').click()

        for sel_idx, menu_link in enumerate(list(filter(self.menuFilterFn, self.driver.find_element(By.CLASS_NAME, "sidemenu").find_elements(By.TAG_NAME,'a')))):
            self.recurse(parent_locator=(By.CLASS_NAME, "sidemenu"), locator=(By.TAG_NAME,'a'), sel_idx=sel_idx, retryfilterFn=self.menuFilterFn)

        self.driver.quit()





job = RomaTrasparenteJob("1","COMUNE_DI_ROMA", "1", "AMMINISTRAZIONE_TRASPARENTE")
job.run()       
job.report()

