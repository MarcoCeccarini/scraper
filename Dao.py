import psycopg2
from minio import Minio
from dotenv import load_dotenv
import os

class Dao:

    def __init__(self):

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

    def create_doc(self, file_path, contenuto, link_pubblico, n_atto):
        try:
            sql = """INSERT INTO documenti (contenuto, link_pubblico, n_atto) VALUES (%s, %s, %s);"""
            with self.conn.cursor() as cursor:

                

                try:
                 self.minio_client.fput_object(
                    bucket_name="italiatrasparente",
                    object_name=contenuto,
                    file_path=file_path
                )
                except Exception as e:
                    raise e
                cursor.execute(sql, (contenuto, link_pubblico, n_atto))

            self.conn.commit()
        except psycopg2.Error as e:
            print(f'Error: {e}')


    def get_doc_by_id(self, contenuto, link_pubblico):
        sql = """SELECT * FROM documenti WHERE contenuto = %s AND link_pubblico = %s;"""
        with self.conn.cursor() as cursor:
            cursor.execute(sql, (contenuto, link_pubblico))
            return cursor.fetchone()

    # Add more methods for other CRUD operations as needed

    def __del__(self):
        self.conn.close()


