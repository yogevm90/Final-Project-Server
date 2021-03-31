from typing import Dict


class CustomImporter(object):
    _LOADED_MODULES = {}

    @staticmethod
    def import_object(module_data: Dict):
        if module_data["name"] in CustomImporter._LOADED_MODULES:
            return CustomImporter._LOADED_MODULES[module_data["name"]]
        module = __import__(module_data["module"])
        module_names = module_data["module"].split(".")
        for module_name in module_names:
            if module_name in module.__dict__:
                module = module.__dict__[module_name]
        loaded_module = module.__dict__[module_data["name"]]
        CustomImporter._LOADED_MODULES[module_data["name"]] = loaded_module
        return loaded_module
