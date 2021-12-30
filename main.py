from contextlib import AsyncExitStack, aclosing
from typing import final
import mariadb
import sys
import os
import platform

def conexion():
    try:
        #Aquí cambiais cada uno los valores para vuestras BD's locales
        conn = mariadb.connect(user="root",password="rosquilla1",host="127.0.0.1",port=3306,database="practica3")
        print("Conectado a la base de datos.")
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(1)
    finally:
        return conn

def desconexion(conn):
    conn.commit()
    conn.close()
    borrarPantalla()
    print('Desconexión de la base de datos')

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
                Telefono VARCHAR (9) NOT NULL,
                PRIMARY KEY (DNI));''')

        cursor.execute('''CREATE TABLE TRABAJADORES(
                Nombre VARCHAR (20) NOT NULL,
                Apellido VARCHAR (40) NOT NULL,
                DNI VARCHAR (9) UNIQUE,
                Telefono VARCHAR (9) NOT NULL,
                Correo VARCHAR (40) NOT NULL
                NumeroCuenta VARCHAR (24) NOT NULL,
                IdentificadorSucursal VARCHAR (24),
                PRIMARY KEY (DNI));''')
        
        cursor.execute('''CREATE TABLE TURNOS(
                FechaInicio DATETIME,
                FechaFin DATETIME,
                DNI VARCHAR (9) REFERENCES TRABAJADORES(DNI),
                PRIMARY KEY (DNI, FechaInicio, FechaFin));''')
        conexion.commit()
    except mariadb.Error as error_tabla:
        print(f"Error al crear la tabla: {error_tabla}")

def subsistemaClientes(conexion):
    cursor = conexion.cursor()
    print("Usted a accedido al subsistema de gestión de clientes")
    salir_cli = False
    while not salir_cli:
        print("1.-Dar de alta a un nuevo cliente")
        print("2.-Dar de baja a un cliente")
        print("3.-Consultar datos personales de un cliente")
        print("4.-Modificar datos de un cliente")
        print("6.-Salir del subsistema clientes")
        opcion_cli = int(input("Introduce el número de la operación a realizar: "))
        if(opcion_cli==1):
            borrarPantalla()
            darAltaCliente(conexion)
        elif(opcion_cli==2):
            borrarPantalla()
            darBajaCliente(conexion)
        elif(opcion_cli==3):
            borrarPantalla()
            consultarDatosClientes(conexion)
        elif(opcion_cli==4):
            borrarPantalla()
            modificarDatosClientes(conexion)
        elif(opcion_cli==6):
            salir_cli = True
    
def darAltaCliente(conexion):
    cursor = conexion.cursor()
    print("Usted está dando de alta a un nuevo cliente")
    cursor.execute("SAVEPOINT alta_cliente")
    Nombre=input("Introduzca el nombre del nuevo cliente: ")
    Apellido=input("Introduzca el apellido del nuevo cliente: ")
    DNI=input("Introduzca el DNI del nuevo cliente: ")
    Telefono=input("Introduzca el telefono del nuevo cliente: ")
    try:
        cursor.execute("INSERT INTO CLIENTES (Nombre, Apellido, DNI, Telefono) VALUES('"+Nombre+"','"+Apellido+"','"+DNI+"','"+Telefono+"')")
        borrarPantalla()
        print("Cliente creado correctamente")
        print()
    except mariadb.Error as error_alta_cliente:
        borrarPantalla()
        print("Ha fallado el proceso de alta del cliente")
        print(error_alta_cliente)
        cursor.execute("ROLLBACK to alta_cliente")
    finally:
        conexion.commit()
    
def darBajaCliente(conexion):
    cursor = conexion.cursor()
    cursor.execute("SAVEPOINT baja_cliente")
    print("Usted está dando de baja a un cliente")
    DNI=input("Introduzca el DNI del cliente: ")
    try:
        cursor.execute("DELETE FROM CLIENTES WHERE DNI='"+DNI+"'")
        borrarPantalla()
        print("Se ha dado de baja al cliente correctamente")
        print()
    except mariadb.Error as error_baja_cliente:
        borrarPantalla()
        print("Ha fallado el proceso de baja del cliente")
        print(error_baja_cliente)
        cursor.execute("ROLLBACK to baja_cliente")
    finally:
        conexion.commit()

def consultarDatosClientes(conexion):
    cursor=conexion.cursor()
    cursor.execute("SAVEPOINT consulta_cliente")
    DNI = input("Introduzca el DNI del cliente sobre el que desea ver los datos: ")
    try:
        cursor.execute("SELECT * FROM CLIENTES where DNI='"+DNI+"'")
        borrarPantalla()
        usuario = cursor.fetchone()
        print(usuario)
        print()
    except mariadb.Error as error_consulta_cliente:
        borrarPantalla()
        print("Ha fallado el proceso de consulta de datos del cliente")
        print(error_consulta_cliente)
        cursor.execute("ROLLBACK TO consulta_cliente")

def modificarDatosClientes(conexion):
    cursor = conexion.cursor()
    print("Se encuentra usted en la funcionalidad de modificación de datos")
    DNI = input("Introduzca el DNI del cliente sobre el que quiere aplicar la modificacion de datos: ")
    salir_mod_cli = False
    while not salir_mod_cli:
        print("1.-Modificar Nombre.")
        print("2.-Modificar Apellidos.")
        print("3.-Modificar Telefono.")
        print("4.-Salir.")
        opcion_cli_mod = int(input("Introduce el número de la acción que desea llevar a cabo: "))
        if opcion_cli_mod==1:
            Nombre = input("Introduzca el nuevo nombre: ")
            cursor.execute("UPDATE CLIENTES SET Nombre='"+Nombre+"' WHERE DNI='"+DNI+"'")
            borrarPantalla()
        elif opcion_cli_mod==2:
            Apellido = input("Introduzca el nuevo apellido: ")
            cursor.execute("UPDATE CLIENTES SET Apellido='"+Apellido+"' WHERE DNI='"+DNI+"'")
            borrarPantalla()
        elif opcion_cli_mod==3:
            Telefono = input("Introduzca el nuevo número telefono: ")
            cursor.execute("UPDATE CLIENTES SET Telefono='"+Telefono+"' WHERE DNI='"+DNI+"'")
            borrarPantalla()
        elif opcion_cli_mod==4:
            borrarPantalla()
            conexion.commit()
            salir_mod_cli = True


# Nos conectamos a la base de datos

cnx = conexion()
salir = False

while not salir:
    borrarPantalla()
    print("Opciones:")
    print("1.-REINICIAR")
    print("2.-SUBSISTEMA TRABAJADORES")
    print("3.-SUBSISTEMA CLIENTES")
    print("4.-SUBSISTEMA SERVICIOS")
    print("5.-SUBSISTEMA CUENTAS")
    print("6.-SUBSISTEMA SUCURSALES")
    print("7.-SALIR")

    opcion = int(input("INTRODUCE EL NUMERO DE LA OPCIÓN: "))

    if opcion==1:
        borrarPantalla()
        reiniciar(cnx)
    elif opcion==2:
        borrarPantalla()
    elif opcion==3:
        borrarPantalla()
        subsistemaClientes(cnx)
    elif opcion==4:
        borrarPantalla()
    elif opcion==5:
        borrarPantalla()
    elif opcion==6:
        borrarPantalla()
    elif opcion==7:
        desconexion(cnx)
        salir = True
    else:
        print("Escribe una opción correcta")
