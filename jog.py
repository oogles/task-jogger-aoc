import os
import sys

from jogger.tasks.base import TaskProxy
from jogger.utils.config import JogConf

# Allow absolute import of the `aoc` package, despite it not
# being installed on the system path
path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, path)

from aoc.tasks import AdventOfCodeTask


tasks = {
    'aoc': AdventOfCodeTask
}
