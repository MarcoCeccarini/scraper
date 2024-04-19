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

class RomaAlboJob(BaseJob):

    def __init__(self, id_struttura, nome_pa, id_sezione, nome_sezione):
        super().__init__(id_struttura, nome_pa, id_sezione, nome_sezione)

    def run(self):
                
        dao = Dao("1","COMUNE_DI_ROMA", "201", "ALBO_PRETORIO")
        headers={
            'Content-type':'application/json', 
            'Accept':'application/json'
        }
        url = "https://www.comune.roma.it/gedalbonet/restgwb/api/gwalbopretorioonline/gestionepubblicazioneao/selezionepubblicazione"
        level = "sottosezione-lv1"

        chrome_driver = ChromeDriverManager().install()
        driver = Chrome(service=Service(chrome_driver)) 
        driver.implicitly_wait(30)
        driver.set_page_load_timeout(30) 

        driver.get("https://www.comune.roma.it/gedalbonet/")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        while True:

            self.logger.info(driver.find_element(By.CLASS_NAME, 'react-bootstrap-table-pagination-total').text)

            rows_number = len(driver.find_elements(By.XPATH, "//button[contains(text(), 'Dettaglio')]")) 

            sel_idx = 0
            while sel_idx < rows_number:
                
                self.logger.info('['+str(sel_idx)+']/'+str(rows_number))

                driver.find_elements(By.XPATH, "//button[contains(text(), 'Dettaglio')]")[sel_idx].click()
                driver.refresh()
                time.sleep(5)        

                sel_idx += 1    
                
                n_atto = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="main"]/form/div/div[1]/div/div/div[2]/div/div[1]/div/div/div[1]/div[2]/label'))).text

                utente_data_inserimento = driver.find_element(By.XPATH, '//*[@id="main"]/form/div/div[1]/div/div/div[2]/div/div[1]/div/div/div[6]/div[2]/label').text

                utente_data_fine_val = driver.find_element(By.XPATH, '//*[@id="main"]/form/div/div[1]/div/div/div[2]/div/div[1]/div/div/div[7]/div[2]/label').text

                atto_idx = 0
                for atto_tr in driver.find_elements(By.XPATH,'//*[@id="idListaAllegati"]/tbody//tr'):

                    self.read_count += 1                

                    atto_idx +=1

                    n_doc =  atto_tr.find_element(By.XPATH,'.//td[1]').text
                    contenuto =  atto_tr.find_element(By.XPATH,'.//td[2]').text


                    payload =json.dumps({
                        "idFil": n_doc,
                        "idPbl": n_atto
                    })
                    
                    response = requests.request("POST", url, headers=headers, data=payload)

                    try:
                        if response.status_code == 200:

                            res = response.json()

                            file_name = res['payload']['nomFil'] # real filename

                            base64_content = res['payload']['base64File']

                            base64_data = base64_content.split(',')[1]

                            file_content = base64.b64decode(base64_data)

                            file_path = dao.nome_pa+"/"+dao.nome_sezione+"/"+contenuto

                            Path(dao.nome_pa+"/"+dao.nome_sezione).mkdir(parents=True, exist_ok=True)

                            with open(file_path, 'wb') as f:
                                f.write(file_content)

                            last_doc = dao.get_doc(contenuto=contenuto, link_pubblico=url+payload)    

                            if(last_doc): #skip double
                                self.logger.debug(last_doc)
                                if(last_doc[5] <= datetime.strptime(utente_data_inserimento, '%d/%m/%Y').date()):
                                    logging.warning(f"{file_name}: DOUBLE SKIPPED!!!")
                                    self.double_skipped_count +=1
                                    continue
                                else:
                                    dao.delete_doc(contenuto=contenuto, link_pubblico=url+payload)    
                                    logging.warning(f"{file_name}: DOUBLE REPLACED!!!")
                                    self.double_replaced_count +=1

                            dao.create_doc(dir=dao.nome_pa+"/"+dao.nome_sezione,file_path=file_path, contenuto=contenuto, link_pubblico=url+payload, n_atto=n_atto, utente_data_fine_val=datetime.strptime(utente_data_fine_val, '%d/%m/%Y'), utente_data_inserimento=datetime.strptime(utente_data_inserimento, '%d/%m/%Y'))

                            self.write_count +=1
                        else:
                            self.logger.warning(f"Request failed with status code: {response.status_code}")
                            self.logger.warning(f"An error occurred: {str(e)}")
                            raise e
                    except Exception as e:
                        self.error_count +=1
                        self.logger.error(f"{str(e)}")
                    self.logger.debug(file_name)
                        
                driver.back() 
                time.sleep(5)            
                '''    
                if driver.find_element(By.XPATH, "//button[contains(text(), '>')]").get_attribute('class').find('enabled') != -1:
                    driver.find_element(By.XPATH, "//button[contains(text(), '>')]").click()
                else:
                    if driver.find_element(By.XPATH, "//button[contains(text(), '>>')]").get_attribute('class').find('enabled') != -1:
                        driver.find_element(By.XPATH, "//button[contains(text(), '>>')]").click()
                        time.sleep(15)

                if(driver.find_element(By.XPATH, "//button[contains(text(), '>')]").get_attribute('class').find('enabled') == -1
                    & driver.find_element(By.XPATH, "//button[contains(text(), '>>')]").get_attribute('class').find('enabled') == -1 ):
                    break 
                    driver.quit()            
                '''