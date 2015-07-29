Intro
########


This is application to prevent you from spending to much time in computer.

The EyeNotifier measures your work time and popups notification - time to take a
relax and plays short mp3 file.

Relax time - 15 minutes is measured also, after elapse of this time you will get
other notification - time to work.

If you block a screen during relax time, EyeNotifier will measure time delta
from block screen till next unblock and here possible 2 options:

    1. Before was relax state. If delta time more than time assigned to relax
    state, EyeNotifier switches to work state.

    2. Before was work state. State will be continued.

If you block screen in work or relax state, difference from start the state to
time of block screen (elapsed state) will be remembered by the state.



Installation
==============

To install EyeNotifier please run next commands:

    python setup.py install

this command should be run in the directory of the project, than

    pip install -r requirements.txt

depending on your settings possible use of <sudo> command.


Tests
=========

To run tests, please comment line #240 (self.process())