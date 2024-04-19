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

dao = Dao()
numero_atto_tds = []
payloads =[]
headers={
    'Content-type':'application/json', 
    'Accept':'application/json'
}
url = "https://www.comune.roma.it/gedalbonet/restgwb/api/gwalbopretorioonline/gestionepubblicazioneao/selezionepubblicazione"
page_size = 20

chrome_driver = ChromeDriverManager().install()
driver = Chrome(service=Service(chrome_driver)) 
driver.implicitly_wait(30)
driver.set_page_load_timeout(30) 

driver.get("https://www.comune.roma.it/gedalbonet/")
driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()


sel_idx = 0
while sel_idx < page_size:

    driver.find_elements(By.XPATH, "//button[contains(text(), 'Dettaglio')]")[sel_idx].click()
    sel_idx += 1    
    time.sleep(5)
    atto_label = driver.find_element(By.XPATH,'//*[@id="main"]/form/div/div[1]/div/div/div[2]/div/div[1]/div/div/div[1]/div[2]/label')
    numero_atto_td = driver.find_element(By.XPATH,'//*[@id="idListaAllegati"]/tbody/tr/td[1]')
    print("-"+str(sel_idx)+": #1:"+atto_label.text+",#2:"+numero_atto_td.text)

    url = "https://www.comune.roma.it/gedalbonet/restgwb/api/gwalbopretorioonline/gestionepubblicazioneao/selezionepubblicazione"
    payload = json.dumps({
    "idFil": numero_atto_td.text,
    "idPbl": atto_label.text
    })
    headers = {
    'Content-Type': 'application/json',
    }
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
        else:
            print(f"Request failed with status code: {response.status_code}")
    except Exception as e:
            print(f"An error occurred: {str(e)}")
    driver.back()
    driver.implicitly_wait(10)