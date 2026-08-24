# coding=utf-8
#!/usr/bin/env python3

import socket
import selectors    #https://docs.python.org/3/library/selectors.html
import select
import types        # Para definir el tipo de datos data
import argparse     # Leer parametros de ejecución
import os           # Obtener ruta y extension
from datetime import datetime, timedelta # Fechas de los mensajes HTTP
import time         # Timeout conexión
import sys          # sys.exit
import re           # Analizador sintáctico
import logging      # Para imprimir logs



BUFSIZE = 8192 # Tamaño máximo del buffer que se puede utilizar
TIMEOUT_CONNECTION = 41 # Timout para la conexión persistente 8+9+5+9+10
MAX_ACCESOS = 10

# Extensiones admitidas (extension, name in HTTP)
filetypes = {"gif":"image/gif", "jpg":"image/jpg", "jpeg":"image/jpeg", "png":"image/png", "htm":"text/htm",
             "html":"text/html", "css":"text/css", "js":"text/js"}

# Configuración de logging
logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s.%(msecs)03d] [%(levelname)-7s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger()


def enviar_mensaje(cs, data):
    if not isinstance(data, bytes):
        data = data.encode()
    return cs.send(data)


def recibir_mensaje(cs):
    datosLeidos = cs.recv(BUFSIZE)
    return datosLeidos.decode()


def cerrar_conexion(cs):
    cs.close()


def process_cookies(headers):
    patron_cookiecounter = r'cookie_counter_8959=\d+'
    er_cookie = re.compile(patron_cookiecounter)
    resultado = er_cookie.search(headers)
    if resultado:
        valor_cookie_counter = int(headers[resultado.start():resultado.end()].partition('=')[2])
        if valor_cookie_counter == MAX_ACCESOS:
            return MAX_ACCESOS
        else:
            valor_cookie_counter += 1
            return valor_cookie_counter
    else:
        return 1
      

def process_web_request(cs, webroot):
    rlist = [cs]
    wlist = []
    xlist = []

    timeout = False

    rsublist, wsublist, xsublist = select.select(rlist, wlist, xlist, TIMEOUT_CONNECTION)


    while not timeout:
        rsublist, wsublist, xsublist = select.select(rlist, wlist, xlist, TIMEOUT_CONNECTION)
        if not rsublist:
            timeout = True
        else:
            datos_recibidos = recibir_mensaje(cs)
            cabeceras = datos_recibidos.split("\r\n")
            primera_linea = cabeceras[0].split(" ")
            if not len(primera_linea) == 3:
                mensaje_error = "Error 400 Bad Request"
                enviar_mensaje(cs, mensaje_error)
                timeout = True
            else:
                if not primera_linea[2] == "HTTP/1.1":
                    mensaje_error = "Error 505 HTTP Version Not Supported"
                    enviar_mensaje(cs, mensaje_error)
                    timeout = True
                else:
                    if primera_linea[0] == "GET":
                        url = primera_linea[1].split('?')[0]
                        setcookie = False
                        if url=="/":
                            ruta = webroot + "/index.html"
                            setcookie = True
                        else:
                            ruta = webroot + url
                        if not os.path.isfile(ruta):
                            mensaje_error = "Error 404 Not Found"
                            enviar_mensaje(cs, mensaje_error)
                            timeout = True
                        else:
                            print(datos_recibidos)
                            valor_cookie_counter = process_cookies(datos_recibidos)
                            if valor_cookie_counter == MAX_ACCESOS:
                                mensaje_error = "Error 403 Forbidden"
                                enviar_mensaje(cs, mensaje_error)
                                timeout = True
                            else:
                                size_fichero = os.stat(ruta).st_size
                                fichero = os.path.basename(ruta)
                                extension = fichero.split('.')[1]
                                for filetype in filetypes:
                                    if extension==filetype[0]:
                                        extension = filetype[1]
                                        break
                                fecha = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
                                respuesta_ok = ("HTTP/1.1 200 OK\r\nDate: " + fecha + "\r\n" +
                                                "Server: web.profesoresdemurcia8959.org\r\n" +
                                                "Connection: Keep-Alive\r\n" + 
                                                "Keep-Alive: timeout=" + str(TIMEOUT_CONNECTION) + ", max=" + str(MAX_ACCESOS) + "\r\n" +
                                                "Content-Length: " + str(size_fichero) + "\r\n" +
                                                "Content-Type: " + extension + "\r\n")
                                if setcookie:
                                    respuesta_ok += "Set-Cookie: cookie_counter_8959=" + str(valor_cookie_counter) + "; Max-Age=120" + "\r\n"
                                respuesta_ok += "\r\n"
                                f = open(ruta, "rb")
                                cont = 0
                                respuesta_ok = respuesta_ok.encode()
                                while cont < size_fichero:
                                    respuesta_ok += f.read(BUFSIZE)
                                    cont += BUFSIZE
                                enviar_mensaje(cs, respuesta_ok)
                  
                    elif primera_linea[0] == "POST":
                        print(datos_recibidos)
                        patron_email = r'email=.*'
                        er_email = re.compile(patron_email)
                        resultado = er_email.search(datos_recibidos)
                        email = datos_recibidos[resultado.start():resultado.end()].partition('=')[2]
                        if email == "admin%40profesoresdemurcia8959.org":
                            ruta = webroot + "/acceso.html"
                            size_fichero = os.stat(ruta).st_size
                            extension = "text/html"
                            fecha = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
                            respuesta_ok = ("HTTP/1.1 200 OK\r\nDate: " + fecha + "\r\n" +
                                            "Server: web.profesoresdemurcia8959.org\r\n" +
                                            "Connection: Keep-Alive\r\n" +
                                            "Keep-Alive: timeout=" + str(TIMEOUT_CONNECTION) + ", max=" + str(MAX_ACCESOS) + "\r\n" +
                                            "Content-Length: " + str(size_fichero) + "\r\n" +
                                            "Content-Type: " + extension + "\r\n\r\n")
                            f = open(ruta, "rb")
                            cont = 0
                            respuesta_ok = respuesta_ok.encode()
                            while cont < size_fichero:
                                respuesta_ok += f.read(BUFSIZE)
                                cont += BUFSIZE
                            enviar_mensaje(cs, respuesta_ok)
                        else:
                            ruta = webroot + "/denegado.html"
                            size_fichero = os.stat(ruta).st_size
                            extension = "text/html"
                            fecha = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
                            respuesta_ok = ("HTTP/1.1 200 OK\r\nDate: " + fecha + "\r\n" +
                                            "Server: web.profesoresdemurcia8959.org\r\n" +
                                            "Connection: Keep-Alive\r\n" +
                                            "Keep-Alive: timeout=" + str(TIMEOUT_CONNECTION) + ", max=" + str(MAX_ACCESOS) + "\r\n" +
                                            "Content-Length: " + str(size_fichero) + "\r\n" +
                                            "Content-Type: " + extension + "\r\n\r\n")
                            f = open(ruta, "rb")
                            cont = 0
                            respuesta_ok = respuesta_ok.encode()
                            while cont < size_fichero:
                                respuesta_ok += f.read(BUFSIZE)
                                cont += BUFSIZE
                            enviar_mensaje(cs, respuesta_ok)
                    else:
                        mensaje_error = 'Error 405 "Method Not Allowed"'
                        enviar_mensaje(cs, mensaje_error)
                        timeout = True

    cerrar_conexion(cs)

def main():
    try:

        # Argument parser para obtener la ip y puerto de los parámetros de ejecución del programa. IP por defecto 0.0.0.0
        parser = argparse.ArgumentParser()
        parser.add_argument("-ip", "--host", help="Dirección IP del servidor (default: 0.0.0.0)", default="0.0.0.0")
        parser.add_argument("-p", "--port", help="Puerto del servidor (default: 8080)", type=int, default=8080)
        parser.add_argument("-wb", "--webroot", help="Directorio base desde donde se sirven los ficheros (default: files)", default="files")
        parser.add_argument('--verbose', '-v', action='store_true', help='Incluir mensajes de depuración en la salida')
        args = parser.parse_args()


        if args.verbose:
            logger.setLevel(logging.DEBUG)

        logger.info('Enabling server in address {} and port {}.'.format(args.host, args.port))

        logger.info("Serving files from {}".format(args.webroot))

        socket_servidor = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM, proto=0)
        socket_servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
        socket_servidor.bind((args.host, args.port))
        socket_servidor.listen()
        pid = 1
        while pid != 0:
            conexion_cliente, direccion_cliente = socket_servidor.accept()
            pid = os.fork()
            if pid == 0:
                cerrar_conexion(socket_servidor)
                process_web_request(conexion_cliente, args.webroot)
            else:
                cerrar_conexion(conexion_cliente)



    except KeyboardInterrupt:
        True

if __name__== "__main__":
    main()