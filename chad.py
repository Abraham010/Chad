# IMPORTS
import socket

# CONSTANTS
SOCK_TIMEOUT = 0.1
RECV_SIZE = 4096

# SEND CODES
BYTES = 0

# MESSAGES

DISCONNECTED_MSG = 'All connections closed.'

EXITING_MSG = 'Exiting...'

# CLASSES


class ConnectionList(object):
    def __init__(self, sockets):
        """
        self.connections is a dictionary of {connectionID: socket}
        self.conn_names is a dictionary of {conn_name: connectionID}
        self.name_conns is a dictionary of {connectionID: conn_name}

        connectionIDs are ints allocated to identify a connection.
        conn_names are names that identify connections.
        """
        check_type(sockets, socket.socket)

        for soc in sockets:
            soc.settimeout(SOCK_TIMEOUT)

        self.sockets = {i: sockets[i] for i in range(len(sockets))}
        self.conn_names = dict()
        self.name_conns = dict()

        # List of conn_ids that are staged for closing and deletion.
        self.closed_conns = list()

    def new_conn(self, host, port):
        new_c = socket.create_connection((host, port))
        new_c.settimeout(SOCK_TIMEOUT)
        self.add_conn(new_c)

    def add_conn(self, soc):
        """
        Add a socket object to self.sockets, and give it a unique conn_id.
        """
        for i in range(len(self.sockets) + 1):
            if i not in self.sockets:
                self.sockets[i] = soc
                break

    def close_conn(self, conn_id):
        """
        Stage a connection to be closed and deleted from the dicts.
        """
        self.closed_conns.append(conn_id)

    def clean_list(self):
        """
        Deletes closed connections from the dicts.
        """
        for conn_id in self.closed_conns:
            self.sockets[conn_id].close()
            # del self.conn_names[self.name_conns[conn_id]]
            # del self.name_conns[conn_id]
            del self.sockets[conn_id]

    def get_socket(self, conn_id):
        return self.sockets[conn_id][0]

    def get_conn(self, conn_name):
        return self.conn_names[conn_name]

    def set_name(self, name, conn_id):
        check_type(name, bytes, str)
        check_type(conn_id, int)
        if type(name) == str:
            name = name.encode()
        if name not in self.conn_names:
            self.conn_names[name] = conn_id
            self.name_conns[conn_id] = name
            return True
        return False


class ChadClient(object):
    def __init__(self, *connections, client_name=None):
        """
        Base Chad client class.
        Handles the communication with other clients for a session.
        :param connections: (list of socket) sockets connected to other clients.
        :param client_name: (bytes) the name of this client.
        """
        check_type(client_name, bytes, type(None))
        self.client_name = client_name

        self.connections = ConnectionList(connections)

        # Buffer for information waiting to be sent.
        self.send_buffer = list()
        # Buffer for information waiting to be received and processed.
        self.recv_buffer = list()
        # An item in a buffer should be in the form of: (connectionID, info)

    def communicate(self):
        if len(self.connections.sockets) == 0:
            self.exit(DISCONNECTED_MSG)
        self.send_pending()
        self.recv_pending()
        self.connections.clean_list()

    def send_pending(self):
        """
        Sends information from self.send_buffer to through the corresponding connection.
        """
        while len(self.send_buffer) > 0:
            message = self.send_buffer.pop(0)
            send(self.connections.sockets[message[0]], message[1], BYTES)

    def recv_pending(self):
        """
        Receive information from all connections into self.recv_buffer.
        """
        for conn_id in range(len(self.connections.sockets)):
            if conn_id in self.connections.sockets:
                try:
                    data = self.connections.sockets[conn_id].recv(RECV_SIZE)

                    # Other side disconnected
                    if not data:
                        self.connections.close_conn(conn_id)

                    else:
                        self.recv_buffer.append((conn_id, data))

                except socket.timeout:
                    pass

    def close_conn(self, conn_id):
        self.connections.close_conn(conn_id)

    def new_conn(self, host, port):
        self.connections.new_conn(host, port)

    def exit(self, message=None):
        for conn_id in self.connections.sockets:
            self.connections.close_conn(conn_id)
        self.connections.clean_list()
        self._exit(message)

    def _exit(self, message=None):
        """
        Exit method to be overwritten in Chad applications.
        """
        if message:
            print(message)
        print(EXITING_MSG)


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


def send(soc, data, code=BYTES):
    if code == BYTES:
        soc.sendall(data)
