from contextlib import AsyncExitStack, aclosing
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

def subsistemaClientes(conexion):
    borrarPantalla()
    cursor = conexion.cursor()
    cursor.execute('SAVEPOINT inicio')
    print("Usted ha ingresado en el Subsitema de Clientes.")
    salir_clientes = False
    while not salir_clientes:
        print("1.-Dar de alta a un nuevo cliente")
        print("2.-Dar de baja a un cliente ya existente")
        print("3.-Consultar los datos de un cliente ya existente")
        print("4.-Alterar los datos de un cliente ya existente")
        print("5.-Listar las cuentas de un cliente")

        opcion_clientes = int(input("¿Qué operación desea realizar?:"))

        if opcion_clientes == 1:
            dardealtacliente(conexion)

def dardealtacliente(conexion):
    borrarPantalla()
    cursor = conexion.cursor()
    print("Se va a dar de alta a un nuevo cliente.")
    cursor.execute("SAVEPOINT alta_cliente")
    Nombre = input("Introduce el nombre del cliente: ")
    Apellido = input("Introduce el apellido del cliente: ")
    DNI = input("Introduce el DNI del cliente: ")
    Telefono = input("Introduce el Teléfono del cliente: ")
    
    try:
        cursor.execute("INSERT INTO CLIENTES (Nombre, Apellido, DNI, Teléfono) VALUES ('"+Nombre+"','"+Apellido+"','"+DNI+"','"+Telefono+"')")
        print("Se ha dado de alta al nuevo cliente correctamente")
    except mariadb.Error as error_alta_cliente:
        print("Ha fallado el proceso de alta al nuevo cliente")
        print(error_alta_cliente)
        cursor.execute("ROLLBACK TO SAVEPOINT alta_cliente")
    finally:
        subsistemaClientes(conexion)
        conexion.commit()
        cursor.close()


# Nos conectamos a la base de datos

cnx = conexion()
salir = False

while not salir:
    borrarPantalla()
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
        nada
    elif opcion==3:
        subsistemaClientes(cnx)
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