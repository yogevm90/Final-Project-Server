from typing import Dict

from server.classroom_manager.classroom.classroom_config import ClassroomConfig
from server.classroom_manager.classroom.user import User
from server.classroom_manager.managers.interfaces.process_manager_interface import ProcessManagerInterface
from server.classroom_manager.process_creators.classroom_process_creator import ClassroomProcessCreator


class ClassroomProcessCreatorsManager(ProcessManagerInterface):
    """
    Class for managing all classroom processes
    """
    _CLASSROOMS: Dict[str, ClassroomProcessCreator] = {}

    @staticmethod
    def initialize(classrooms=None):
        """
        Initialize the manager
        :param classrooms: classrooms to initialize with
        """
        if classrooms:
            ClassroomProcessCreatorsManager._CLASSROOMS = classrooms

    @staticmethod
    def manage(new_class_config: ClassroomConfig):
        """
        By a given configuration, add a new class to the manager.

        :param new_class_config: new class ClassroomConfig object
        """
        new_classroom_obj = ClassroomProcessCreator(class_id=new_class_config.ID,
                                                    class_room_users_ids=new_class_config.UserIds,
                                                    working_dir=new_class_config.WorkingDir)
        new_classroom_obj.create_process()

        ClassroomProcessCreatorsManager._CLASSROOMS[new_class_config.ID] = new_classroom_obj

    @staticmethod
    def register_user_to_class(user: User, classroom_id):
        """
        Add a new user to class.

        :param user: user to add
        :param classroom_id: classroom id
        """
        classroom = ClassroomProcessCreatorsManager._CLASSROOMS[classroom_id]
        classroom.add_user(user)

    @staticmethod
    def unregister_user_to_class(user: User, classroom_id):
        """
        Remove user from class.

        :param user: user to remove
        :param classroom_id: classromm id
        """
        classroom = ClassroomProcessCreatorsManager._CLASSROOMS[classroom_id]
        classroom.remove_user(user)

    @staticmethod
    def close_classroom(classroom_id):
        """
        Close a given class by id.

        :param classroom_id: classroom id to close
        """
        if classroom_id in ClassroomProcessCreatorsManager._CLASSROOMS:
            classroom = ClassroomProcessCreatorsManager._CLASSROOMS[classroom_id]
            classroom.stop()
            del classroom
        else:
            AttributeError(f"The classroom id {classroom_id} is not a classroom")

    @staticmethod
    def is_user_in_class(user_id, class_id):
        """
        :param user_id: user id to check
        :param class_id: class id to check
        :return: True - user id is in class ; False - O.W.
        """
        classroom = ClassroomProcessCreatorsManager._CLASSROOMS[class_id]
        if classroom.get_user(user_id):
            return True
        return False

    @staticmethod
    def get_classroom_by_user_id(user_id):
        """
        Get the class object of the user by its id.

        :param user_id: user id
        :return: ClassroomProcessCreator object
        """
        for class_id, class_obj in ClassroomProcessCreatorsManager._CLASSROOMS.items():
            if ClassroomProcessCreatorsManager.is_user_in_class(user_id, class_id):
                return class_obj
        return None

