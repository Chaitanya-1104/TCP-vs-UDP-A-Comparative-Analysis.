from socket import *
from hashlib import *
import os
import sys
import time
import uuid

# start using UDP to transfer the file
def startUsingUDP(serverName, serverUDPPort, filemd5):
    # create UDP socket
    clientUDPSocket = socket(AF_INET, SOCK_DGRAM)

    # start using UDP
    print("Start using UDP | Server: %s, Port: %d" % (serverName, serverUDPPort))

    # send a null string out socket; destination host and port number req'd
    clientUDPSocket.sendto(b'', (serverName, serverUDPPort))

    # download prompt
    print("Start downloading..")

    # get the file back from the server
    filedata, serverAddr = clientUDPSocket.recvfrom(5000)

    # get the md5 of the transferred data
    newMD5 = md5(filedata).hexdigest()

    # if the transmitted data has no error, then write the data to file.
    # if the data has error, do nothing
    if newMD5 == filemd5:
        # no error prompt
        print("MD5 check success, no transmission error")

        directory = "received_files"

        # create the directory if it does not exist
        if not os.path.exists(directory):
            os.makedirs(directory)

        # generate a unique filename
        filename = str(uuid.uuid4()) + ".txt"
        filepath = os.path.join(directory, filename)

        # create a file and write the data to it
        with open(filepath, 'wb') as filehandler:
            filehandler.write(filedata)

        # success prompt
        print(f"File received successfully: {filename}")
    else:
        # error prompt
        print("Error found")

    # close the UDP socket
    clientUDPSocket.close()


# server machine's name
serverName = "127.0.0.1"

# port numbers of server
serverTCPPort = 12306
serverUDPPort = 12307

# create TCP socket on client to use for connecting to remote
# server. Indicate the server's remote listening port
clientTCPSocket = socket(AF_INET, SOCK_STREAM)

# open the TCP connection
clientTCPSocket.connect((serverName, serverTCPPort))

# connection prompt
print("TCP connection established! | Server: %s, Port: %d" % (serverName, serverTCPPort))

# input the file name client wants
filename = input("Input file name: ")

# send the file name to the server
clientTCPSocket.send(bytes(filename, "utf-8"))

# get the status of the file from server "yes" or "No"
filestatus = clientTCPSocket.recv(1024).decode("utf-8").strip()

# check whether the file is on the server. If yes, receive the file.
# If no, do nothing
if filestatus == "yes":
    # get the md5 back from the server
    filemd5 = clientTCPSocket.recv(5000).decode("utf-8").strip()

    # print the md5 value of the data expected to transfer
    print("File md5: %s" % filemd5)

    # close the TCP connection
    clientTCPSocket.close()

    # start use UDP to download the file
    startUsingUDP(serverName, serverUDPPort, filemd5)

else:
    # cannot find the file on the server
    print("No such file found on the server!")
    # close the TCP connection
    clientTCPSocket.close()