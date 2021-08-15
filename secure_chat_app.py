#importing necessary files
import socket
import sys
import ssl

'''
If -c optiom is choosen client() finction is called and functions of alice are called.
'''
def client():
    host = "bob1"
    #Socket creation
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error:
        print('Error making the socket')
    
    #Find the IP of bob1 to connect
    try:
        remote_ip = socket.gethostbyname(host)
    except socket.gaierror:
        print('Could not resove hostname')
        sys.exit()

    port = 5006
    # Connect to remote server
    s.connect((remote_ip, port))

    print('Socket connected to ' + host + ' on IP: ' + remote_ip)
    s.send("chat_hello".encode())
    reply = s.recv(50)
    print(reply.decode())
    s.send("chat_STARTTLS".encode())
    reply = s.recv(50)
    print(reply.decode())
    # if bob(server) replies chat_STARTTLS_ACK then a socket is wrapped with tls and a handshake is intiated.
    if (reply.decode() == "chat_STARTTLS_ACK"):
        s = ssl.wrap_socket(s, keyfile="/root/alice-private-key.pem", certfile="/root/alice.crt", server_side=False,
                            ca_certs="/root/root.crt", cert_reqs=ssl.CERT_REQUIRED, ssl_version=ssl.PROTOCOL_TLS)

    #Chat_loop
    while (1):
        message = input("Enter Your Message :- ")
        if (message == "chat_close"):
            s.send(message.encode())
            break
        s.send(message.encode())
        data = s.recv(100)
        data = data.decode()
        if (data == "chat_close"):
            print("Message from bob :- " + data)
            break
        print("Message from bob :- " + data)

    s.close()

def server():
    PORT = 5006  # Arbitrary 4 digit number, avoiding using the smaller ports which are designated for system use

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('Socket created')
    HOST = "bob1"
    try:
        remote_ip = socket.gethostbyname(HOST)
    except socket.gaierror:
        print('Could not resove hostname')
        sys.exit()

    # Bind the specified port to the socket, capture all incoming data
    try:
        s.bind((remote_ip, PORT))
    except socket.error:
        print('Bind failed. Error:')
        sys.exit()

    print('Socket bind complete')

    # listen for any incoming connections over this port, 10 means only 10 connections are allowed to be waiting
    s.listen(1)
    print('Socket now listening')

    conn, addr = s.accept()
    data = conn.recv(50)
    print(data.decode())
    conn.send("chat_reply".encode())
    data = conn.recv(50)
    data = data.decode()
    if (data == "chat_STARTTLS"):
        print(data)
        conn.send("chat_STARTTLS_ACK".encode())
        conn = ssl.wrap_socket(conn, keyfile="/root/bob-private-key.pem", certfile="/root/bob.crt",
                               ca_certs="/root/root.crt", server_side=True, cert_reqs=ssl.CERT_REQUIRED,
                               ssl_version=ssl.PROTOCOL_TLS)
    else:
        print("Message from alice :- " + data)
        message = input("Enter Your Message :- ")
        if (message == "chat_close"):
            conn.send(message.encode())
            conn.close()
        conn.send(message.encode())

    while (1):
        data = conn.recv(50)
        data = data.decode('UTF-8')
        if (data == "chat_close"):
            break
        print("Message from Alice :- " + data)
        message = input("Enter Your Message :- ")
        if (message == "chat_close"):
            conn.send(message.encode())
            break
        conn.send(message.encode())

    conn.close()
    s.close()

choice = sys.argv[1]
if(choice == "-s"):
    server()
else :
    client()
