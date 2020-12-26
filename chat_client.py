# IMPORTS
import chad
import threading
import time
import argparse

# CONSTANTS

COMMAND_CHAR = '!'

# MESSAGES

ENTRY_MSG = '''
===============================================================================
- POWERED BY C.H.A.D (Communication system utilizing Hot Administrator Dogma) -
                              Welcome to Chad Chat!
                             To get help type !help.
                               To exit type !exit.
===============================================================================
'''

HELP_MSG = """
Help will be here soon.
"""

STARTED_INPUT = '[+ Started Input Thread]'
STARTED_OUTPUT = '[+ Started Output Thread]'
STARTED_MAIN = '[+ Started Main Thread]'

INCOMING_MSG_PROMPT = '>>>'

# CLASSES


class ChatClient(chad.ChadClient):
    def __init__(self, *connections):
        super().__init__(*connections)

        self.running = True

        self.active_conn = None

        self.input_thread = threading.Thread(target=self.input_loop)
        self.output_thread = threading.Thread(target=self.output_loop)

    def _start_threads(self):
        self.input_thread.start()
        self.output_thread.start()
        while threading.activeCount() < 3:
            time.sleep(0.1)

    def start(self):
        print(STARTED_MAIN)

        self._start_threads()

        print(ENTRY_MSG)

        while self.running:
            self.communicate()

    def input_loop(self):
        print(STARTED_INPUT)

        while self.running:
            self.handle_input(input())

    def handle_input(self, message):
        """
        Handle incoming input - call input commands or append to buffer.
        """
        if len(message) > 0:
            if message[0] == COMMAND_CHAR:
                self.call_command(message[1:])
            else:
                self.send(self.active_conn, message.encode())

    def call_command(self, command, data=None):
        if command == 'exit':
            # NEEDS CHANGE
            self.exit()
        elif command == 'help':
            print(HELP_MSG)
        else:
            print('Command not found.')

    def output_loop(self):
        print(STARTED_OUTPUT)
        while self.running:
            while self.incoming_data() > 0:
                print(INCOMING_MSG_PROMPT, self.recv()[1].decode())

    def exit(self, message=None):
        if message:
            print(message)
        self.running = False
        self.close_all_conns()
        while threading.activeCount() > 1:
            time.sleep(0.1)
        quit()

    def all_disconnected(self):
        self.exit(chad.DISCONNECTED_MSG)

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
    client.start()


if __name__ == '__main__':
    main()
