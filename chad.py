# IMPORTS
import socket

# CONSTANTS
SOCK_TIMEOUT = 0.1
RECV_SIZE = 4096
DEFAULT_PORT = 55555

# SEND CODES
BYTES = 0

# MESSAGES

DISCONNECTED_MSG = 'All connections closed.'

EXITING_MSG = 'Exiting...'


# FUNCTIONS


def check_type(var, *types, message=None, direct_check=False):
    """
    Check if var is of one of the types, else raise a TypeError with a message.
    If var is a list or tuple, check every element.
    """
    if message is None:
        message = '{} must be of type {}'.format(var, ', '.join(map(str, types)))
    if type(var) in (list, tuple) and not direct_check:
        for element in var:
            if type(element) not in types:
                raise TypeError(message)
    else:
        if type(var) not in types:
            raise TypeError(message)


# CLASSES


class Connection(object):
    def __init__(self, host, port=DEFAULT_PORT):
        """
        Object representing a connection to a client.
        :param host: (str or bytes) ip of host the connection is to, or existing (socket).
        :param port: (int) port of the host client to connect to.
        """
        if type(host) == str or type(host) == bytes:
            self.socket = socket.create_connection((host, port))
        elif type(host) == socket.socket:
            self.socket = host
        else:
            raise TypeError('host for Connection must be a string or socket object')

        self.socket.settimeout(SOCK_TIMEOUT)

    def local_info(self):
        """
        Return (local_address, local_port)
        """
        return self.socket.getsockname()

    def peer_info(self):
        """
        Return (peer_address, peer_port)
        """
        return self.socket.getpeername()

    def close(self):
        self.socket.close()

    def send(self, data):
        self.socket.send(data)

    def recv(self, bufsize=RECV_SIZE):
        return self.socket.recv(bufsize)


class ChadClient(object):
    """
    Chad Client - manages multiple connections and supplies multiple functions
    for sending and receiving data.

    Methods that should be used by Chad-Powered applications are as described below:

    -- MAIN METHODS --
    send, recv, communicate, close_all_conns

    -- USEFUL METHODS --
    new_conn, get_conn_ids, close_conn, incoming_data

    -- METHODS APPLICATIONS CAN OVERWRITE --
    conn_disconnected, all_disconnected
    """

    def __init__(self, *connections):
        """
        self.connections is a dict of {connectionID: Connection_Object}
        self.closed_conns is a set of connectionIDs that are staged fro closing and deletion.

        A connectionID is an int identifying a connection in the client.

        :param connections: (list of Connection objects) Connections connected to other clients.
        """
        self.connections = dict()
        for conn in connections:
            self.add_conn(conn)
        self._closed_conns = set()

        # Buffer for information waiting to be sent.
        self._send_buffer = list()
        # Buffer for information waiting to be received and processed.
        self._recv_buffer = list()
        # An item in a buffer should be in the form of: (connectionID, bytes)

    def send(self, conn_id, data):
        """
        Stage data to be sent to the specified connection (append to send_buffer).
        :param conn_id: (int) connectionID. (None) to broadcast to all connections.
        :param data: (bytes) data to be sent through the connection.
        """
        if (conn_id is None or conn_id in self.connections) and type(data) == bytes:
            self._send_buffer.append((conn_id, data))

    def incoming_data(self):
        """
        Return the number of items in the recv_buffer.
        """
        return len(self._recv_buffer)

    def recv(self):
        """
        Return data received from a connection (first item of recv_buffer),
        in the form (connectionID, data).
        """
        if len(self._recv_buffer) > 0:
            return self._recv_buffer.pop(0)

    def communicate(self):
        """
        Main function for the client: should be run in a loop.
        Send all data that is staged for sending (in send_buffer) and
        receive data from all connections into recv_buffer.
        Also close any pending connections and call all_disconnected if no more connections are active.
        """
        if len(self.connections) == 0:
            self.all_disconnected()
        self._send_pending()
        self._recv_pending()
        self._clean_connections()

    def _send_pending(self):
        """
        Sends information from self.send_buffer through the corresponding connection.
        """
        while len(self._send_buffer) > 0:
            conn_id, data = self._send_buffer.pop(0)

            # Broadcast
            if conn_id is None:
                for conn in self.connections:
                    self.connections[conn].send(data)
            # Regular send
            else:
                self.connections[conn_id].send(data)

    def _recv_pending(self):
        """
        Receive information from all connections into self.recv_buffer.
        """
        for conn_id in self.connections:
            try:
                data = self.connections[conn_id].recv()

                # Other side disconnected
                if not data:
                    self.conn_disconnected(conn_id)

                else:
                    self._recv_buffer.append((conn_id, data))

            except socket.timeout:
                pass

    def _clean_connections(self):
        """
        Close connections at connectionIDs from closed_conns,
        and delete them from the connection list.
        """
        for conn_id in self._closed_conns:
            self.connections[conn_id].close()
            del self.connections[conn_id]

    def close_conn(self, conn_id):
        """
        Stage a connection to be closed and deleted from the dicts.
        """
        if conn_id in self.connections:
            self._closed_conns.add(conn_id)

    def new_conn(self, host, port=DEFAULT_PORT):
        """
        Create a new Connection object and add it to self.connections.
        """
        self.add_conn(Connection(host, port))

    def add_conn(self, conn):
        """
        Add a Connection object to self.connections, and give it a unique connectionID.
        """
        for i in range(len(self.connections) + 1):
            if i not in self.connections:
                self.connections[i] = conn
                break

    def get_conn_ids(self):
        """
        Return a set of connectionIDs that are active.
        """
        return self.connections.keys() - self._closed_conns

    def close_all_conns(self):
        """
        Close all connections. Should be called on an exit.
        """
        for conn_id in self.connections:
            self.close_conn(conn_id)
        self._clean_connections()

    def conn_disconnected(self, conn_id):
        """
        Gets called when a connection is closed.
        """
        self.close_conn(conn_id)

    def all_disconnected(self):
        """
        Gets called when all connections are closed.
        """
        print(DISCONNECTED_MSG)
        quit()
