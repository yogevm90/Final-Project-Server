from Server.database_manager.exception_types import OperationFailedException


class QueryExecutor:
    def __init__(self, db_data_manager):
        self.data_manager = db_data_manager

    def execute_query(self, request):
        try:
            request_type = request['type']
            request_location = request['location']
            request_object_name = request['name']
            request_data = request['data']
            if request_type == 'get':
                return self.get_request(request_location, request_object_name)
            else:
                if request_location == 'user':
                    document = self.data_manager.get_user_by_name(request_object_name)
                    for key in document:
                        if key in request_data:
                            document[key] = request_data[key]
                    self.data_manager.update_user(request_object_name, document)
                else:
                    document = self.data_manager.get_class_by_name(request_object_name)
                    for key in document:
                        if key in request_data:
                            document[key] = request_data[key]
                    self.data_manager.update_class(request_object_name, document)
                return self.get_request(request_location, request_object_name)
        except Exception as e:
            raise OperationFailedException('Failed executing set request {}\n error: {}'.format(request, e))

    def get_request(self, request_location, request_object_name):
        try:
            if request_location == 'user':
                user_document = self.data_manager.get_user_by_name(request_object_name)
                user_details = user_document['details']
                return user_details
            else:
                class_document = self.data_manager.get_class_by_name(request_object_name)
                return class_document
        except Exception as e:
            raise OperationFailedException('Failed executing get request {}\n error: {}'.format(request_object_name, e))
