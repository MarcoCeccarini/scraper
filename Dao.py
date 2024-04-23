import psycopg2
from minio import Minio
from dotenv import load_dotenv
import os
from datetime import datetime
import logging


class Dao:

    def __init__(self, id_struttura, nome_pa, id_sezione, nome_sezione):

        self.logger = logging.getLogger(f'{self.__class__.__name__}')

        self.id_struttura = id_struttura
        self.id_sezione = id_sezione
        self.nome_pa = nome_pa
        self.nome_sezione = nome_sezione

        load_dotenv()
        
        self.minio_client = Minio(
            endpoint=os.getenv('MINIO_URL'),
            access_key=os.getenv('MINIO_ACCESS_KEY'),  # Access key of your MinIO server
            secret_key=os.getenv('MINIO_SECRET_KEY'),  # Secret key of your MinIO server
            secure=False,
        )

        self.conn = psycopg2.connect(
            dbname= os.getenv('POSTGRES_DB'),
            user=os.getenv('POSTGRES_ROOT_USER'),
            password=os.getenv('POSTGRES_ROOT_PASSWORD'),
            host=os.getenv('POSTGRES_HOST'),
            port=os.getenv('POSTGRES_PORT'),
        )

    def create_doc(self, dir, file_path, contenuto, link_pubblico, n_atto, utente_data_inserimento, utente_data_fine_val, id_struttura):
        sql = """INSERT INTO documenti (contenuto, link_pubblico, path_privato, desc_flower, n_atto, utente_data_inserimento, utente_data_fine_val, ammin_data_inserimento, id_sezione, id_struttura)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""
        with self.conn.cursor() as cursor:

            cursor.execute(sql, (contenuto, link_pubblico, file_path, None, n_atto, utente_data_inserimento, utente_data_fine_val, datetime.today().date(), self.id_sezione, id_struttura))

            self.minio_client.fput_object(
                bucket_name="italiatrasparente-dev",
                object_name=dir+"/"+contenuto,
                file_path=file_path
            )
    
    def create_struttura(self, id_sezione, level1, level2):
        with self.conn.cursor() as cursor:
                
            cursor.execute(query="SELECT max(CAST(id as INT)) FROM struttura")
        
            id_struttura = cursor.fetchone()[0] + 1

            sql = f"""INSERT INTO struttura(id, sottosezione_lv1, sottosezione_lv2, id_sezione) VALUES('{id_struttura}', '{level1}', '{level2}', '{id_sezione}')"""

            cursor.execute(query=sql)
               

    def get_doc(self, contenuto, link_pubblico):
        sql = """SELECT * FROM documenti WHERE contenuto = %s AND link_pubblico = %s;"""
        with self.conn.cursor() as cursor:
            cursor.execute(sql, (contenuto, link_pubblico))
            return cursor.fetchone()
        
    def get_struttura(self, level1, level2):
        sql = """SELECT * FROM struttura WHERE sottosezione_lv1 = %s AND sottosezione_lv2 = %s;"""
        with self.conn.cursor() as cursor:
            cursor.execute(sql, (level1, level2))
            return cursor.fetchone()
        
    def delete_doc(self, contenuto, link_pubblico):
        sql = """DELETE * FROM documenti WHERE contenuto = %s AND link_pubblico = %s;"""
        with self.conn.cursor() as cursor:
            cursor.execute(sql, (contenuto, link_pubblico))
        
    def commit(self):
        self.conn.commit()
        
            

    def __del__(self):
        self.conn.close()


