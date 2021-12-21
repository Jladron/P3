from contextlib import aclosing
import mariadb
import sys
import os
import platform

def conexion():
    try:
        #Aquí cambiais cada uno los valores para vuestras BD's locales
        conn = mariadb.connect(user="root",password="rosquilla1",host="127.0.0.1",port=3306,database="practica3")
        print("Conectado a la base de datos")
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(1)
    finally:
        return conn

def desconexion(conn):
    conn.commit()
    conn.close()
    print('Desconexion de la base de datos')

def borrarPantalla():
    if os.name == "posix":
        os.system("clear")
    else:
        os.system("cls")

# Para reiniciar tablas
def reiniciar(conexion):
    try:
        cursor = conexion.cursor()

        cursor.execute('''DROP TABLE CLIENTES;''')

        cursor.execute('''CREATE TABLE CLIENTES(
                Nombre VARCHAR (20) NOT NULL,
                Apellido VARCHAR (40) NOT NULL,
                DNI VARCHAR (9) UNIQUE,
                Teléfono VARCHAR (9) NOT NULL,
                PRIMARY KEY (DNI));''')
        conexion.commit()
    except mariadb.Error as error_tabla:
        print(f"Error al crear la tabla: {error_tabla}")

def crearTablaClientes(conexion):
    print()

# Nos conectamos a la base de datos

cnx = conexion()
borrarPantalla()
salir = False

while not salir:
    print("Opciones:")
    print("1.-REINICIAR")
    print("2.-")
    print("3.-SUBSISTEMA CLIENTES")
    print("4.-")
    print("5.-")
    print("6.-")
    print("7.-SALIR")

    opcion = int(input("INTRODUCE EL NUMERO DE LA OPCIÓN: "))
    borrarPantalla

    if opcion==1:
        reiniciar(cnx)
    elif opcion==2:
        crearTablaClientes(cnx)
    elif opcion==3:
        nada
    elif opcion==4:
        nada
    elif opcion==5:
        nada
    elif opcion==6:
        nada
    elif opcion==7:
        desconexion(cnx)
        salir = True
    else:
        print("Escribe una opción correcta")