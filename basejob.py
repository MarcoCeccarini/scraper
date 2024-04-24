from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import ElementClickInterceptedException
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

class BaseJob:

    def __init__(self, id_struttura, nome_pa, id_sezione, nome_sezione):

        self.id_struttura = id_struttura
        self.nome_pa = nome_pa
        self.id_sezione = id_sezione
        self.nome_sezione = nome_sezione

        chrome_driver = ChromeDriverManager().install()
        self.driver = Chrome(service=Service(chrome_driver)) 
        self.driver.implicitly_wait(30)
        self.driver.set_page_load_timeout(30) 
        self.wait = WebDriverWait(self.driver, 20)

        self.read_count = 0
        self.write_count = 0
        self.double_skipped_count = 0
        self.double_replaced_count = 0
        self.error_count = 0
        
        # Create a logger
        self.logger = logging.getLogger(f'{self.__class__.__name__}')
        self.logger.setLevel(logging.DEBUG)

        # Create console handler and set level to debug
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)

        # Create file handler and set level to error
        file_handler = logging.FileHandler('log.log')
        file_handler.setLevel(logging.ERROR)

        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(pathname)s:%(lineno)d- %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        # Add console handler and file handler to logger
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)

        # Test the logger
        self.logger.info('Running...')

    def report(self):
        self.logger.info("--------------------------------------------")
        self.logger.info(f" JOB {self.nome_pa} {self.nome_sezione}")
        self.logger.info("--------------------------------------------")
        self.logger.info(f'read..........:{self.read_count}')
        self.logger.info(f' written........:{self.write_count}')
        self.logger.info(f'     skipped double...:{self.double_skipped_count}')
        self.logger.info(f'     double...........:{self.double_replaced_count}')
        self.logger.info(f'     errors...........:{self.error_count}')
        self.logger.info("--------------------------------------------")
        self.logger.info('END')

        status_code = 0 if (self.error_count == 0) else -1

        print(f'EXIT: status_code={status_code}')

    def run(self):
        pass


    
      

