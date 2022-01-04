from contextlib import AsyncExitStack, aclosing
from typing import final
import mariadb
import sys
import os
import platform
from random import randint 

##############################################################
### CONEXIÓN ###
##############################################################

def conexion():
    try:
        #Aquí cambiais cada uno los valores para vuestras BD's locales
        conn = mariadb.connect(user="root",password="password",host="127.0.0.1",port=3306,database="pruebas")
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

##############################################################
### OTROS MÉTODOS ###
##############################################################
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
        cursor.execute('''DROP TABLE SUCURSALES;''')
        cursor.execute('''DROP TABLE TRABAJADORES;''')
        cursor.execute('''DROP TABLE TRABAJA;''')

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
                Correo VARCHAR (40) NOT NULL,
                NumeroCuenta VARCHAR (24) NOT NULL,
                PRIMARY KEY (DNI));''')
        
        cursor.execute('''CREATE TABLE TURNOS(
                FechaInicio DATETIME,
                FechaFin DATETIME,
                DNI VARCHAR (9) REFERENCES TRABAJADORES(DNI),
                PRIMARY KEY (DNI, FechaInicio, FechaFin));''')
        
        cursor.execute('''CREATE TABLE SUCURSALES(
                Direccion VARCHAR(40) NOT NULL,
                ID_Sucursal VARCHAR(10) UNIQUE NOT NULL,
                PRIMARY KEY (ID_Sucursal));''')
        
        cursor.execute('''CREATE TABLE TRABAJA(
                ID_Sucursal VARCHAR (10) NOT NULL,
                DNI VARCHAR(9) NOT NULL,
                FOREIGN KEY (ID_Sucursal) REFERENCES SUCURSALES(ID_Sucursal),
                FOREIGN KEY (DNI) REFERENCES TRABAJADORES(DNI));''')

        conexion.commit()
    except mariadb.Error as error_tabla:
        print(f"Error al crear la tabla: {error_tabla}")

##############################################################
### SUBSISTEMA CLIENTES ###
##############################################################

def subsistemaClientes(conexion):
    cursor = conexion.cursor()
    print("Usted ha accedido al subsistema de gestión de clientes")
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

##############################################################
### SUBSISTEMA SUCURSALES ###
##############################################################

def subsistemaSucursales(conexion):
    cursor = conexion.cursor()
    
    print("Usted ha accedido al Subsistema de Sucursales.\n")
    salir_cli = False

    while not salir_cli:
        print ("1.- Crear una nueva sucursal.")
        print ("2.- Eliminar una sucursal.")
        print ("3.- Asignar trabajadores a una sucursal.")
        print ("4.- Listar sucursales.")
        print ("5.- Consultar trabajadores de una sucursal.")
        print ("6.- Salir del Subsistema de Sucursales.\n")

        opcion_cli = int(input("Introduzca la opción a la que quiera acceder: "))

        if (opcion_cli == 1):
            borrarPantalla()
            crearSucursal(conexion)
        elif (opcion_cli == 2):
            borrarPantalla()
            eliminarSucursal(conexion)
        elif (opcion_cli == 3):
            borrarPantalla()
            asignarTrabajadores(conexion)
        elif (opcion_cli == 4):
            borrarPantalla()
            listarSucursales(conexion)
        elif (opcion_cli == 5):
            borrarPantalla()
            consultarTrabajadoresSucursal(conexion)
        elif (opcion_cli == 6):
            salir_cli = True

def random_n_digitos(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)

def crearSucursal(conexion):
    cursor = conexion.cursor()
    cursor.execute("SAVEPOINT crear_sucursal")
    borrarPantalla()

    Direccion = input("Para crear una sucursal debe proporcionar la dirección postal de la misma usando hasta 40 caracteres: ")
    ID_Sucursal = str(random_n_digitos(10))

    try:
        cursor.execute("INSERT INTO SUCURSALES (Direccion, ID_Sucursal) VALUES('"+Direccion+"','"+ID_Sucursal+"')")
        print("\nSucursal creada correctamente con los siguientes datos:")
        print("Dirección postal:",Direccion)
        print("ID de la sucursal generado automáticamente:",ID_Sucursal)
        print("\nVolviendo al menú anterior. \n")
    except mariadb.Error as error_crear_sucursal:
        print("Ha fallado el proceso de creación de una sucursal.\n")
        print(error_crear_sucursal, "\n")
        cursor.execute("ROLLBACK to crear_sucursal")
    finally:
        conexion.commit()

def eliminarSucursal(conexion):
    cursor = conexion.cursor()
    cursor.execute("SAVEPOINT eliminar_sucursal")
    borrarPantalla()

    ID_Sucursal = input("Para poder eliminar una sucursal debe proporcionar su ID: ")

    try:
        cursor.execute("DELETE FROM SUCURSALES WHERE ID_SUCURSAL = ('"+ID_Sucursal+"')")
        print("\nSucursal eliminada correctamente.")
        print("\nVolviendo al menú anterior. \n")
    except mariadb.Error as error_eliminar_sucursal:
        print("Ha fallado el proceso de eliminación de una sucursal.\n")
        print(error_eliminar_sucursal, "\n")
        cursor.execute("ROLLBACK to eliiminar_sucursal")
    finally:
        conexion.commit()

def listarSucursales(conexion):
    cursor = conexion.cursor()
    borrarPantalla()

    try:
        query = "SELECT * FROM SUCURSALES"
        cursor.execute(query)
        records = cursor.fetchall()

        print("\nLista de sucursales existentes:\n")

        print ("{:<40} {:<10}".format('Dirección','ID_Sucursal'))
        for record in records:
            Direccion, ID_Sucursal = record
            print("{:<40} {:<10}".format(Direccion, ID_Sucursal))
        print("\nVolviendo al menú anterior.\n")

    except mariadb.Error as error_mostrar_sucursales:
        print("Error al mostrar las sucursales.\n")
        print(error_mostrar_sucursales, "\n")

def asignarTrabajadores(conexion):
    cursor = conexion.cursor()
    cursor.execute("SAVEPOINT asignar_trabajador")
    borrarPantalla()
    
    ID_Sucursal = input("Introduzca el ID de la sucursal a la que desee asignar un trabajador: ")
    DNI = input("Introduzca el DNI del trabajador: ")

    try:
        cursor.execute("INSERT INTO TRABAJA (ID_Sucursal, DNI) VALUES('"+ID_Sucursal+"','"+DNI+"')")
        print("\nEl trabajador ha sido asignado a la sucursal correctamente.")
        print("\nVolviendo al menú anterior. \n")
    except mariadb.Error as error_asignar_sucursal:
        print("Ha fallado el proceso de asignación a una sucursal.\n")
        print(error_asignar_sucursal, "\n")
        cursor.execute("ROLLBACK to asignar_trabajador")
    finally:
        conexion.commit()

def consultarTrabajadoresSucursal(conexion):
    cursor = conexion.cursor()
    borrarPantalla()
    
    ID_Sucursal = input("Introduzca el ID de una sucursal: ")
    try:
        query = "SELECT DISTINCT TRABAJADORES.NOMBRE, TRABAJADORES.APELLIDO FROM TRABAJADORES INNER JOIN TRABAJA ON TRABAJADORES.DNI=TRABAJA.DNI WHERE ID_SUCURSAL=8269813641"
        cursor.execute(query)
        records = cursor.fetchall()

        print("\nLista de trabajadores de esta sucursal:\n")

        print ("{:<40} {:<10}".format('Nombre','Apellido'))
        for record in records:
            Nombre, Apellido = record
            print("{:<40} {:<10}".format(Nombre, Apellido))
        print("\nVolviendo al menú anterior.\n")

    except mariadb.Error as error_mostrar_trabajadores_sucursales:
        print("Error al mostrar los trabajadores.\n")
        print(error_mostrar_trabajadores_sucursales, "\n")

##############################################################
### SUBSISTEMA TRABAJADORES ###
##############################################################

def subsistemaTrabajadores(conexion):
    cursor = conexion.cursor()
    print("Usted a accedido al subsistema de gestión de Trabajadores")
    salir_Tra = False
    while not salir_Tra:
        print("1.-Dar de alta a un nuevo trabajador")
        print("2.-Dar de baja a un trabajador")
        print("3.-Consultar datos personales de un trabajador")
        print("4.-Modificar datos de un trabajador")
        print("6.-Salir del subsistema Trabajadores")
        opcion_Tra = int(input("Introduce el número de la operación a realizar: "))
        if(opcion_Tra==1):
            borrarPantalla()
            darAltaTrabajador(conexion)
        elif(opcion_Tra==2):
            borrarPantalla()
            darBajaTrabajador(conexion)
        elif(opcion_Tra==3):
            borrarPantalla()
            consultarDatosTrabajadores(conexion)
        elif(opcion_Tra==4):
            borrarPantalla()
            modificarDatosTrabajadores(conexion)
        elif(opcion_Tra==6):
            salir_Tra = True
    
def darAltaTrabajador(conexion):
    cursor = conexion.cursor()
    print("Usted está dando de alta a un nuevo trabajador")
    cursor.execute("SAVEPOINT alta_trabajador")
    Nombre=input("Introduzca el nombre del nuevo trabajador: ")
    Apellido=input("Introduzca el apellido del nuevo trabajador: ")
    DNI=input("Introduzca el DNI del nuevo trabajador: ")
    Telefono=input("Introduzca el telefono del nuevo trabajador: ")
    Correo=input("Introduzca la direccion de correo del nuevo trabajador: ")
    NumeroCuenta=input("Introduzca el numero de cuenta del nuevo trabajador: ")
    try:
        cursor.execute("INSERT INTO TRABAJADORES (Nombre, Apellido, DNI, Telefono, Correo, NumeroCuenta) VALUES('"+Nombre+"','"+Apellido+"','"+DNI+"','"+Telefono+"','"+Correo+"','"+NumeroCuenta+"')")
        borrarPantalla()
        print("trabajador creado correctamente")
        print()
    except mariadb.Error as error_alta_trabajador:
        borrarPantalla()
        print("Ha fallado el proceso de alta del trabajador")
        print(error_alta_trabajador)
        cursor.execute("ROLLBACK to alta_trabajador")
    finally:
        conexion.commit()
    
def darBajaTrabajador(conexion):
    cursor = conexion.cursor()
    cursor.execute("SAVEPOINT baja_trabajador")
    print("Usted está dando de baja a un trabajador")
    DNI=input("Introduzca el DNI del trabajador: ")
    try:
        cursor.execute("DELETE FROM TRABAJADORES WHERE DNI='"+DNI+"'")
        borrarPantalla()
        print("Se ha dado de baja al trabajador correctamente")
        print()
    except mariadb.Error as error_baja_trabajador:
        borrarPantalla()
        print("Ha fallado el proceso de baja del trabajador")
        print(error_baja_trabajador)
        cursor.execute("ROLLBACK to baja_trabajador")
    finally:
        conexion.commit()

def modificarDatosTrabajadores(conexion):
    cursor = conexion.cursor()
    print("Se encuentra usted en la funcionalidad de modificación de datos")
    DNI = input("Introduzca el DNI del trabajador sobre el que quiere aplicar la modificacion de datos: ")
    salir_mod_tra = False
    while not salir_mod_tra:
        print("1.-Modificar Nombre.")
        print("2.-Modificar Apellidos.")
        print("3.-Modificar Telefono.")
        print("4.-Modificar Correo.")
        print("5.-Modificar Nuemro de cuenta.")
        print("6.-Salir.")
        opcion_tra_mod = int(input("Introduce el número de la acción que desea llevar a cabo: "))
        if opcion_tra_mod==1:
            Nombre = input("Introduzca el nuevo nombre: ")
            cursor.execute("UPDATE TRABAJADORES SET Nombre='"+Nombre+"' WHERE DNI='"+DNI+"'")
            borrarPantalla()
        elif opcion_tra_mod==2:
            Apellido = input("Introduzca el nuevo apellido: ")
            cursor.execute("UPDATE TRABAJADORES SET Apellido='"+Apellido+"' WHERE DNI='"+DNI+"'")
            borrarPantalla()
        elif opcion_tra_mod==3:
            Telefono = input("Introduzca el nuevo número de telefono: ")
            cursor.execute("UPDATE TRABAJADORES SET Telefono='"+Telefono+"' WHERE DNI='"+DNI+"'")
            borrarPantalla()
        elif opcion_tra_mod==4:
            Correo=input("Introduzca la direccion de correo del nuevo trabajador: ")
            cursor.execute("UPDATE TRABAJADORES SET Correo='"+Correo+"' WHERE DNI='"+DNI+"'")
            borrarPantalla()
        elif opcion_tra_mod==5:
            NumeroCuenta=input("Introduzca el numero de cuenta del nuevo trabajador: ")
            cursor.execute("UPDATE TRABAJADORES SET NumeroCuenta='"+NumeroCuenta+"' WHERE DNI='"+DNI+"'")
            borrarPantalla()
        elif opcion_tra_mod==6:
            borrarPantalla()
            conexion.commit()
            salir_mod_tra = True

def asignarTurno(conexion):
    cursor = conexion.cursor()
    print("Usted está asignando un horario a un trabajador")
    cursor.execute("SAVEPOINT Turno")

    DNI=input("Introduzca el DNI del nuevo trabajador: ")
    print("Las fechas deben ingresarse con el iguiente formato 2012-04-19 13:08:22 y entre dobles comillas")
    #Ejemplo Datetime("2012-04-19 13:08:22")
    FechaInicio=input("Introduzca el inicio del turno: ")
    FechaFin=input("Introduzca el final del turno: ")

    try:
        cursor.execute("INSERT INTO TURNOS (FechaInicio, FechaFin, DNI) VALUES('"+FechaInicio+"','"+FechaFin+"','"+DNI+"')")
        borrarPantalla()
        print("Turno creado correctamente")
        print()
    except mariadb.Error as error_Turno:
        borrarPantalla()
        print("Ha fallado la asignacion de turnos")
        print(error_Turno)
        cursor.execute("ROLLBACK to Turno")
    finally:
        conexion.commit()

def consultarTrabajadoresLibres(conexion):
    cursor=conexion.cursor()
    cursor.execute("SAVEPOINT consulta_trabajador")
    print("Las fechas deben ingresarse con el iguiente formato 2012-04-19 13:08:22 y entre dobles comillas")
    FechaInicio=input("Introduzca el inicio del turno: ")
    try:
        cursor.execute("SELECT DNI FROM TRABAJADORES MINUS SELECT DNI FROM TURNOS where FechaInicio='"+FechaInicio+"'")
        borrarPantalla()
        usuario = cursor.fetchone()
        print(usuario)
        print()
    except mariadb.Error as error_consulta_trabajador:
        borrarPantalla()
        print("Ha fallado el proceso de consulta de los trabajadores")
        print(error_consulta_trabajador)
        cursor.execute("ROLLBACK TO consulta_trabajador")

##############################################################
### MENÚ PRINCIPAL ###
##############################################################

# Nos conectamos a la base de datos

cnx = conexion()
salir = False

while not salir:
    borrarPantalla()
    print("¡Bienvenido al Sistema Informático del Banco de España! Esperamos que no nos robe el oro.")
    print("\nA continuación se le muestran los subsistemas disponibles:")
    print("1.- REINICIAR")
    print("2.- SUBSISTEMA TRABAJADORES")
    print("3.- SUBSISTEMA CLIENTES")
    print("4.- SUBSISTEMA SERVICIOS")
    print("5.- SUBSISTEMA CUENTAS")
    print("6.- SUBSISTEMA SUCURSALES")
    print("7.- SALIR")

    opcion = int(input("\nIntroduzca el número del subsistema al que desee acceder: "))

    if opcion==1:
        borrarPantalla()
        reiniciar(cnx)
    elif opcion==2:
        borrarPantalla()
        subsistemaTrabajadores(cnx)
    elif opcion==3:
        borrarPantalla()
        subsistemaClientes(cnx)
    elif opcion==4:
        borrarPantalla()
    elif opcion==5:
        borrarPantalla()
    elif opcion==6:
        borrarPantalla()
        subsistemaSucursales(cnx)
    elif opcion==7:
        desconexion(cnx)
        salir = True
    else:
        print("ERROR: NO ES UNA OPCIÓN CORRECTA.")
