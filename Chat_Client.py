
import socket
import sys
import time
from threading import Thread

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_port = 12000
# User needs to enter the IP address of the server which will be printed by the server code
server_ip = input("<System>   Please enter the IP address of the server.")

# loop that runs 5 times as it tries to connect to the server and if it doesnt connect the program terminates
for x in range(5):
    try:
        client_socket.connect((server_ip, server_port))
    except socket.error as e:
        print("<System> Designated server is either not running or an error occurred while connecting. "
              "Will try to connect again.")
        if x == 4:
            print("<System> Could not connect to the server. Ending process.")
            sys.exit()
    else:
        break

# name that will be given a random 4 digit number attached to the end by the server. Name + number combo is unique
temp_name = input("<Server> Please enter a name. ")
try:
    client_socket.send(temp_name.encode())
except socket.error as e:
    print("<System> Error occurred while sending name.")
    client_socket.close()


# message receiving
def wait_for_messages():
    while True:
        try:
            message = client_socket.recv(1024).decode()
            print(message)
        except socket.error as e:
            time.sleep(3) # sleep is here to make sure below message does not print if a .exit command is used
            print("<System> Error occurred while receiving messages.")
            client_socket.close()
            sys.exit()


# Thread to wait for messages
client_thread = Thread(target=wait_for_messages)
client_thread.daemon = True
client_thread.start()


# message sending
while True:
    message_input = input()
    try:
        if message_input == ".exit":
            client_socket.send(message_input.encode())
            client_socket.close()
            break
        client_socket.send(message_input.encode())
    except socket.error as e:
        print("<System> Unexpected error occurred when sending message")
        client_socket.close()
        break
