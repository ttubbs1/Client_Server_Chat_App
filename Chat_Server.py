
import socket
import random
import sys
from threading import Thread

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_name = socket.getfqdn()
server_address = socket.gethostbyname(server_name)
server_port = 12000
server_socket.bind((server_name, server_port))
print("<System> IP address of the server is:", server_address)

# keeps track of the unique name + number combo used in assign_client_id
client_ids = []
# keeps track of all connection sockets the server has
connections = []


# the client enters a name and the server adds a 4 digit random number to the end and ensures the name is unique
def assign_client_id(temp_name, current_connection_socket):
    while True:
        r = random.randint(1000, 9999)
        if (temp_name + str(r)) not in client_ids:
            client_ids.append(temp_name + str(r))
            message = "<Server> Your name on the server is "+ client_ids[-1] +\
                      ".\n\t\t This is the name other users will see you by."
            current_connection_socket.send(message.encode())
            break
    return client_ids[-1]


# if client enters the command SHOW CLIENTS, this method will give all currently connected clients
def show_clients(current_connection_socket):
    current_connection_socket.send(("<Server> Clients currently connected ").encode())
    for client in client_ids:
        current_connection_socket.send(("<" + client + "> ").encode())


# If the SHOW COMMANDS command is used and upon first entering the server this method will run
# it gives the client some basic guidelines on how to use the server
def show_commands(current_connection_socket):
    message = "\n<Server> Enter 'SHOW CLIENTS' to see who is online." + \
              "\n\t\t Enter 'SHOW COMMANDS' to make this text appear again" + \
              "\n\t\t To send a message to another client type, for example, '@John3252' followed by message" + \
              "\n\t\t Or, to send a message everyone can see use '@ALL' followed by a message" + \
              "\n\t\t To close your connection to the server you can enter '.exit'"
    current_connection_socket.send(message.encode())


# from the input from a client, if it starts with @ this method will run to determine if it is a valid client
# and it will return the intended client
def determine_client_name(message):
    x = 0 # var to keep track of index
    client_name = "x"
    for char in message:
        if char.isspace() and x > 3:
            client_name = message[1:x]
        elif char.isspace() and x < 3:
            client_name = message[1:x]
        x+=1

    for name in client_ids:
        if name == client_name:
            return client_name
        elif client_name == 'ALL':
            return 'ALL'

    return "error"


# allows a client to send a message to another client or to all clients
def forward_message(receiving_client, message, sending_connection):
    if receiving_client == "ALL":
        for connection in connections:
            if connection != sending_connection:
                connection.send(message.encode())
    else:
        client_to_connect_to = client_ids.index(receiving_client) - 1
        connections[client_to_connect_to].send(message.encode())


server_socket.listen()


# a method in which threads will deal with each client as they connect
def handle_client(current_connection_socket):
    # this loop handles the input from the client in regard to their name
    while True:
        try:
            temp_client_name = current_connection_socket.recv(1024).decode()
            if temp_client_name == "ALL":
                message = "<Server> Name cannot be 'ALL'. Please enter another name."
                current_connection_socket.send(message.encode())
                continue
            break
        except socket.error as e:
            try:
                current_connection_socket.send(("<Server> Error occurred while receiving name."
                                                " Please enter it again").encode())
            except socket.error as e:
                current_connection_socket.close()
                connections.remove(current_connection_socket)
                sys.exit()

    try:
        current_client_id = assign_client_id(temp_client_name, current_connection_socket)
        show_commands(current_connection_socket)
    except socket.error as e:
        current_connection_socket.close()
        connections.remove(current_connection_socket)
        client_ids.remove(current_client_id)
        sys.exit()

    # just a variable for quick use in giving an error to a client
    input_error = "<Server> Unexpected input. Enter 'SHOW COMMANDS' for guidelines on input."

    # this loop will handle all messages from the client that are not the initial naming process
    while True:
        try:
            client_message = current_connection_socket.recv(1024).decode()

            if client_message == "SHOW CLIENTS":
                show_clients(current_connection_socket)
            elif client_message == "SHOW COMMANDS":
                show_commands(current_connection_socket)
            elif client_message[0] == "@":
                receiving_client_name = determine_client_name(client_message)
                client_message = client_message.replace(("@" + receiving_client_name),
                                                        ("<" + current_client_id + "> "))
                if receiving_client_name != "error":
                    forward_message(receiving_client_name, client_message, current_connection_socket)
                else:
                    current_connection_socket.send(("<Server> Invalid client name. Use 'SHOW COMMANDS'"
                                                    " to see online clients").encode())
            else:
                current_connection_socket.send(input_error.encode())

        except socket.error as e:
            current_connection_socket.close()
            client_ids.remove(current_client_id)
            connections.remove(current_connection_socket)
            sys.exit()


# this loop handles incoming connections before giving them to threads which will run the handle_client
while True:
    connection_socket, addr = server_socket.accept()
    connections.append(connection_socket)

    server_thread = Thread(target=handle_client, args=(connections[-1],))
    server_thread.daemon = True
    server_thread.start()
