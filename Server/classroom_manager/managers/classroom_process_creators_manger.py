from typing import Dict

from classroom_manager.classroom.classroom_config import ClassroomConfig
from classroom_manager.classroom.user import User
from classroom_manager.managers.interfaces.process_manager_interface import ProcessManagerInterface
from classroom_manager.process_creators.classroom_process_creator import ClassroomProcessCreator


class ClassroomProcessCreatorsManager(ProcessManagerInterface):
    _CLASSROOMS: Dict[str, ClassroomProcessCreator]

    @staticmethod
    def initialize(data):
        ClassroomProcessCreatorsManager._CLASSROOMS = {}

    @staticmethod
    def manage(new_class_config: ClassroomConfig):
        new_classroom_obj = ClassroomProcessCreator(class_id=new_class_config.ID,
                                                    class_room_users_ids=new_class_config.UserIds,
                                                    working_dir=new_class_config.WorkingDir)
        new_classroom_obj.create_process()

        ClassroomProcessCreatorsManager._CLASSROOMS[new_class_config.ID] = new_classroom_obj

    @staticmethod
    def register_user_to_class(user: User, classroom_id):
        classroom = ClassroomProcessCreatorsManager._CLASSROOMS[classroom_id]
        classroom.add_user(user)

    @staticmethod
    def unregister_user_to_class(user: User, classroom_id):
        classroom = ClassroomProcessCreatorsManager._CLASSROOMS[classroom_id]
        classroom.remove_user(user)

    @staticmethod
    def close_classroom(classroom_id):
        classroom = ClassroomProcessCreatorsManager._CLASSROOMS[classroom_id]
        classroom.stop()
        del classroom
