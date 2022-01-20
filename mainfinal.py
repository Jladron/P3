from asyncio.windows_events import NULL
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

        #Borramos todas las tablas
        cursor.execute('''DROP TABLE IF EXISTS ASOCIA''')
        cursor.execute('''DROP TABLE IF EXISTS TRABAJA;''')
        cursor.execute('''DROP TABLE IF EXISTS TURNOS;''')
        cursor.execute('''DROP TABLE IF EXISTS CUENTAS''')
        cursor.execute('''DROP TABLE IF EXISTS CUENTAS_BORRADAS''')
        cursor.execute('''DROP TABLE IF EXISTS SUCURSALES''')
        cursor.execute('''DROP TABLE IF EXISTS TRABAJADORES;''')
        cursor.execute('''DROP TABLE IF EXISTS CLIENTES;''')        
        cursor.execute('''DROP TABLE IF EXISTS SERVICIOS''')
        cursor.execute('''DROP TABLE IF EXISTS PERTENECE;''')
        
        #Creamos todas las tablas
        cursor.execute('''CREATE TABLE SERVICIOS(
                ID VARCHAR (20) UNIQUE,
                PRIMARY KEY (ID));
                ''')
        
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
                
        cursor.execute('''CREATE TABLE SUCURSALES(
                Direccion VARCHAR(40) NOT NULL,
                ID_Sucursal VARCHAR(10) UNIQUE NOT NULL,
                PRIMARY KEY (ID_Sucursal));''')
        
        cursor.execute('''CREATE TABLE CUENTAS(
                IBAN VARCHAR (24) UNIQUE,
                DNI_prop VARCHAR (9) NOT NULL,
                Saldo FLOAT,
                FOREIGN KEY (DNI_prop) REFERENCES CLIENTES(DNI),
                PRIMARY KEY (IBAN));
                ''')

        cursor.execute('''CREATE TABLE CUENTAS_BORRADAS(
                IBAN VARCHAR (24) UNIQUE,
                DNI_prop VARCHAR (9) NOT NULL,
                Saldo FLOAT,
                PRIMARY KEY (IBAN));
                ''')
                        
        cursor.execute('''CREATE TABLE TURNOS(
                FechaInicio DATETIME,
                FechaFin DATETIME,
                DNI VARCHAR (9) REFERENCES TRABAJADORES(DNI),
                PRIMARY KEY (DNI, FechaInicio, FechaFin));''')
        
        cursor.execute('''CREATE TABLE TRABAJA(
                ID_Sucursal VARCHAR (10) NOT NULL,
                DNI VARCHAR(9) NOT NULL,
                FOREIGN KEY (ID_Sucursal) REFERENCES SUCURSALES(ID_Sucursal),
                FOREIGN KEY (DNI) REFERENCES TRABAJADORES(DNI));''')
                
        cursor.execute('''CREATE TABLE ASOCIA(
                IBAN VARCHAR (24) NOT NULL,
                ID_SERVICIO VARCHAR (20) NOT NULL,
                PRIMARY KEY (IBAN, ID_SERVICIO),
                FOREIGN KEY (IBAN) REFERENCES CUENTAS(IBAN),
                FOREIGN KEY (ID_SERVICIO) REFERENCES SERVICIOS(ID));
                ''')

        cursor.execute('''CREATE TABLE PERTENECE(
                DNI VARCHAR (9) NOT NULL,
                IBAN VARCHAR (24) UNIQUE NOT NULL,
                FOREIGN KEY (IBAN) REFERENCES CUENTAS(IBAN),
                FOREIGN KEY (DNI) REFERENCES CLIENTES(DNI),
                PRIMARY KEY (DNI, IBAN));''')

        #Triggers
        triggerCuentas(conexion)
        triggerTrabajadores(conexion)
        triggerSucursales(conexion)

        #Tuplas para pruebas
        #Dueño del banco
        cursor.execute('''INSERT INTO CLIENTES (Nombre, Apellido, DNI, Telefono) VALUES
                ('José',
                'Morón',
                '77148388V',
                '722445823')''')

        #Cuenta del banco                
        cursor.execute('''INSERT INTO CUENTAS (IBAN, DNI_prop, Saldo) VALUES
                ('000000000000000000000000',
                '77148388V',
                '99999')''')

        #Cuentas de prueba
        cursor.execute('''INSERT INTO CUENTAS (IBAN, DNI_prop, Saldo) VALUES
                ('100000000000000000000000',
                '77148388V',
                '100')''')
        cursor.execute('''INSERT INTO CUENTAS (IBAN, DNI_prop, Saldo) VALUES
                ('200000000000000000000000',
                '77148388V',
                '-100')''')

        #Primer trabajador
        cursor.execute('''INSERT INTO TRABAJADORES (Nombre, Apellido, DNI, Telefono, Correo, NumeroCuenta) VALUES
                ('Domingo',
                'Rodriguez',
                '69876955T',
                '698584237',
                'drodriguez@gmail.com',
                '100000000000000000000000')''')

        #Turno del primer trabajador
        cursor.execute('''INSERT INTO TURNOS (FechaInicio, FechaFin, DNI) VALUES
                ("2022-01-19 12:00:00", "2023-01-19 12:00:00", '69876955T')''')

        #Servicio basico
        cursor.execute('''INSERT INTO SERVICIOS (ID) VALUES ('0')
                '''
        )

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
        print("1.- Dar de alta a un nuevo cliente.")
        print("2.- Dar de baja a un cliente.")
        print("3.- Consultar datos personales de un cliente.")
        print("4.- Modificar datos de un cliente.")
        print("5.- Listar cuentas de un cliente. ")
        print("9.- Salir del subsistema clientes.")
        opcion_cli = int(input("Introduzca el número de la operación a realizar: "))
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
        elif(opcion_cli==9):
            salir_cli = True
    
def darAltaCliente(conexion):
    cursor = conexion.cursor()
    print("Usted está dando de alta a un nuevo cliente")
    cursor.execute("SAVEPOINT alta_cliente")
    Nombre=input("Introduzca el nombre del nuevo cliente: ")
    Apellido=input("Introduzca el apellido del nuevo cliente: ")
    DNI=input("Introduzca el DNI del nuevo cliente: ")
    Telefono=input("Introduzca el teléfono del nuevo cliente: ")
    try:
        cursor.execute("INSERT INTO CLIENTES (Nombre, Apellido, DNI, Telefono) VALUES('"+Nombre+"','"+Apellido+"','"+DNI+"','"+Telefono+"')")
        borrarPantalla()
        print("Cliente creado correctamente")
        cursor.execute("SELECT COUNT(IBAN) FROM cuentas")
        IBAN = int(str(cursor.fetchone()).replace("(", "").replace(")", "").replace(",",""))
        cursor.execute("SELECT COUNT(IBAN) FROM cuentas_borradas")
        IBAN = IBAN + int(str(cursor.fetchone()).replace("(", "").replace(")", "").replace(",",""))
        for x in range(24-len(str(IBAN))):
            IBAN = str(IBAN)+"0"
        cursor.close()
        cursor = conexion.cursor()
        saldo=0
        cursor.execute("INSERT INTO CUENTAS (IBAN, DNI_prop, Saldo) VALUES('"+IBAN+"','"+DNI+"', '"+str(saldo)+"')")
        print("Cuenta creada correctamente")

        cursor.execute("INSERT INTO PERTENECE (DNI, IBAN) VALUES('"+DNI+"','"+IBAN+"')")

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
    DNI = input("Introduzca el DNI del cliente que desea dar de baja: ")
    try:
        condicion = True
        while condicion:
            IBAN = str(str(cursor.fetchone()).replace("(", "").replace(")", "").replace(",","").replace("'",""))
            cursor.execute("DELETE FROM PERTENECE WHERE IBAN='"+IBAN+"'")
            cursor.execute("DELETE FROM CUENTAS WHERE IBAN='"+IBAN+"'")

        cursor.execute("DELETE FROM CLIENTES WHERE DNI='"+DNI+"'")
        borrarPantalla()
        print("Se ha dado de baja al cliente y todas sus cuentas. ")

    except mariadb.Error as error_baja_cliente:
        borrarPantalla()
        print("Ha fallado el proceso de baja de cliente.")
        print(error_baja_cliente)
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
        print("Ha fallado el proceso de consulta de datos del cliente.")
        print(error_consulta_cliente)
        cursor.execute("ROLLBACK TO consulta_cliente")

def modificarDatosClientes(conexion):
    cursor = conexion.cursor()
    print("Se encuentra usted en la funcionalidad de modificación de datos")
    DNI = input("Introduzca el DNI del cliente sobre el que quiere aplicar la modificación de datos: ")
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
        print ("9.- Salir del Subsistema de Sucursales.\n")

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
        elif (opcion_cli == 9):
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

def triggerSucursales(conexion):
    cursor = conexion.cursor()
    
    cursor.execute('''
                    CREATE DEFINER='root'@'localhost' TRIGER 'trigger_Sucursales'
                        BEFORE INSERT on SUCURSALES
                        FOR EACH ROW
                    BEGIN
                        IF EXISTS (SELECT DIRECCION FROM SUCURSALES WHERE DIRECCION = ('"+DIRECCION+"')) THEN
                            signal sqlstate '23000' set message_text = 'La dirección postal introducida se encuentra en uso. Introduzca una nueva para poder completar el proceso.';
                        END IF;
                        IF EXISTS (SELECT ID_Sucursal FROM SUCURSALES WHERE ID_Sucursal = ('"+ID_Sucursal+"')) THEN
                            signal sqlstate '23600' set message_text = 'Ha fallado el proceso de asignación de ID para la sucursal. Inténtelo de nuevo.';
                        END IF;
                     END;''')
                          
##############################################################
### SUBSISTEMA TRABAJADORES ###
##############################################################

def subsistemaTrabajadores(conexion):
    cursor = conexion.cursor()
    print("Usted a accedido al subsistema de gestión de Trabajadores")
    salir_Tra = False
    while not salir_Tra:
        print("1.- Dar de alta a un nuevo trabajador.")
        print("2.- Dar de baja a un trabajador.")
        print("3.- Consultar datos personales de un trabajador.")
        print("4.- Modificar datos de un trabajador.")
        print("5.- Asignar turno a trabajador.")
        print("9.- Salir del Subsistema Trabajadores.\n")
        opcion_Tra = int(input("Introduzca el número de la operación a realizar: "))
        if(opcion_Tra==1):
            borrarPantalla()
            darAltaTrabajador(conexion)
        elif(opcion_Tra==2):
            borrarPantalla()
            darBajaTrabajador(conexion)
        elif(opcion_Tra==3):
            borrarPantalla()
            consultarTrabajadoresLibres(conexion)
        elif(opcion_Tra==4):
            borrarPantalla()
            modificarDatosTrabajadores(conexion)
        elif(opcion_Tra==5):
            borrarPantalla()
            asignarTurno(conexion)
        elif(opcion_Tra==9):
            salir_Tra = True
    
def darAltaTrabajador(conexion):
    cursor = conexion.cursor()
    print("Usted está dando de alta a un nuevo trabajador.")
    cursor.execute("SAVEPOINT alta_trabajador")
    Nombre=input("Introduzca el nombre del nuevo trabajador: ")
    Apellido=input("Introduzca el apellido del nuevo trabajador: ")
    DNI=input("Introduzca el DNI del nuevo trabajador: ")
    Telefono=input("Introduzca el teléfono del nuevo trabajador: ")
    Correo=input("Introduzca la dirección de correo del nuevo trabajador: ")
    NumeroCuenta=input("Introduzca el numero de cuenta del nuevo trabajador: ")
    try:
        cursor.execute("INSERT INTO TRABAJADORES (Nombre, Apellido, DNI, Telefono, Correo, NumeroCuenta) VALUES('"+Nombre+"','"+Apellido+"','"+DNI+"','"+Telefono+"','"+Correo+"','"+NumeroCuenta+"')")
        borrarPantalla()
        print("Trabajador creado correctamente.")
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
    print("Usted está dando de baja a un trabajador.")
    DNI=input("Introduzca el DNI del trabajador: ")
    try:
        cursor.execute("DELETE FROM TRABAJADORES WHERE DNI='"+DNI+"'")
        borrarPantalla()
        print("Se ha dado de baja al trabajador correctamente.")
        print()
    except mariadb.Error as error_baja_trabajador:
        borrarPantalla()
        print("Ha fallado el proceso de baja del trabajador.")
        print(error_baja_trabajador)
        cursor.execute("ROLLBACK to baja_trabajador")
    finally:
        conexion.commit()

def modificarDatosTrabajadores(conexion):
    cursor = conexion.cursor()
    print("Se encuentra usted en la funcionalidad de modificación de datos.")
    DNI = input("Introduzca el DNI del trabajador sobre el que quiere aplicar la modificación de datos: ")
    salir_mod_tra = False
    while not salir_mod_tra:
        print("1.-Modificar Nombre.")
        print("2.-Modificar Apellidos.")
        print("3.-Modificar Telefono.")
        print("4.-Modificar Correo.")
        print("5.-Modificar Número de cuenta.")
        print("6.-Salir.")
        opcion_tra_mod = int(input("Introduzca el número de la acción que desea llevar a cabo: "))
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
            Correo=input("Introduzca la dirección de correo del nuevo trabajador: ")
            cursor.execute("UPDATE TRABAJADORES SET Correo='"+Correo+"' WHERE DNI='"+DNI+"'")
            borrarPantalla()
        elif opcion_tra_mod==5:
            NumeroCuenta=input("Introduzca el número de cuenta del nuevo trabajador: ")
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
    print("Las fechas deben ingresarse con el siguiente formato 2012-04-19 13:08:22 y entre dobles comillas.")
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
        print("Ha fallado la asignacion de turnos.")
        print(error_Turno)
        cursor.execute("ROLLBACK to Turno")
    finally:
        conexion.commit()

def consultarTrabajadoresLibres(conexion):
    cursor=conexion.cursor()
    cursor.execute("SAVEPOINT consulta_trabajador")
    print("Las fechas deben ingresarse con el siguiente formato 2012-04-19 13:08:22 y entre dobles comillas.")
    FechaInicio=input("Introduzca el inicio del turno: ")
    try:
        cursor.execute("SELECT DNI FROM TRABAJADORES MINUS SELECT DNI FROM TURNOS where FechaInicio='"+FechaInicio+"'")
        borrarPantalla()
        usuario = cursor.fetchone()
        print(usuario)
        print()
    except mariadb.Error as error_consulta_trabajador:
        borrarPantalla()
        print("Ha fallado el proceso de consulta de los trabajadores.")
        print(error_consulta_trabajador)
        cursor.execute("ROLLBACK TO consulta_trabajador")

def triggerTrabajadores(conexion):
    cursor = conexion.cursor()

    cursor.execute('''
                    CREATE DEFINER=`root`@`localhost` TRIGGER `trigger_trabajadores` BEFORE INSERT ON `turnos` FOR EACH ROW BEGIN

                        DECLARE rowcount INT;
                        SET rowcount = (SELECT COUNT(*)
                        FROM turnos
                        WHERE((DNI = NEW.DNI) 
                        AND((NEW.FechaInicio BETWEEN FechaInicio AND FechaFin)
                        OR (NEW.FechaFin BETWEEN FechaInicio AND FechaFin))
                        ));
                            
                        IF rowcount > 0 THEN
                            signal sqlstate '20000' set message_text = 'El turno declarado se sobrepone a uno existente';
                        END IF; 

                    END
                    ''')

##############################################################
### SUBSISTEMA CUENTAS ###
##############################################################

def subsistemaCuentas(conexion):
    cursor = conexion.cursor()
    print("Usted a accedido al subsistema de gestión de cuentas")
    salir_cuentas = False
    while not salir_cuentas:
        print("1.-Crear cuenta")
        print("2.-Eliminar cuenta")
        print("3.-Consultar saldo")
        print("4.-Modificar saldo")
        print("5.-Agregar servicio")
        print("6.-Salir del subsistema cuentas")

        opcion = int(input("Introduce el número de la operación a realizar: "))

        if(opcion==1):
            borrarPantalla()
            crearCuenta(conexion)
        elif(opcion==2):
            borrarPantalla()
            eliminarCuenta(conexion)
        elif(opcion==3):
            borrarPantalla()
            consultarSaldo(conexion)
        elif(opcion==4):  
            borrarPantalla()
            modificarSaldo(conexion)
        elif(opcion==5):
            borrarPantalla()
            agregarServicio(conexion)
        elif(opcion==9):
            borrarPantalla()
            salir_cuentas = True

def crearCuenta(conexion):
    cursor = conexion.cursor()
    print("Usted está creando una cuenta")
    cursor.execute("SAVEPOINT crear_cuenta")
    DNI=input("Introduzca el DNI del propietario de la cuenta: ")

    try:
        #El IBAN es incremental, depende del numero de cuenta que hayan sido creadas
        cursor.execute("SELECT COUNT(IBAN) FROM cuentas")
        IBAN = int(str(cursor.fetchone()).replace("(", "").replace(")", "").replace(",",""))
        cursor.execute("SELECT COUNT(IBAN) FROM cuentas_borradas")
        IBAN = IBAN + int(str(cursor.fetchone()).replace("(", "").replace(")", "").replace(",",""))
        for x in range(24-len(str(IBAN))):
            IBAN = str(IBAN)+"0"
        
        cursor.close()
        cursor = conexion.cursor()

        saldo=0
        cursor.execute("INSERT INTO CUENTAS (IBAN, DNI_prop, Saldo) VALUES('"+IBAN+"','"+DNI+"', '"+str(saldo)+"')")
        cursor.execute("INSERT INTO PERTENECE (DNI, IBAN) VALUES('"+DNI+"','"+IBAN+"')")
        borrarPantalla()
        print("Cuenta creada correctamente")
        print()
    except mariadb.Error as error_crear_cuenta:
        borrarPantalla()
        print("Ha fallado el proceso de creación de la cuenta, asegurese de que el propietario de la cuenta sea cliente.")
        print(error_crear_cuenta)
        cursor.execute("ROLLBACK TO crear_cuenta")
    finally:
        print("IBAN de cuenta: " + IBAN);
        conexion.commit()

def eliminarCuenta(conexion):
    cursor = conexion.cursor()
    cursor.execute("SAVEPOINT eliminar_cuenta")
    print("Usted está eliminando una cuenta")
    IBAN=input("Introduzca el IBAN de la cuenta: ")
    for x in range(24-len(IBAN)):
            IBAN = IBAN+"0"
    try:
        cursor.execute("SELECT Saldo FROM CUENTAS where IBAN='"+IBAN+"'")
        saldo = str(cursor.fetchone()).replace("(", "").replace(")", "").replace(",","")
        if float(saldo) >= 0 : 
            cursor.execute("UPDATE CUENTAS SET saldo = (SELECT Saldo FROM CUENTAS where IBAN='"+IBAN+"') + (SELECT Saldo FROM CUENTAS where IBAN='000000000000000000000000') WHERE IBAN='000000000000000000000000';")
            cursor.execute("DELETE FROM CUENTAS WHERE IBAN='"+IBAN+"'")
            borrarPantalla()
            print("Se ha eliminado la cuenta correctamente")
        else:
            cursor.execute("ROLLBACK to eliminar_cuenta")
            print("No puede eliminar una cuenta con saldo negativo")
        print()
    except mariadb.Error as error_eliminar_cuenta:
        borrarPantalla()
        print("Ha fallado el proceso de eliminación de cuenta")
        print(error_eliminar_cuenta)
        cursor.execute("ROLLBACK to eliminar_cuenta")
    finally:
        conexion.commit()

def consultarSaldo(conexion):
    cursor=conexion.cursor()
    cursor.execute("SAVEPOINT consulta_saldo")
    IBAN = input("Introduzca el IBAN de la cuenta: ")
    for x in range(24-len(IBAN)):
            IBAN = IBAN+"0"
    try:
        cursor.execute("SELECT Saldo FROM CUENTAS where IBAN='"+IBAN+"'")
        borrarPantalla()
        saldo = str(cursor.fetchone()).replace("(", "").replace(")", "").replace(",","")+"€"
        print("Su saldo: "+saldo)
        print()
    except mariadb.Error as error_consulta_saldo:
        borrarPantalla()
        print("Ha fallado el proceso de consulta")
        print(error_consulta_saldo)
        cursor.execute("ROLLBACK TO consulta_saldo")

def modificarSaldo(conexion):
    cursor=conexion.cursor()
    cursor.execute("SAVEPOINT modificar_saldo")
    borrarPantalla()

    try:
        IBAN = input("Introduzca el IBAN de la cuenta: ")
        for x in range(24-len(IBAN)):
            IBAN = IBAN+"0"

        cursor.close()
        cursor = conexion.cursor()

        cursor.execute("SELECT saldo FROM CUENTAS WHERE IBAN="+IBAN)
        
        saldo_actual = float(str(cursor.fetchone()).replace("(", "").replace(")", "").replace(",",""))


        saldo = saldo_actual + float(input("Indique la cantidad a ingresar/retirar(-): "))
        
        cursor.close()
        cursor = conexion.cursor()
        borrarPantalla()
        if (saldo >= 0):
            cursor.execute("UPDATE CUENTAS SET Saldo='"+str(saldo)+"' WHERE IBAN='"+IBAN+"'")
            print("Sueldo modificado correctamente")
        else:
            print("El saldo no puede quedar negativo")
        
        cursor.close()
        cursor = conexion.cursor()

    except mariadb.Error as error_modificar_saldo:
        borrarPantalla()
        print("Ha fallado el proceso de modificar saldo")
        print(error_modificar_saldo)
        cursor.execute("ROLLBACK to eliminar_cuenta")
        
    finally:
        conexion.commit()

def agregarServicio(conexion):
    cursor = conexion.cursor()
    cursor.execute("SAVEPOINT agregar_cuenta")

    try:
        IBAN = input("¿Que cuenta quiere vincular?: ")
        ID_servicio = input("¿Que servicio quiere vincular?: ")
        cursor.execute("INSERT INTO ASOCIA (IBAN, ID_SERVICIO) VALUES ('"+IBAN+"','"+ID_servicio+"')")

    except mariadb.Error as error_agregar_cuenta:
        borrarPantalla()
        print("Ha fallado el proceso de agregar servicio a la cuenta")
        print(error_agregar_cuenta)
        cursor.execute("ROLLBACK TO agregar_cuenta")

    finally:
        conexion.commit()

def triggerCuentas(conexion):
    cursor = conexion.cursor()

    cursor.execute('''
                    CREATE DEFINER=`root`@`localhost` TRIGGER `trigger_cuentas` BEFORE DELETE ON `cuentas` FOR EACH ROW BEGIN

                    INSERT INTO cuentas_borradas (IBAN, DNI_prop, Saldo)
                    VALUES (OLD.IBAN, OLD.DNI_prop, OLD.Saldo);

                    END
                    ''')

##############################################################
### MENÚ PRINCIPAL ###
##############################################################

# Nos conectamos a la base de datos

cnx = conexion()
salir = False

while not salir:
    borrarPantalla()
    print("¡Bienvenido al Sistema Informático del Banco de España! Esperamos que no nos robe el oro.")
    print("\nA continuación se le muestran las opciones disponibles:")
    print("0.- REINICIAR")
    print("1.- SUBSISTEMA TRABAJADORES")
    print("2.- SUBSISTEMA CLIENTES")
    print("3.- SUBSISTEMA SERVICIOS")
    print("4.- SUBSISTEMA CUENTAS")
    print("5.- SUBSISTEMA SUCURSALES")
    print("9.- SALIR")

    opcion = int(input("\nIntroduzca el número del subsistema al que desea acceder: "))

    if opcion==0:
        borrarPantalla()
        reiniciar(cnx)
    elif opcion==1:
        borrarPantalla()
        subsistemaTrabajadores(cnx)
    elif opcion==2:
        borrarPantalla()
        subsistemaClientes(cnx)
    elif opcion==3:
        borrarPantalla()
    elif opcion==4:
        borrarPantalla()
        subsistemaCuentas(cnx)
    elif opcion==5:
        borrarPantalla()
        subsistemaSucursales(cnx)
    elif opcion==9:
        desconexion(cnx)
        salir = True
    else:
        print("ERROR: NO ES UNA OPCIÓN CORRECTA.")
