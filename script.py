from pypacker import psocket
from pypacker.layer12 import ethernet
from pypacker.layer4 import tcp
from time import time
import pyotp 

socket = psocket.SocketHndl(iface_name=None)
ports = [1337, 1338, 1339]
current_port = current_time = 0
timeout = 5

while (current_port < len(ports)):
  bts = socket.recv()
  pkt = ethernet.Ethernet(bts)

  if ((pkt[tcp.TCP] is not None) and (pkt[tcp.TCP]).dport == ports[current_port]): 
    if ((current_port != 0) and (time() - current_time > timeout)):
      current_port = current_time = 0
    else:
      print ("Recebeu!")
      current_port += 1
      current_time = time()
