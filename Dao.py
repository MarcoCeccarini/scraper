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

    def create_doc(self, dir, file_path, contenuto, link_pubblico, n_atto, utente_data_inserimento, utente_data_fine_val):
        try:
            sql = """INSERT INTO documenti (contenuto, link_pubblico, path_privato, desc_flower, n_atto, utente_data_inserimento, utente_data_fine_val, ammin_data_inserimento, id_sezione, id_struttura)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"""
            with self.conn.cursor() as cursor:

                cursor.execute(sql, (contenuto, link_pubblico, file_path, None, n_atto, utente_data_inserimento, utente_data_fine_val, datetime.today().date(), self.id_sezione, self.id_struttura))

                try:
                 self.minio_client.fput_object(
                    bucket_name="italiatrasparente-dev",
                    object_name=dir+"/"+contenuto,
                    file_path=file_path
                )
                except Exception as e:
                    self.conn.rollback()
                    raise e

            self.conn.commit()
        except psycopg2.Error as e:
            self.logger.error(f'Error: {e}')


    def get_doc_by_id(self, contenuto, link_pubblico):
        sql = """SELECT * FROM documenti WHERE contenuto = %s AND link_pubblico = %s;"""
        with self.conn.cursor() as cursor:
            cursor.execute(sql, (contenuto, link_pubblico))
            return cursor.fetchone()

    # Add more methods for other CRUD operations as needed

    def __del__(self):
        self.conn.close()


