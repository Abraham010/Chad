# IMPORTS
import chad_client as chad
import threading
import time
import argparse

# CONSTANTS

INPUT_COMMANDS = [
    '<EXIT>',
    '<HELP>'
]

# MESSAGES

ENTRY_MSG = '''
===============================================================================
- POWERED BY C.H.A.D (Communication system utilizing Hot Administrator Dogma) -
                              Welcome to Chad Chat!
                             To get help type <HELP>.
                               To exit type <EXIT>.
===============================================================================
'''

HELP_MSG = """
Help will be here soon.
"""

STARTED_INPUT = '[+ Started Input Thread]'
STARTED_OUTPUT = '[+ Started Output Thread]'
STARTED_CHAT = '[+ Started Chat Thread]'

INCOMING_MSG_PROMPT = '>>> {}'

# CLASSES


class ChatClient(chad.ChadClient):
    def __init__(self, *connections):
        super().__init__(*connections)

        self.running = True

        self.active_conn = 0

        self.input_thread = threading.Thread(target=self.input_loop)
        self.output_thread = threading.Thread(target=self.output_loop)

    def _start_threads(self):
        self.input_thread.start()
        self.output_thread.start()
        while threading.activeCount() < 3:
            time.sleep(0.1)

    def start_chat(self):
        print(STARTED_CHAT)
        self._start_threads()

        self.recv_buffer.append((-1, ENTRY_MSG.encode()))

        while self.running:
            self.send_pending()
            self.recv_pending()

    def input_loop(self):
        print(STARTED_INPUT)
        while self.running:
            self.handle_input(input())

    def handle_input(self, message):
        """
        Handle incoming input - call input commands or append to buffer.
        """
        split_msg = message.split(' ', maxsplit=1)
        if split_msg[0] in INPUT_COMMANDS:
            if len(split_msg) < 2:
                self.call_command(split_msg[0])
            else:
                self.call_command(split_msg[0], split_msg[1])
        else:
            self.send_buffer.append((self.active_conn, message.encode()))

    def call_command(self, command, data=None):
        if command == '<EXIT>':
            self.exit()
        elif command == '<HELP>':
            print(HELP_MSG)

    def output_loop(self):
        print(STARTED_OUTPUT)
        while self.running:
            if len(self.recv_buffer) > 0:
                print(INCOMING_MSG_PROMPT.format(self.recv_buffer.pop(0)[1].decode()))

    def _exit(self, message=None):
        if message:
            print(message)
        self.running = False
        while threading.activeCount() > 1:
            time.sleep(0.1)
        quit()

# FUNCTIONS


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('host_ip', type=str, help='IP of host to connect to')
    parser.add_argument('host_port', type=int, help='Port of host to connect to')
    return parser.parse_args()

# MAIN


def main():
    args = parse_args()
    client = ChatClient()
    client.new_conn(args.host_ip, args.host_port)
    client.start_chat()


if __name__ == '__main__':
    main()