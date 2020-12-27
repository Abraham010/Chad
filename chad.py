# IMPORTS
import socket
import threading

# CONSTANTS
SOCK_TIMEOUT = 0.01
RECV_SIZE = 4096
DEFAULT_PORT = 55555
BROADCAST = None

# CONNECTION STATUS CODES
LISTENING = 0
ACTIVE = 1

# SEND CODES
BYTES = 0

# MESSAGES

DISCONNECTED_MSG = 'All connections closed.'

EXITING_MSG = 'Exiting...'


# CLASSES

class Timeout(Exception):
    pass


class Connection(object):
    """
    Connection object, representing a connection of various types. (Currently just regular TCP)
    -- MAIN METHODS --
    send, recv, close
    """
    def __init__(self, host, port, conn_type='TCP'):
        """
        Object representing a connection to a client.
        :param host: (str or bytes) ip of host the connection is to.
            If host is None, will listen for connections on the port.
        :param port: (int) port of the host client to connect to.
        """
        if conn_type == 'TCP':

            # MISSING ERROR HANDLING

            if host is not None:
                self.socket = socket.create_connection((host, port))
                self.socket.settimeout(SOCK_TIMEOUT)
                self.status = ACTIVE
            else:
                self.socket = socket.socket()
                self.socket.bind(('', port))
                self.status = LISTENING
        else:
            raise ValueError('Chad does not support connections of this type')

        self.conn_type = conn_type

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
        if self.conn_type == 'TCP':
            self.socket.close()

    def send(self, data):
        if self.conn_type == 'TCP':
            return self.socket.send(data)

    def recv(self, bufsize=RECV_SIZE):
        if self.conn_type == 'TCP':
            try:
                return self.socket.recv(bufsize)
            except socket.timeout:
                raise Timeout


class ChadClient(object):
    """
    Chad Client - manages multiple connections and supplies multiple functions
    for live sending and receiving of data.

    Methods that should be used by Chad-Powered applications are as described below:

    -- MAIN METHODS --
    stage_send, receive, communication_loop, close_conn

    -- USEFUL METHODS --
    new_conn, get_conn_ids, close_all_conns, incoming_data

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
            self._add_conn(conn)

        self._closed_conns = set()

        # Buffer for information waiting to be sent.
        self._send_buffer = list()
        # Buffer for information waiting to be received and processed.
        self._recv_buffer = list()
        # An item in a buffer should be in the form of: (connectionID, bytes)

        # For communicate_loop
        self.running = True

    def _communicate(self):
        """
        Main function for the client: should be run in a loop.
        Send all data that is staged for sending (in send_buffer) and
        receive data from all connections into recv_buffer.
        Also close any pending connections and call all_disconnected if no more connections are active.
        """
        if len(self.connections) == 0:
            self.all_disconnected()

        self._recv_pending()
        self._clean_connections()
        self._send_pending()

    def _recv_pending(self):
        """
        Receive information from all connections into self.recv_buffer.
        """
        for conn_id in self.connections.keys() - self._closed_conns:
            try:
                # DEBUGGING INFO
                print(self.connections.keys() - self._closed_conns)

                data = self.connections[conn_id].recv()

                # Other side disconnected
                if not data:
                    self.conn_disconnected(conn_id)

                else:
                    self._recv_buffer.append((conn_id, data))

            except Timeout:
                pass

    def _send_pending(self):
        """
        Sends information from self.send_buffer through the corresponding connection.
        """
        while len(self._send_buffer) > 0:
            conn_id, data = self._send_buffer.pop(0)

            # Broadcast
            if conn_id == BROADCAST:
                for conn in self.connections:
                    self.connections[conn].send(data)
            # Regular send
            else:
                self.connections[conn_id].send(data)

    def _clean_connections(self):
        """
        Close connections at connectionIDs from closed_conns,
        and delete them from the connection list.
        """
        for conn_id in self._closed_conns:
            self.connections[conn_id].close()
            del self.connections[conn_id]

    def _add_conn(self, conn):
        """
        Add a Connection object to self.connections, and give it a unique connectionID.
        """
        for conn_id in range(len(self.connections) + 1):
            if conn_id not in self.connections:
                self.connections[conn_id] = conn
                return conn_id

    def communication_loop(self):
        """
        Runs communicate in a loop. Recommended to be run in a thread of it's own, to handle communication.
        """
        while self.running:
            self._communicate()
        else:
            self.close_all_conns()
            self._clean_connections()

    def receive(self):
        """
        Return data received from a connection (first item of recv_buffer),
        in the form (connectionID, data).
        """
        if len(self._recv_buffer) > 0:
            return self._recv_buffer.pop(0)

    def stage_send(self, conn_id, data):
        """
        Stage data to be sent to the specified connection (append to send_buffer).
        :param conn_id: (int) connectionID. (None) to broadcast to all connections.
        :param data: (bytes) data to be sent through the connection.
        """
        if (conn_id is None or conn_id in self.connections) and type(data) == bytes:
            self._send_buffer.append((conn_id, data))

    def new_conn(self, host, port=DEFAULT_PORT):
        """
        Create a new Connection object and add it to self.connections.
        """
        self._add_conn(Connection(host, port))

    def incoming_data(self):
        """
        Return the number of items in the recv_buffer.
        """
        return len(self._recv_buffer)

    def get_conn_ids(self):
        """
        Return a set of connectionIDs that are active.
        """
        return self.connections.keys() - self._closed_conns

    def close_conn(self, conn_id):
        """
        Stage a connection to be closed and deleted from the dicts.
        """
        if conn_id in self.connections:
            self._closed_conns.add(conn_id)

    def close_all_conns(self):
        """
        Stage all connections for closing. Should be called on an exit.
        """
        for conn_id in self.connections:
            self.close_conn(conn_id)

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
        self.exit()

    def exit(self):
        """
        Chad exit method for orderly exit.
        """
        self.running = False
