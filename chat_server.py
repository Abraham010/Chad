# IMPORTS
import socket
import chat_client as chcl
import argparse

# CONSTANTS

# MESSAGES
CONNECTED_MSG = 'New connection from {}:{}'

DESCRIPTION = '''
Chad Server. Listen for new connections and create clients.
'''

LISTENING = 'Listening on port {}...'

# FUNCTIONS


def parse_args():
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('listen_port', type=int, help='Port to listen on')
    return parser.parse_args()


def listen(port):
    try:
        with socket.socket() as listen_socket:
            print(LISTENING.format(port))
            listen_socket.bind(('', port))
            listen_socket.listen()
            conn, address = listen_socket.accept()
            print(CONNECTED_MSG.format(address[0], address[1]))
            chat_client = chcl.ChatClient(conn)
            chat_client.start_chat()
    except KeyboardInterrupt:
        quit()


# MAIN

def main():
    args = parse_args()
    listen(args.listen_port)


if __name__ == '__main__':
    main()
