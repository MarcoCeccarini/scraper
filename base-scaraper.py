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
driver.get("https://www.comune.palermo.it/amministrazione-trasparente.php?grp=3")
#gli dico di attendere almeno 10 secondi se la pagina non viene caricata
driver.implicitly_wait(10)
#Cerco la classe che mi permetterà di cliccare sul "Rifiuta i cookies"
driver.find_element(By.CLASS_NAME, 'cb-enable').click()

# Find an element by ID and click on it
#creo una variabile che contiene tutti gli elementi all'interno dell'id specificato e con il tag specificato
#RICORDA: la funzione find_elements restituisce una lista di elementi web
lista = driver.find_element(By.ID, 'at-grid').find_elements(By.TAG_NAME, 'li')
print(len(lista))
#itero su ogni elemento web all'interno della lista
for voce in lista:
    #Per ogni elemento prendo gli elementi con il TAG 'a', di questi mi servirà il nome della sezione e il link che porta alla sezione
    voce = voce.find_element(By.TAG_NAME, 'a')
    link = voce.get_attribute('href')
    print(f'{voce.text} : {link}')
    #aggiorno il dizionario
    sezione.update({voce.text : {'href' : voce.get_attribute('href')}})


#Adesso iteriamo per ogni sezione all'interno del dizionario sezioni e prendiamo il nome e i link delle varie sottosezioni 
for key, value in sezione.items():
    #per ogni sezione prendiamo il link e indirizziamo il driver alla pagina della sezione voluta
    driver.get(value['href'])
    time.sleep(2)
    #Stessa operazione fatta nella cella precedente: per ogni sezione prendiamo il nome ed il link della sottosezione
    sottosezioni = driver.find_element(By.ID, 'at-grid').find_elements(By.TAG_NAME, 'li')
    for sottosezione in sottosezioni:
        sottosezione = sottosezione.find_element(By.TAG_NAME, 'a')
        #inseriamo nome e link della sottosezione nel valore (che è un dizionario)dell'apposita sezione
        sezione[key].update({sottosezione.text : sottosezione.get_attribute('href')})    

# Find an element by name and type something into it
search_box = driver.find_element(By.ID,"q")
search_box.send_keys("Comune")
search_box.send_keys(Keys.RETURN)

# Wait for the page to load
try:
    # Wait until the element with the specific class name appears
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "gsc-table-result"))
    )
    # Extract information
    search_results = driver.find_elements_by_class_name("gsc-table-result")
    for result in search_results:
        print(result.text)
except:
    print("Timeout occurred while waiting for search results")

# Close the browser
driver.quit()

#Scriviamo tutto in un file
percorso_file_csv = r'C:\Users\CeccariniMarco\Desktop\informazioni.csv' 

# Apri il file CSV in modalità scrittura
# with open(percorso_file_csv, 'w', newline='') as file_csv:
with open(percorso_file_csv, 'w', newline='') as file_csv:
    # Definisci i nomi delle colonne
    intestazioni = ['sezione', 'sottosezione', 'link']

    # Crea l'oggetto scrittore CSV
    scrittore_csv = csv.DictWriter(file_csv, delimiter=';', fieldnames=intestazioni)

    # Scrivi l'intestazione del CSV
    scrittore_csv.writeheader()

    # Itera attraverso il dizionario e scrivi ogni riga nel file CSV
    for sezione, info in sezione.items():
        for sottosezione, link in info.items():
            # Ignora 'href'
            if sottosezione != 'href':
                scrittore_csv.writerow({'sezione': sezione, 'sottosezione': sottosezione, 'link': link})

#SE NON VOLETE ASPETTARE CHE CARICHI TUTTI I LINK POTETE FERMARE LA CELLA E PASSARE ALLA SUCCESSIVA

links_pdf = []
dizionario = {}
i = 0

for sezione, info in sezione.items():
    for sottosezione, link in info.items():
        # Ignora 'href'
        if sottosezione != 'href':
            driver.get(link)
            time.sleep(5)
            if len(driver.find_elements(By.CLASS_NAME, 'div100.accordion')) > 0:
                elenco = driver.find_elements(By.CLASS_NAME, 'div100.accordion')
                for bla in elenco:
                    dizionario.update({bla.text : []})
                    bla.click()
                    pdfs = bla.find_element(By.CLASS_NAME, 'content').find_element(By.TAG_NAME, 'ul').find_elements(By.TAG_NAME, 'li')

                    for pdf in pdfs:
                        pdf.find_element(By.TAG_NAME, 'a').click()
                        links_pdf.append(pdf.find_element(By.TAG_NAME, 'a').get_attribute('href'))

for link_pdf in links_pdf:
    driver.get(link_pdf)
    time.sleep(2)
    driver.execute_cdp_cmd("Page.printToPDF", {"landscape": False, "displayHeaderFooter": False})
    time.sleep(2)                        