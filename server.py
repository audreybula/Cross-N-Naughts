# Import the required libraries
from socket import *
from random import *
import json
import os

# Create the server socket object
try:
    serverSocket = socket(AF_INET, SOCK_STREAM)
except socket.error:
    print('Failed to connect')
    sys.exit()
print('Socket successfully created\n')

# Listening port for the server
serverPort = 7000

# Bind the server socket to the port
try:
    serverSocket.bind(('', serverPort))
except socket.error:
    print('Socket did not bind successfully to the port\n')
    sys.exit()
print('Socket successfully bound to port: ' + str(serverPort) + '\n')

# Start listening for new connections
serverSocket.listen(1)

print('The server is ready to receive messages\n\n')

# Keeps track of the number of moves the client and server makes
clientMoves = 0
serverMoves = 0

# Cross and Naughts board in JSON
class CrossNaughts:
    board = []
    def __init__(self):
        self.board = ["", "", "", "", "", "", "", "", ""]
        self.state = 0
    def getBoardIndex(self, i):
        return self.board[i]
    def setBoardIndex(self, i, value):
        self.board[i] = value

# Define the winning combinations
def WinningComb(jStructure):
    # Client is X
    if jStructure[0] == "X" and jStructure[1] == "X" and jStructure[2] == "X":
        return "X"
    elif jStructure[0] == "X" and jStructure[3] == "X" and jStructure[6] == "X":
        return "X"
    elif jStructure[0] == "X" and jStructure[4] == "X" and jStructure[8] == "X":
        return "X"
    elif jStructure[1] == "X" and jStructure[4] == "X" and jStructure[7] == "X":
        return "X"
    elif jStructure[2] == "X" and jStructure[5] == "X" and jStructure[8] == "X":
        return "X"
    elif jStructure[3] == "X" and jStructure[4] == "X" and jStructure[5] == "X":
        return "X"
    elif jStructure[6] == "X" and jStructure[7] == "X" and jStructure[8] == "X":
        return "X"
    elif jStructure[6] == "X" and jStructure[4] == "X" and jStructure[2] == "X":
        return "X"
    # Server is O
    elif jStructure[0] == "O" and jStructure[1] == "O" and jStructure[2] == "O":
        return "O"
    elif jStructure[0] == "O" and jStructure[3] == "O" and jStructure[6] == "O":
        return "O"
    elif jStructure[1] == "O" and jStructure[4] == "O" and jStructure[7] == "O":
        return "O"
    elif jStructure[2] == "O" and jStructure[5] == "O" and jStructure[8] == "O":
        return "O"
    elif jStructure[3] == "O" and jStructure[4] == "O" and jStructure[5] == "O":
        return "O"
    elif jStructure[6] == "O" and jStructure[7] == "O" and jStructure[8] == "O":
        return "O"
    elif jStructure[0] == "O" and jStructure[4] == "O" and jStructure[8] == "O":
        return "O"
    elif jStructure[6] == "O" and jStructure[4] == "O" and jStructure[2] == "O":
        return "O"
    else:
        return ""

crossNaughts = CrossNaughts()

while True:
    # Accept a connection from a client
    connectionSocket, addr = serverSocket.accept()

    # Retrieve the message sent by the client
    clientMessage = connectionSocket.recv(1024).decode('UTF-8')
    print(clientMessage)

    # Check if message is not empty
    if clientMessage != "":
        # Check to see if it is a http GET request
        if clientMessage.split()[0] == "GET":
            # Extract the resource from the string
            resource = clientMessage.split()[1].split("/")[1]

            # Check to see if resource exists
            if os.path.isfile(resource):
                response = "HTTP/1.1 200 OK\n\n"
                # Open the file
                with open(resource, 'r') as file:
                    # Append file contents to the HTTP response header
                    response += file.read()
                    print(str(response) + '\n')
                    # Send response to client
                    connectionSocket.send(response.encode())
            # Else block is entered if resource does not exist
            else:
                response = "HTTP 404 Not found"
                print(str(response) + '\n')
                # Send response to client
                connectionSocket.send(response.encode())

        # Check to see if it is a http POST request
        elif clientMessage.split()[0] == "POST":
            # Extract the client's choice from the string
            clientChoice = clientMessage.split()[1].split("/")[1]

            # Checks whether Reset button was clicked
            if clientChoice == "reset":
                # Reset client moves
                clientMoves = 0
                # Reset server moves
                serverMoves = 0
                # New game
                crossNaughts = CrossNaughts()
                response = json.dumps(crossNaughts.__dict__)
            else:
                # Decrement client choice because board index starts from zero
                clientChoice = int(clientChoice) - 1
                # Check if client's choice is valid
                if crossNaughts.getBoardIndex(clientChoice) == "":
                    # Put X on client's selected position
                    crossNaughts.setBoardIndex(clientChoice, "X")
                    # Increment client moves
                    clientMoves += 1
                    # Don't know how else to decide a Draw. This becomes wrong if the client's
                    # last move is a winning combination, but it's much better than having an
                    # infinite loop. Checks if client and server have made maximum number of moves
                    if clientMoves < 5 and serverMoves < 5:
                        while True:
                            # Server chooses a random position
                            serverChoice = randint(0, 8)
                            # Check if server's choice is valid
                            if crossNaughts.getBoardIndex(serverChoice) == "" and serverChoice != clientChoice:
                                # Put O on server's selected position
                                crossNaughts.setBoardIndex(serverChoice, "O")
                                # Increment server moves
                                serverMoves += 1
                                response = json.dumps(crossNaughts.__dict__)
                                print(crossNaughts.board)
                                # Check if client or server has won
                                winner = WinningComb(crossNaughts.board)
                                # Client wins
                                if winner == "X":
                                    # Change state to X
                                    crossNaughts.state = "X"
                                    response = json.dumps(crossNaughts.__dict__)
                                # Server wins
                                elif winner == "O":
                                    # Change state to O
                                    crossNaughts.state = "O"
                                    response = json.dumps(crossNaughts.__dict__)
                                break
                    # Enter this else block if there is a draw
                    else:
                        # Change state to D
                        crossNaughts.state = "D"
                        response = json.dumps(crossNaughts.__dict__)
                # Enter this else block if client chooses an existing position
                else:
                    # Change state to Error
                    crossNaughts.state="Error"
                    response = json.dumps(crossNaughts.__dict__)

            # Append response(board positions and game state) to HTTP response
            httpResponse = "HTTP/1.1 200 OK\n\n" + response
            print(httpResponse + '\n')

            # Send HTTP response to client
            connectionSocket.send(httpResponse.encode())
                            
    # Close the connection
    connectionSocket.close()
