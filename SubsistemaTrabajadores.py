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


