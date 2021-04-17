import json
import os
from pathlib import Path

from jinja2 import Environment, PackageLoader


class TestReportGenerator(object):
    """
    Class for generating a test report html
    """
    def __init__(self):
        self._template = Path(os.path.dirname(__file__)) / "templates" / "report_template.html"

    def generate_report(self, source: Path, dest: str):
        """
        Generate a report by a JSON in source and into dest

        :param source: test summary JSON
        :param dest: destination for the report
        """
        orig_cwd = os.getcwd()
        os.chdir(os.path.dirname(__file__))
        test_sol = json.loads(source.read_text())

        env = Environment(loader=PackageLoader(TestReportGenerator.__module__, "templates"))
        template = env.from_string(self._template.read_text())
        with open(dest, "w") as dest_file:
            dest_file.write(template.render(username=test_sol["username"],
                                            test_id=test_sol["test_id"],
                                            answers=test_sol["answers"]))
        os.chdir(orig_cwd)
