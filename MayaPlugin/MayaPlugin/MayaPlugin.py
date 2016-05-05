#! /usr/bin/env python3

###############################
# This script unloads and reloads a Maya plugin remotely so that we can include it
# in the build processes.
#
# "No connection could be made because the target machine actively refused it"?
# This means you have not opened a Maya command port!
# 
# See: userSetup.mel
###############################

import socket
from sys import argv
import os

host = '127.0.0.1'
port = 8934

address = (host, port)

# This filepath may have to change depending on your build configuration
filename = "MayaPlugin"

filepath = os.path.dirname(os.path.realpath(__file__))
filepath += "\\..\\..\\x64\\Debug\\%s.mll" % filename

filepath = filepath.replace("\\", "/")


def send_command(cmd):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(address)

    client.send(bytes(cmd, 'UTF-8'))

    # Response
    data = client.recv(1024)

    client.close()
    return data


def unload_plugin():
    send_command("unloadPlugin %s;" % filename);
    print("\"%s\" unloaded." % filename)

def load_plugin():
    send_command("loadPlugin \"%s\";" % filepath);
    print("\"%s\" loaded." % filename)

def echo(str):
    send_command("print \"%s\";" % str);


# Script is called via cmd as
# `python MayaPlugin.py load|unload|echo [echo message]`
if __name__ == "__main__":
    if(argv[1] == "load"):
        load_plugin()
    if(argv[1] == "unload"):
        unload_plugin()
    if(argv[1] == "echo"):
        echo(argv[2])