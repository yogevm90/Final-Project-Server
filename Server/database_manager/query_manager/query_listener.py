import socket
import threading

from bson.json_util import dumps
from Server.database_manager.exception_types import QueryException
from Server.database_manager.authentication_manager.authentication_manager import AuthenticationManager
from Server.database_manager.data_manager.database_data_manager import DatabaseDataManager
from Server.database_manager.query_manager.query_executor import QueryExecutor
from Server.database_manager.query_manager.query_parser import QueryParser


class QueryListener:
    def __init__(self, port, database_name):
        db_data_manager = DatabaseDataManager(database_name)
        self.query_parser = QueryParser(db_data_manager)
        self.authentication_manager = AuthenticationManager(db_data_manager)
        self.query_executor = QueryExecutor(db_data_manager)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = ('localhost', port)
        self.sock.bind(server_address)
        self.listen_loop = None
        self.listen = False

    def start_listening(self):
        self.listen = True
        self.listen_loop = threading.Thread(target=self.listen_for_requests())
        self.listen_loop.start()

    def stop_listening(self):
        self.listen = False
        self.listen_loop.join()

    def listen_for_requests(self):
        self.sock.listen(1)
        while self.listen:
            connection, client_address = self.sock.accept()
            try:
                while True:
                    data = connection.recv(1000)
                    if data:
                        request = self.query_parser.validate_query(data)
                        self.authentication_manager.authenticate_request(request)
                        response = self.query_executor.execute_query(request)
                        return_data = {'status': '100', 'data': response}
                        connection.sendall(dumps(return_data))
                    else:
                        break
            except QueryException as e:
                response = {'message': e.message}
                return_data = {'status': '500', 'data': response}
                connection.sendall(dumps(return_data))
            finally:
                connection.close()
