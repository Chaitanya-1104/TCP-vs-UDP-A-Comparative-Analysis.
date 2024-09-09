from socket import *
from hashlib import *
import os

TCPPort = 12306
UDPPort = 12307

# creates TCP socket and bind to specified port first (for FTP-PDU control information)
TCPSocket = socket(AF_INET, SOCK_STREAM)
try:
    TCPSocket.bind(("", TCPPort))
except:
    print("*** FTPServerUsingUDP: error: Port 12306 is not available, Quitting... ")
    exit(0)

TCPSocket.listen(1)

# create UDP socket and bind to your specified port
UDPSocket = socket(AF_INET, SOCK_DGRAM)
UDPSocket.bind(("", UDPPort))
print ("The FTP server using UDP is listening to user request on port TCP: %d ... " % TCPPort)
print ("FTPServerUsingUDP: the UDP port to this server is %d." % UDPPort)

def send_file(client, filename):
    # open the file and read its content
    try:
        with open(filename, 'rb') as file:
            file_content = file.read()
    except FileNotFoundError:
        print(f"File '{filename}' not found.")
        client.sendto(b'FILE_NOT_FOUND', client_address)
        return

    # calculate MD5 hash
    md5_val = md5(file_content).hexdigest()

    # send MD5 hash to client
    client.sendto(md5_val.encode(), client_address)

    # send file content in chunks
    chunk_size = 1024
    for i in range(0, len(file_content), chunk_size):
        client.sendto(file_content[i:i+chunk_size], client_address)

while True:
    # read the FILENAME included in client's message
    #    AND REMEMBER client's address (IP and port)
    connectionSocket, addr = TCPSocket.accept()
    file_name = connectionSocket.recv(255).decode('utf-8').strip()

    # tries to open the file. If yes, sends 'yes' to the client;
    #    otherwise, sends 'no' to the client and closes the TCP connection.
    try:
        file_handler = open(file_name, 'rb')
        connectionSocket.send(b'yes')
    except:
        print ("*** Server log: file \"%s\" cannot open!" % file_name)
        connectionSocket.send(b'no')
        connectionSocket.close()
        continue

    # get file content and md5
    file_content = file_handler.read()
    md5_val = md5(file_content).hexdigest()

    # sends the md5 value to the client using TCP. Then, closes the TCP connection.
    connectionSocket.send(bytes(md5_val, 'utf-8'))
    connectionSocket.close()

    # Waits the signal message from the client before start sending the file contents.
    message, clientAddr = UDPSocket.recvfrom(255)

    # sends the file content to clientAddress
    UDPSocket.sendto(file_content, clientAddr)
    print("Sent file \"%s\" to client (IP, port) = %s\n" % (file_name, str(clientAddr)))