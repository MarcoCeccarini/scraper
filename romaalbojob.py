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
from selenium.common.exceptions import ElementClickInterceptedException

class RomaAlboJob(BaseJob):

    def __init__(self, id_struttura, nome_pa, id_sezione, nome_sezione):

        super().__init__(id_struttura, nome_pa, id_sezione, nome_sezione)

        self.dao = Dao("1","COMUNE_DI_ROMA", "201", "ALBO_PRETORIO")

        self.headers={
            'Content-type':'application/json', 
            'Accept':'application/json'
        }
        self.url = "https://www.comune.roma.it/gedalbonet/restgwb/api/gwalbopretorioonline/gestionepubblicazioneao/selezionepubblicazione"



    def click_element_retry(self, locator, sel_idx=None, max_retries=5):
        retries = 0
        while retries < max_retries:
            try:
                # overlap_ele = self.driver.find_element(By.CLASS_NAME, 'Header-toggle')
                # overlap_ele.click()
                self.driver.execute_script("window.scrollTo(0, 0);")

                if(sel_idx == None):
                    ele = self.driver.find_element(*locator)
                else:
                    ele = self.driver.find_elements(*locator)[sel_idx]
                
                ele.click()

                return  # Exit the function if click is successful
            except Exception as e:
                time.sleep(5)
                retries += 1
                self.logger.error(f"ElementClickInterceptedException occurred. Retrying attempt {retries}/{max_retries}")
        raise ElementClickInterceptedException(f"Max retries exceeded. Element could not be clicked.{str(e)}")


    def run(self):
                
        self.driver.get("https://www.comune.roma.it/gedalbonet/")
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        page_number = 41
        page_set_clicked = 8
        while True:

            self.logger.info(self.driver.find_element(By.CLASS_NAME, 'react-bootstrap-table-pagination-total').text)

            rows_number = len(self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Dettaglio')]")) 

            sel_idx = 19
            
            while sel_idx < rows_number:
                
                self.logger.info('['+str(sel_idx)+']/'+str(rows_number))
                try:
                    self.driver.find_elements(By.XPATH, "//button[contains(text(), 'Dettaglio')]")[sel_idx].click()
                except Exception as e:
                    self.click_element_retry((By.XPATH, "//button[contains(text(), 'Dettaglio')]"), sel_idx)

                time.sleep(5)        

                sel_idx += 1    
                
                n_atto = self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="main"]/form/div/div[1]/div/div/div[2]/div/div[1]/div/div/div[1]/div[2]/label'))).text

                utente_data_inserimento = self.driver.find_element(By.XPATH, '//*[@id="main"]/form/div/div[1]/div/div/div[2]/div/div[1]/div/div/div[6]/div[2]/label').text

                utente_data_fine_val = self.driver.find_element(By.XPATH, '//*[@id="main"]/form/div/div[1]/div/div/div[2]/div/div[1]/div/div/div[7]/div[2]/label').text

                atto_idx = 0
                for atto_tr in self.driver.find_elements(By.XPATH,'//*[@id="idListaAllegati"]/tbody//tr'):

                    self.read_count += 1                

                    atto_idx +=1

                    n_doc =  atto_tr.find_element(By.XPATH,'.//td[1]').text
                    contenuto =  atto_tr.find_element(By.XPATH,'.//td[2]').text


                    payload =json.dumps({
                        "idFil": n_doc,
                        "idPbl": n_atto
                    })
                    
                    response = requests.request("POST", self.url, headers=self.headers, data=payload)

                    try:
                        if response.status_code == 200:

                            res = response.json()

                            file_name = res['payload']['nomFil'] # real filename

                            base64_content = res['payload']['base64File']

                            base64_data = base64_content.split(',')[1]

                            file_content = base64.b64decode(base64_data)

                            file_path = self.dao.nome_pa+"/"+self.dao.nome_sezione+"/"+contenuto

                            Path(self.dao.nome_pa+"/"+self.dao.nome_sezione).mkdir(parents=True, exist_ok=True)

                            with open(file_path, 'wb') as f:
                                f.write(file_content)

                            last_doc = self.dao.get_doc(contenuto=contenuto, link_pubblico=self.url+payload)    

                            if(last_doc): #skip double
                                if(last_doc[5] <= datetime.strptime(utente_data_inserimento, '%d/%m/%Y').date()):
                                    logging.warning(f"{file_name}: DOUBLE SKIPPED!!!")
                                    self.double_skipped_count +=1
                                    continue
                                else:
                                    self.dao.delete_doc(contenuto=contenuto, link_pubblico=self.url+payload)    
                                    logging.warning(f"{file_name}: DOUBLE REPLACED!!!")
                                    self.double_replaced_count +=1

                            # self.dao.create_doc(dir=self.dao.nome_pa+"/"+self.dao.nome_sezione,file_path=file_path, contenuto=contenuto, link_pubblico=self.url+payload, n_atto=n_atto, utente_data_fine_val=datetime.strptime(utente_data_fine_val, '%d/%m/%Y'), utente_data_inserimento=datetime.strptime(utente_data_inserimento, '%d/%m/%Y'), id_struttura=None)

                            self.write_count +=1
                        else:
                            self.logger.warning(f"Request failed with status code: {response.status_code}")
                            self.logger.warning(f"An error occurred: {str(e)}")
                            raise e
                    except Exception as e:
                        self.error_count +=1
                        self.logger.error(f"{str(e)}")
                    self.logger.debug(file_name)

                self.driver.back() 
                time.sleep(5)            
                
                btn_links = self.driver.find_elements(By.XPATH, "//button[contains(@class, 'paginazione')]")

                next_btn = next(filter(lambda x : int(0 if not x.text.isdigit() else x.text ) == page_number + 1, btn_links ), None)
                
                if next_btn:
                    next_btn.click()
                else:
                    click_index = 0
                    page_set_clicked += 1
                    while click_index < page_set_clicked:
                        # self.driver.find_element(By.XPATH, "//button[contains(text(), '>>')]").click()
                        self.click_element_retry((By.XPATH, "//button[contains(text(), '>>')]"))
                        time.sleep(5)
                        click_index += 1
                
                page_number += 1
                
                '''
                if self.driver.find_element(By.XPATH, "//button[contains(text(), '>')]").get_attribute('class').find('enabled') != -1:
                    self.driver.find_element(By.XPATH, "//button[contains(text(), '>')]").click()
                else:
                    if self.driver.find_element(By.XPATH, "//button[contains(text(), '>>')]").get_attribute('class').find('enabled') != -1:
                        self.driver.find_element(By.XPATH, "//button[contains(text(), '>>')]").click()
                        time.sleep(5)
                '''
                '''
                if(self.driver.find_element(By.XPATH, "//button[contains(text(), '>')]").get_attribute('class').find('enabled') == -1
                    & self.driver.find_element(By.XPATH, "//button[contains(text(), '>>')]").get_attribute('class').find('enabled') == -1 ):
                    self.driver.quit()            
                    break 
                '''
            
job = RomaAlboJob("1","COMUNE_DI_ROMA", "201", "ALBO_PRETORIO")
job.run()
job.report()                
                