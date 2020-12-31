# IMPORTS
import socket
import argparse
import select

# CONSTANTS
RECV_SIZE = 1024


# CLASSES


class Chad(object):
    """
    A manager for TCP connections.
    """
    def __init__(self):
        # Connection ID: socket
        self.connections = dict()
        # socket: [bytes, bytes, ...]
        self.send_queues = dict()
        self.recv_queues = dict()
        # List of closed sockets
        self.closed = list()

    def communicate(self):
        """
        Main function, sends and receives data.
        """
        readable, writable, exceptional = select.select(
            self.recv_queues.keys(), self.send_queues.keys(), self.recv_queues.keys())
        self.readfrom(readable)
        self.handle_except(exceptional)
        self.clean_conns()
        self.sendto(writable)

    def readfrom(self, readable):
        """
        Read from all readable connections, and append the data to their recv_queue.
        :param readable: list of sockets that have data to read from.
        """
        for read_socket in readable:
            data = read_socket.recv(RECV_SIZE)
            if data:
                self.recv_queues[read_socket].append(data)
            else:
                self.close(read_socket)

    def clean_conns(self):
        """
        Remove closed sockets from self.connections.
        """
        for conn_id in self.connections:
            if self.connections[conn_id] in self.closed:
                del self.connections[conn_id]

    def sendto(self, writable):
        """
        Send pending data to connections that are ready for sending.
        """
        for write_socket in writable:
            if self.send_queues[write_socket]:
                writable.sendall(self.send_queues[write_socket])

    def handle_except(self, exceptional):
        for except_socket in exceptional:
            self.close(except_socket)

    def close(self, closed_sock):
        closed_sock.close()
        self.closed.append(closed_sock)
        del self.recv_queues[closed_sock]
        del self.send_queues[closed_sock]


class Chat(object):
    def __init__(self):
        self.chad = Chad()


# FUNCTIONS


# MAIN


def main():
    pass

if __name__ == '__main__':
    main()

