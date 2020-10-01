from pypacker import psocket
from pypacker.layer12 import ethernet
from pypacker.layer4 import tcp
from time import time
import pyotp 
import socket 

my_socket = psocket.SocketHndl(iface_name=None)
ports = [1337, 1338, 1339]
current_port = current_time = 0
timeout = 5

while (current_port < len(ports)):
  bts = my_socket.recv()
  pkt = ethernet.Ethernet(bts)

  if ((pkt[tcp.TCP] is not None) and (pkt[tcp.TCP]).dport == ports[current_port]): 
    if ((current_port != 0) and (time() - current_time > timeout)):
      current_port = current_time = 0
    else:
      print ("Recebeu!")
      current_port += 1
      current_time = time()

serv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serv_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
serv_socket.bind(('127.0.0.1', 1340)) 
serv_socket.listen(10) 
con, cliente = serv_socket.accept() 
client_value = con.recv(1024).decode().strip()
serv_socket.close() 

totp = pyotp.TOTP('2UZC3V2WGD2OHNDP')
if (totp.verify(client_value)):
  print("Aceito!")
else:
  print("Rejeitado!")

