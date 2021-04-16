import socket
import threading

from bson.json_util import dumps

from server.database_manager.authentication_manager.authentication_manager import AuthenticationManager
from server.database_manager.data_manager.database_data_manager import DatabaseDataManager
from server.database_manager.exception_types import QueryException
from server.database_manager.interfaces.query_listener_interface import QueryListenerInterface
from server.database_manager.query_manager.query_executor import QueryExecutor
from server.database_manager.query_manager.query_parser import QueryValidator


class QueryListener(QueryListenerInterface):
    _query_validator: QueryValidator
    _authentication_manager: AuthenticationManager
    _query_executor: QueryExecutor
    _sock: socket.socket

    def __init__(self, port: int, database_name: str):
        db_data_manager = DatabaseDataManager(database_name)
        self._authentication_manager = AuthenticationManager(db_data_manager)
        self._query_validator = QueryValidator(db_data_manager, self._authentication_manager)
        self._query_executor = QueryExecutor(db_data_manager)
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = ('localhost', port)
        self._sock.bind(server_address)
        self._listen_loop = None
        self._listen = False

    def start_listening(self):
        self._listen = True
        self._listen_loop = threading.Thread(target=self._listen_for_requests())
        self._listen_loop.start()

    def stop_listening(self):
        self._listen = False
        self._listen_loop.join()

    def _listen_for_requests(self):
        self._sock.listen(1)
        while self._listen:
            connection, client_address = self._sock.accept()
            try:
                while True:
                    data = connection.recv(1024)
                    if data:
                        request = self._query_validator.validate_query(data)
                        self._authentication_manager.authenticate_request(request)
                        response = self._query_executor.execute_query(request)
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
