"""
  UC101: Create project(s)
"""

from qgate.uc.ucbase import UCBase
from qgate.output import Output
from qgate.solution import Solution


class UC101(UCBase):

    def __init__(self, sln: Solution, output: Output):
        super().__init__(sln, output, self.__class__.__name__)

    @property
    def desc(self) -> str:
        return "Create project(s)"

    @property
    def long_desc(self):
        return "Create project with setting name, description and tags"

    def exec(self):
        self.sln.create_projects(self)


