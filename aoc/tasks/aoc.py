from pathlib import Path

from jogger.tasks import Task


class AdventOfCodeTask(Task):
    
    help = (
        'Initialise or run the Advent of Code puzzle solver/s for a given day.'
    )
    
    def handle(self, **options):
        
        self.stdout.write('Hello, world!')
