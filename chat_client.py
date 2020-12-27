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
STARTED_COMMUNICATION = '[+ Started Communication Thread]'

INCOMING_MSG_PROMPT = '>>>'

# CLASSES


class ChatClient(object):
    def __init__(self):
        self.running = True

        self.chad = chad.ChadClient()

        self.input_thread = threading.Thread(target=self.input_loop)
        self.output_thread = threading.Thread(target=self.output_loop)

    def start(self):
        # Add control messages for input thread
        print(STARTED_COMMUNICATION)
        print(ENTRY_MSG)

        self._start_threads()
        self.chad.communicate_loop()

    def _start_threads(self):
        self.output_thread.start()
        self.input_thread.start()
        while threading.activeCount() < 3:
            time.sleep(0.01)

    def input_loop(self):
        print(STARTED_INPUT)

        while self.running:
            self.handle_input(input())

    def handle_input(self, message):
        """
        Handle incoming input - call input commands or send through connection.
        """
        if len(message) > 0:
            if message[0] == COMMAND_CHAR:
                self.call_command(message[1:])
            else:
                # Send the message
                self.chad.stage_send(chad.BROADCAST, message.encode())

    def call_command(self, command):
        if command == 'exit':
            self.exit()
        elif command == 'help':
            print(HELP_MSG)
        else:
            print('Command not found.')

    def output_loop(self):
        print(STARTED_OUTPUT)

        while self.running:
            while self.chad.incoming_data() > 0:
                print(INCOMING_MSG_PROMPT, self.chad.receive()[1].decode())

    def exit(self):
        """
        Exit all threads gracefully.
        """
        self.chad.exit()
        self.running = False
        while threading.activeCount() > 1:
            time.sleep(0.01)
        quit()

    def connect(self, host, port):
        """
        Temporary connect method
        """
        self.chad.new_conn(host, port)


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
