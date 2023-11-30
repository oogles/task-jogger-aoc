=========================================
Advent of Code Solution Runner for Python
=========================================

This project provides a structural template and runner for `Advent of Code <https://adventofcode.com/>`_ solutions written in Python. It is built on top of `jogger` (https://github.com/oogles/task-jogger).


Installation
============

The latest stable version can be installed from PyPI::

    pip install task-jogger-aoc

The following dependencies will also be installed:

* ``jogger``: The underlying task running system. See: https://github.com/oogles/task-jogger.


Quickstart
==========

Add a ``jog.py`` file including ``AdventOfCodeTask``:

.. code-block:: python
    
    from aoc.tasks import AdventOfCodeTask
    
    tasks = {
        'aoc': AdventOfCodeTask
    }

Assuming a task name of ``aoc``, as used in the above example, create a template for solving the next puzzle using::

    $ jog aoc --next
    or
    $ jog aoc -n

This will create a subdirectory for the next day's puzzle that doesn't already have one, using day 1 by default. E.g. ``solutions/day01/``. This subdirectory contains:

* ``solvers.py``: A module containing ``part1()`` and ``part2()`` functions for solving the respective parts of the puzzle (it's up to you to implement these). It also optionally contains an ``input_parser`` function (see `Input parsing`_ below).
* ``input``: A file to contain the puzzle input. This can be populated automatically if you have a session cookie set (see `Configuration`_ below). Otherwise, it must be populated manually.

Once at least one solver is implemented, the latest puzzle can be run using::

    $ jog aoc

To run the solvers using sample data instead of the full input data, use::

    $ jog aoc --sample
    or
    $ jog aoc -s

When using sample data, you will be prompted to enter separate sample data for each part of the puzzle. Part 2 will offer the choice to use the same sample data as part 1. Entered sample data will be saved to ``solutions/day01/sample1`` and ``solutions/day01/sample2``, respectively, and the prompt will not be shown again.

Each part of the puzzle can be run independently using::

    $ jog aoc --part1
    or
    $ jog aoc -1

    $ jog aoc --part2
    or
    $ jog aoc -2

Finally, you can specify an exact puzzle using the day's number. E.g. for day 12::

    $ jog aoc 12

This will create a puzzle subdirectory if it doesn't already exist, and run the solvers within if it does.


Configuration
=============

No configuration is necessary, but the following settings are available. They can be configured using `any compatible config file <https://task-jogger.readthedocs.io/en/stable/topics/config.html>`_ recognised by ``jogger``.

* ``year``: The year of the Advent of Code challenge being attempted. Controls verifying puzzle availability and downloading puzzle input data. This setting is optional (it defaults to the current year) but recommended. Without it, you can't re-run solutions from previous years, or continue to work on puzzles after December 31.
* ``session_cookie``: The value of your cookie for an authenticated session at https://adventofcode.com. Used to download puzzle input, which is unique per user. If not provided, puzzle input cannot be downloaded and must be populated manually. It is **strongly recommended** to put this setting in ``joggerenv.cfg`` and ignore/exclude that file from any version control in use.


Input parsing
=============

A ``solvers.py`` file can optionally contain an ``input_parser`` attribute, which should reference a function that takes a single argument (the raw input data) and returns a value to be passed to the solvers. This can be used to parse the input data into a more convenient format for the solvers to work with. If not present, the raw input data will be passed to the solvers as-is.

Specifying an ``input_parser`` is useful when the input needs to be processed in the same way for both parts of the puzzle. If only one part requires certain processing, that logic can and should reside in the solver itself.

The ``solvers.py`` template created when initialising a new puzzle contains a default value for ``input_parser`` that splits the input data into lines, as this is a common format for puzzle input. This can be removed or altered if need be.

A handful of parsers for common puzzle input formatters are provided in ``aoc.utils.parsing``. These can be provided as values for ``input_parser``. Available options are:

* ``split_lines``: Splits the input data into lines and returns a ``list`` of strings.
* ``int_lines``: Splits the input data into lines and returns a ``list`` of integers.
* ``split_commas``: Splits the input data into comma-separated values and returns a ``list`` of strings.
* ``int_commas``: Splits the input data into comma-separated values and returns a ``list`` of integers.

It is also possible to provide a custom parser function:

.. code-block:: python
    
    # solvers.py
    
    def input_parser(input_data):
        
        # Calculate the sum of each "group" of line-separated integers.
        # Each group is separated by two line breaks.
        return [sum(map(int, input_item.split('\n'))) for group in input_data.split('\n\n')]
