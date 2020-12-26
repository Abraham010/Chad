# IMPORTS
import socket
import chat_client as chatcl
import argparse
import chad

# CONSTANTS

# MESSAGES
CONNECTED_MSG = 'New connection from {}:{}'

DESCRIPTION = '''
Chad-Chat Server. Listen for new connections and create clients.
'''

LISTENING = 'Listening on port {}...'

# FUNCTIONS


def parse_args():
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('listen_port', type=int, help='Port to listen on')
    return parser.parse_args()


def listen(port):
    with socket.socket() as listen_socket:
        print(LISTENING.format(port))
        listen_socket.bind(('', port))
        listen_socket.listen()
        soc, address = listen_socket.accept()
        print(CONNECTED_MSG.format(address[0], address[1]))
        chat_client = chatcl.ChatClient(chad.Connection(soc))
        chat_client.start()


# MAIN

def main():
    args = parse_args()
    listen(args.listen_port)


if __name__ == '__main__':
    main()
