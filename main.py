import mariadb
import sys

try:
    #Aquí cambiais cada uno los valores para vuestras BD's locales
    conn = mariadb.connect(user="root",password="rosquilla1",host="127.0.0.1",port=3306,database="practica3")
    print("Conectado a la base de datos")
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)

cur = conn.cursor()
