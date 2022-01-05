import mariadb
import os


def subsistemaTrabajadores():
    #CONEXIÓN DE LA BASE DE DATOS
    conexion = connection()
    cur= conexion.cursor()
    menu(conexion)
    desconexion(conexion)




def menu(conexion):
    print("SUBSISTEMA DE SERVICIOS")

    salir=False

    while not salir:
        print("OPCIONES:")
        print("1.-CREAR SERVICIO")
        print("2.-DAR DE BAJA UN SERVICIO")
        print("3.-MODIFICAR SERVICIO")
        print("4.-CONSULTAR SERVICIOS ACTIVOS")
        print("5.-CONSULTAR SERVICIOS INACTIVOS")
        print("6.-VOLVER")

        opcion = int(input("INTRODUCE EL NUMERO DE LA OPCION: "))
        os.system("cls")
        #SORPRENDENTEMENTE NO EXISTE SWITCH EN PYTHON

        if opcion == 1:
            crearServicio(conexion)

        elif opcion == 2:
            idServicio = int(input("INTRODUCE EL ID DEL SERVICIO QUE QUIERES DAR DE BAJA: "))
            darBajaServicio(idServicio,conexion)

        elif opcion == 3:
            idServicio = int(input("INTRODUCE EL ID DEL SERVICIO QUE QUIERES MODIFICAR: "))
            modificarServicio(idServicio, conexion)

        elif opcion==4:
            consultarServiciosActivos(conexion)
        
        elif opcion==5:
            consultarServiciosInactivos(conexion)
        elif opcion==6:
            salir = True
            
        else:
            print("Escribe una opcion correcta")


def darBajaServicio(idServicio,conexion):
    cur=conexion.cursor()
    query='UPDATE `servicio` SET `estado`="inactivo" WHERE `id_servicio`='+ str(idServicio)
    cur.execute(query)
    print("SERVICIO ACTUALIZADO")
    cur.close()

def consultarServiciosActivos(conexion):
    cur=conexion.cursor()
    query='SELECT `nombre_servicio`,`id_servicio`,`descripcion`,`estado` FROM `servicio` WHERE `estado`="activo"'
    print("SERVICIOS ACTIVOS")
    cur.execute(query)
    for (nombre,idServicio, descripcion, estado)in cur:
        print("")
        print("nombre = ",nombre)
        print("id servicio = ",idServicio)
        print("estado = ", estado)
        print("descripcion = ", descripcion)
    print("")
    cur.close()

def consultarServiciosInactivos(conexion):
    cur=conexion.cursor()
    query='SELECT `nombre_servicio`,`descripcion`,`estado` FROM `servicio` WHERE `estado`="inactivo"'
    print("SERVICIOS INACTIVOS")
    cur.execute(query)
    for (nombre, descripcion, estado)in cur:
        print("")
        print("nombre = ",nombre)
        print("estado = ", estado)
        print("descripcion = ", descripcion)
    print("")
    cur.close()

def crearServicio(conexion):
    cur=conexion.cursor()
    nombre=input("INTRODUCE EL NOMBRE DEL SERVICIO: ")
    descripcion=input("INTRODUCE UNA DESCRIPCION DE SERVICIO (1000 CARACTERES MAX)")
    query='INSERT INTO `servicio` (`id_servicio`, `nombre_servicio`, `descripcion`, `estado`) VALUES (NULL, "'+nombre+'", "'+descripcion+'", "activo")'
    cur.execute(query)
    cur.close()


def modificarServicio(idServicio, conexion):
    cur=conexion.cursor()
    #COMPROBAR 1º SI EL ID ES VÁLIDO EN ESE CASO HACER ROLLBACK
    fin=False
    while not fin:
        print("¿QUE QUIERE MODIFICAR?:")
        print("1.-NOMBRE SERVICIO")
        print("2.-DESCRIPCION")
        print("3.-LOS DOS")
        print("4.-VOLVER")

        opcion = int(input("INTRODUCE EL NUMERO DE LA OPCION: "))
        os.system("cls")

        if opcion==1:
            nombre=input("INTRODUCE EL NOMBRE DEL SERVICIO: ")
            query='UPDATE `servicio` SET `nombre_servicio`='+nombre+' WHERE `id_servicio`='+str(idServicio)
            cur.execute(query)
            fin=True
        elif opcion==2:
            descripcion=input("INTRODUCE UNA DESCRIPCION DE SERVICIO (1000 CARACTERES MAX)")
            query='UPDATE `servicio` SET `descripcion`='+descripcion+' WHERE `id_servicio`='+str(idServicio)
            cur.execute(query)
            fin=True
        elif opcion==3:
            nombre=input("INTRODUCE EL NOMBRE DEL SERVICIO: ")
            descripcion=input("INTRODUCE UNA DESCRIPCION DE SERVICIO (1000 CARACTERES MAX)")
            query='UPDATE `servicio` SET `nombre_servicio`='+nombre+',`descripcion`='+descripcion+'  WHERE `id_servicio`='+str(idServicio)
            cur.execute(query)
            fin=True
        elif opcion==4:
            print("NO HAS MODIFICADO NADA")
            fin=True
        else:   
            print("INTRODUCE UNA OPCIÓN VALIDA")

    conexion.commit()
    cur.close()

def connection():
    try:
        conn=mariadb.connect(
            host="localhost",
            user="root",
            password="",
            database="brokers"
        )
        print("Conexion a la base de datos con exito")
    except mariadb.Error as e:
        print("Error de conexion base de datos ",e)
    finally:
        return conn

def desconexion(conexion):
    conexion.commit()
    conexion.close()
    print('Desconexion de la base de datos')

#PROGRAMA

subsistemaTrabajadores()