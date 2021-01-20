#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
    Author: Andreas Poesch (andreas.poesch@googlemail.com)

    make a port forwarding / tunneling server
    
    inspired by: http://code.activestate.com/recipes/483730-port-forwarding/
    
    2014/01/22
    
    tested to work with SSH connections and HTTPS
    --> could be mis-used to eavesdrop on unencrypted connections ;)
'''
import http.server
import socketserver
import base64

import socket
import sys
import _thread

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

#connect to "localhost:localport" and be forwarded to "remotehost:remoteport"

settings = {'localhost': '0.0.0.0', #fake endpoint socket to connect to from our app
            'localport': 8001,  
            'remotehost': "localhost",   #the real service 
            'remoteport': 8000,
            'evesdrop': True, #output all communication?
            'base64': False, #evesdrop in base64 or try raw?
            'chunksize': 2**16
           }





def server():
    print("start server", settings)
    try:
        dock_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        dock_socket.bind((settings.get('localhost', '0.0.0.0'), settings['localport']))
        dock_socket.listen(5)
        print("Connect to ", settings.get('localhost', '0.0.0.0'), ':', settings['localport'])
        while True:
            client_socket = dock_socket.accept()[0]
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print("Forwarding to:", settings['remotehost'], ":", settings['remoteport'])
            server_socket.connect((settings['remotehost'], settings['remoteport']))   #here we go!
            
            _thread.start_new_thread(forward, (client_socket, server_socket, bcolors.OKGREEN))
            _thread.start_new_thread(forward, (server_socket, client_socket, bcolors.OKBLUE))
    except Exception as ex:
        print(ex)
    finally:
        _thread.start_new_thread(server, ())

def forward(source, destination, color=None):
    string = ' '
    while string:
        string = source.recv(settings.get('chunksize', 1024))
        if string:
            if settings.get('evesdrop', False):
                if color:
                    print(color)
                print((source.getpeername()), end=' ')
                print("-->", end=' ')
                print((destination.getpeername()), end=' ')
                if settings.get('base64', False):
                    print((base64.b64encode(string)))
                else:
                    print(string)
                if color:
                    print(bcolors.ENDC)
            destination.sendall(string)
        else:
            source.shutdown(socket.SHUT_RD)
            destination.shutdown(socket.SHUT_WR)
            
def main():
    _thread.start_new_thread(server, ())
    lock = _thread.allocate_lock()
    lock.acquire()
    lock.acquire()
    
if __name__ == '__main__':
    print("start.")
    main()
    print("end.")
