#!/usr/bin/env python
# Script to preserve eyes and productivity
# Script is combination of timer and notifier
# Created : 30-06-2015
# Author  : Andras Gyacsok

import gobject
import dbus
import multiprocessing
import os
import pynotify
import Queue
import select
import socket
import time

from dbus.mainloop.glib import DBusGMainLoop
from pygame import mixer


def notify(summary, body='', app_name='', app_icon='',
           timeout=5000, actions=[], hints={}, replaces_id=0):
        _bus_name = 'org.freedesktop.Notifications'
        _object_path = '/org/freedesktop/Notifications'
        _interface_name = _bus_name

        session_bus = dbus.SessionBus()
        obj = session_bus.get_object(_bus_name, _object_path)
        interface = dbus.Interface(obj, _interface_name)
        interface.Notify(app_name, replaces_id, app_icon, summary,
                         body, actions, hints, timeout)


def send_message(title, message, img=''):
    notify(title, message, app_icon=img)


def sendmessage(title, message, img=''):
    pynotify.init("Test")
    notice = pynotify.Notification(title, message, img)
    notice.show()
    return


def check_existence(path):
    if not os.path.exists(path):
        raise Exception("File %s does not exists" % (path))
    return True


def _full_path(path):
    base = os.path.dirname(os.path.abspath(__file__))
    if type(path) in [list, tuple]:
        path = [os.path.join(base, i) for i in path]
        for p in path:
            check_existence(p)
    else:
        path = os.path.join(base, path)
        check_existence(path)
    return path


class State(object):
    def __init__(self):
        self.name = "State"
        self.process_time = 0
        self.title = ''
        self.message = ''
        self._next_state = None
        self.elapsed = 0

    def next_state(self):
        self.elapsed = 0
        return self._next_state

    def notify_state(self):
        timeout_min = (self.process_time - self.elapsed) / 60
        title = "Notification"
        message = "You now in %s state and it finishes through %s minutes" % (
            self.name, timeout_min)
        img = _full_path('img/bell.png')
        sendmessage(title, message, img)

    def get_timeout(self):
        return int(self.process_time - self.elapsed)


class WorkState(State):
    def __init__(self):
        self.name = "Work"
        self.process_time = 45 * 60
        self.title = "Time to play"
        self.message = "Let's earn good money in an interesting play"
        self.track = _full_path('music/drum-patterns-march-1.mp3')
        self.image = _full_path('img/money_increase.png')
        self._next_state = RelaxState(self)
        self.waiting_state = WaitingState(self)


class RelaxState(State):
    def __init__(self, startState=None):
        self.name = "Relax"
        self.process_time = 15 * 60
        self.title = "Time to relax"
        self.message = "Let's relax"
        self.track = _full_path('music/be-gentle-with-yourself.mp3')
        self.image = _full_path('img/ying_yang.png')
        self._next_state = startState if startState else WorkState()
        self.waiting_state = WaitingState(self)


class WaitingState(State):
    def __init__(self, trigger_obj):
        self.name = "Waiting"
        self.process_time = 8 * 60 * 60
        self.waiting_state = trigger_obj

    def get_timeout(self):
        return self.process_time


class Timer(object):
    def __init__(self, sock):
        self.sock = sock

    def timer(self, end):
        mins = 0
        while mins != end:
            time.sleep(60)
            mins += 1

    def socket_timer(self, timeout):
        empty = False
        elapsed = 0
        start_time = int(time.time())

        stdin, stdut, stderr = select.select([self.sock],[],[], timeout)
        if stdin:
            for desc in stdin:
                print desc.recv(1024)
            elapsed = time.time() - start_time
            return elapsed, empty
        empty = True
        return elapsed, empty


class Player(object):
    def __init__(self):
        self.mixer = mixer
        self.mixer.init()

    def play(self, track_path):
        self.mixer.music.load(track_path)
        mixer.music.play()
        # HINT: ensure that sound will be played during 20 sec and than
        # changed to another sound
        time.sleep(20)


class ScreenState(object):
    """Class process Dbus ScreenSaver signal and notifies main Timer thread.
       Potentially possible to use:
           'org.freedesktop.ScreenSaver'
           'org.gnome.ScreenSaver'
       or other Screen Savers.
       Now only gnome is supported by my workstation.
    """
    def __init__(self, sock):
        main_loop = DBusGMainLoop(set_as_default=True)
        session = dbus.SessionBus(mainloop=main_loop)
        screen_proxy = session.get_object('org.gnome.ScreenSaver',
                                          '/org/gnome/ScreenSaver')
        self.iface = dbus.Interface(screen_proxy, 'org.gnome.ScreenSaver')
        self.iface.connect_to_signal('ActiveChanged', self.listen)
        self.sock = sock

    def process(self):
        gobject.MainLoop().run()

    def listen(self, *args, **kwargs):
        self.sock.sendall("1")
        print "Put event"

    def get_screen_state(self):
        return self.iface.GetActive()


class Engine():
    def __init__(self, sock=None):
        self.state = WorkState()
        self.timer = Timer(sock)
        self.player = Player()

    def process(self):
        timeout = self.state.get_timeout()
        elapsed, empty = self.timer.socket_timer(timeout)
        self.process_event(elapsed, empty)

    def process_event(self, elapsed=0, empty=False):
        timeout = 0
        if isinstance(self.state, WaitingState) and not empty:
            w_state = self.state.waiting_state
            w_state.elapsed += elapsed

            if (isinstance(w_state, RelaxState) and
                        w_state.process_time < w_state.elapsed):
                self.state = w_state.next_state()
                sendmessage(self.state.title,
                            self.state.message,
                            self.state.image)
                self.player.play(self.state.track)
            else:
                self.state = self.state.waiting_state
                self.state.notify_state()
            elapsed = 0
            print "Process Activate"
        elif elapsed:
            self.state.elapsed = elapsed
            self.state = WaitingState(self.state)
            print "Waiting state"
        elif empty:
            self.state = self.state.next_state()
            sendmessage(self.state.title, self.state.message, self.state.image)
            self.player.play(self.state.track)
            print "New state"
        self.process()


def main():
    parent, child = socket.socketpair()
    engine = Engine(parent)
    screen = ScreenState(child)
    listener = multiprocessing.Process(target=screen.process)
    listener.daemon = True
    listener.start()
    print "Start Engine"
    engine.process()


if __name__ == "__main__":
    main()