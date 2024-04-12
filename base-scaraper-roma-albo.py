from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
import csv
import os
import time
#TEST
# webdriver.Firefox(executable_path=r'C:\Users\CeccariniMarco\dev\geckodriver-v0.34.0-win64')
chrome_driver = ChromeDriverManager().install()
driver = Chrome(service=Service(chrome_driver)) 
sezione = {}
# inizializzo il driver che ci permetterà di navigare il portale del comune di Palermo
# options = Options()
# PATH = './test_files_download'
# service = Service(executable_path = "C:/Users/MarcoCeccarini/Downloads/chromedriver-win64/chromedriver-win64/chromedriver.exe")
# prefs = {"download.default_directory": f"{PATH}"}
# options.add_experimental_option("prefs", prefs)
# driver = Chrome(service = service, options = options)
# Open a website
# indirizzo il driver alla pagina web del portale del comune di Palermo
driver.get("https://www.comune.roma.it/gedalbonet/")
#gli dico di attendere almeno 10 secondi se la pagina non viene caricata
driver.implicitly_wait(10)
#Cerco la classe che mi permetterà di cliccare sul "Rifiuta i cookies"
driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

driver.implicitly_wait(5)
# Find an element by ID and click on it
#creo una variabile che contiene tutti gli elementi all'interno dell'id specificato e con il tag specificato
#RICORDA: la funzione find_elements restituisce una lista di elementi web


while True:
    table = driver.find_element(By.CSS_SELECTOR, '#idListaAllegati')
    headers =  table.find_elements(By.TAG_NAME, 'th')
    tbody = table.find_element(By.TAG_NAME, 'tbody')
    rows = tbody.find_elements(By.TAG_NAME, 'tr')

    for row in rows:
        print(row.text)


    percorso_file_csv = r'C:\Users\CeccariniMarco\Desktop\informazioni-roma-albo.csv' 

# Apri il file CSV in modalità scrittura
# with open(percorso_file_csv, 'w', newline='') as file_csv:
    intestazioni = []
    row_tmp = {}
    with open(percorso_file_csv, 'w', newline='') as file_csv:
        # Definisci i nomi delle colonne
        for head in  headers:
            intestazioni.append(head.text)

        # Crea l'oggetto scrittore CSV
        scrittore_csv = csv.DictWriter(file_csv, delimiter=';', fieldnames=intestazioni)

        # Scrivi l'intestazione del CSV
        scrittore_csv.writeheader()

        # Itera attraverso il dizionario e scrivi ogni riga nel file CSV
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, 'td')
            for idx, cell in enumerate(cells):
                print(cells[idx].text)
                # time.sleep(3)
                # driver.execute_cdp_cmd("Page.printToPDF", {"landscape": False, "displayHeaderFooter": False})
                # if idx == 6:
                #    cells[idx].find_element(By.XPATH, "//button[contains(text(), 'Allegato')]").click()
                row_tmp.update({intestazioni[idx]: cells[idx].text})
            scrittore_csv.writerow(row_tmp)

        for row in rows:
            cells = row.find_elements(By.TAG_NAME, 'td')
            allegato = cells[6].find_element(By.XPATH, "//button[contains(text(), 'Allegato')]")
            allegato.click()

    next_button = driver.find_element(By.XPATH, "//button[contains(text(), '>>')]")

    enabled = next_button.get_attribute('class').find('enabled')

    if enabled != -1:
        next_button.click()
        driver.implicitly_wait(5)
    else:
        # driver.close()
        break