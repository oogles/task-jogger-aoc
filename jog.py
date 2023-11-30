import os
import sys

from jogger.tasks import LintTask
from jogger.tasks._release import ReleaseTask

# Allow absolute import of the `aoc` package, despite it not
# being installed on the system path
path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, path)

from aoc.tasks import AdventOfCodeTask  # noqa: E402


class RuffLintTask(LintTask):
    
    def handle_python(self, explicit):
        
        self.stdout.write('Running ruff...', style='label')
        result = self.cli('ruff check .')
        self.outcomes['ruff'] = result.returncode == 0
        self.stdout.write('')  # newline


tasks = {
    'aoc': AdventOfCodeTask,
    'lint': RuffLintTask,
    'release': ReleaseTask
}
