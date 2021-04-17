import traceback
from typing import Dict

from server.database_manager.data_manager.database_data_manager import DatabaseDataManager
from server.database_manager.exception_types import OperationFailedException
from server.database_manager.interfaces.query_executor_interface import QueryExecutorInterface
from utilities.logging.scholapp_server_logger import ScholappLogger


class QueryExecutor(QueryExecutorInterface):
    _data_manager: DatabaseDataManager

    def __init__(self, db_data_manager: DatabaseDataManager):
        self._data_manager = db_data_manager

    def execute_query(self, request: Dict):
        try:
            request_type = request['type']
            request_location = request['location']
            request_object_name = request['name']
            request_data = request['data']
            if request_type == 'get':
                return self._get_request(request_location, request_object_name)
            else:
                if request_location == 'user':
                    document = self._data_manager.get_user_by_name(request_object_name)
                    for key in document:
                        if key in request_data:
                            document[key] = request_data[key]
                    self._data_manager.update_user(request_object_name, document)
                else:
                    document = self._data_manager.get_class_by_name(request_object_name)
                    for key in document:
                        if key in request_data:
                            document[key] = request_data[key]
                    self._data_manager.update_class(request_object_name, document)
                return self._get_request(request_location, request_object_name)
        except Exception as e:
            ScholappLogger.error(traceback.format_exc())
            raise OperationFailedException(f"Failed executing set request {request}\n error: {e}")

    def _get_request(self, request_location, request_object_name):
        try:
            if request_location == 'user':
                user_document = self._data_manager.get_user_by_name(request_object_name)
                user_details = user_document['details']
                return user_details
            else:
                class_document = self._data_manager.get_class_by_name(request_object_name)
                return class_document
        except Exception as e:
            ScholappLogger.error(traceback.format_exc())
            raise OperationFailedException(f"Failed executing get request {request_object_name}\n error: {e}")
