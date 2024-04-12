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
from Dao import Dao
import requests
import base64
import json

dao = Dao()
numero_atto_tds = []
payloads =[]
headers={
    'Content-type':'application/json', 
    'Accept':'application/json'
}
url = "https://www.comune.roma.it/gedalbonet/restgwb/api/gwalbopretorioonline/gestionepubblicazioneao/selezionepubblicazione"


chrome_driver = ChromeDriverManager().install()
driver = Chrome(service=Service(chrome_driver)) 
driver.implicitly_wait(30)
driver.set_page_load_timeout(30) 

driver.get("https://www.comune.roma.it/gedalbonet/")
driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

# while True:

print(driver.find_element(By.CLASS_NAME, 'react-bootstrap-table-pagination-total').text)

rows_number = len(driver.find_elements(By.XPATH, "//button[contains(text(), 'Dettaglio')]")) 

sel_idx = 0
while sel_idx < rows_number:
        
    print('['+str(sel_idx)+']/'+str(rows_number))

    driver.find_elements(By.XPATH, "//button[contains(text(), 'Dettaglio')]")[sel_idx].click()
    
    time.sleep(5)        

    sel_idx += 1    
    
    atto_label = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="main"]/form/div/div[1]/div/div/div[2]/div/div[1]/div/div/div[1]/div[2]/label')))

    for atto_idx in range(len(driver.find_elements(By.XPATH,'//*[@id="idListaAllegati"]/tbody//tr/td[1]'))):

        numero_atto_td = driver.find_elements(By.XPATH,'//*[@id="idListaAllegati"]/tbody//tr/td[1]')[atto_idx]

        atto_idx +=1
        
        print("-"+str(sel_idx)) # "+": #1:"+atto_label.text+",#2:"+numero_atto_td.text+"...: Downloading....")

        payload =json.dumps({
            "idFil": numero_atto_td.text,
            "idPbl": atto_label.text
        })
        
        response = requests.request("POST", url, headers=headers, data=payload)

        try:
            if response.status_code == 200:

                res = response.json()

                file_name = res['payload']['nomFil']

                base64_content = res['payload']['base64File']

                base64_data = base64_content.split(',')[1]

                file_content = base64.b64decode(base64_data)

                file_path = file_name

                with open(file_path, 'wb') as f:
                    f.write(file_content)
                dao.create_doc(file_path,file_name, url+payload, numero_atto_td.text)
            else:
                print(f"Request failed with status code: {response.status_code}")
        except Exception as e:
                print(f"An error occurred: {str(e)}")
        print(file_name)
             
        driver.back() 
'''            
if driver.find_element(By.XPATH, "//button[contains(text(), '>')]").get_attribute('class').find('enabled') != -1:
    driver.find_element(By.XPATH, "//button[contains(text(), '>')]").click()
else:
    if driver.find_element(By.XPATH, "//button[contains(text(), '>>')]").get_attribute('class').find('enabled') != -1:
        driver.find_element(By.XPATH, "//button[contains(text(), '>>')]").click()
        time.sleep(15)

if(driver.find_element(By.XPATH, "//button[contains(text(), '>')]").get_attribute('class').find('enabled') == -1
    & driver.find_element(By.XPATH, "//button[contains(text(), '>>')]").get_attribute('class').find('enabled') == -1 ):
'''       
#    break 
            
