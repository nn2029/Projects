import time
import socket
import sys
import os

soc = socket.socket()
host = socket.gethostname()
port = 8080
soc.bind(('',port))

print("waiting for connection... ... ...")
soc.listen()
conn, addr = soc.accept()

print(addr, "is connected to server")
command = input(str("Enter Command"))
conn.send(command.encode())
print("Command has been sent successfully")
data = conn.recv(1024)

if data:
    print("Command received and successfully executed")

