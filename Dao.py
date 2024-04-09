import psycopg2

class Dao:
    def __init__(self):
        self.conn = psycopg2.connect(
            dbname="italia-trasparente",
            user="harvester",
            password="harvester",
            host="10.20.4.5",
            port="30001"
        )

    def create_doc(self, contenuto, link_pubblico):
        try:
            sql = """INSERT INTO documenti (contenuto, link_pubblico) VALUES (%s, %s);"""
            with self.conn.cursor() as cursor:
                cursor.execute(sql, (contenuto, link_pubblico))
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

# Example usage:
dao = Dao()
# dao.create_doc("test", "www.example.com")
doc = dao.get_doc_by_id("test", "www.example.com")
print(doc)
