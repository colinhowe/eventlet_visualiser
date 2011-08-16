import time
import traceback

import eventlet.corolocal
import eventlet.greenthread

old_main = None
out = None

def new_main(self, *args):
    global old_main
    _id = id(self)
    try:
        out.write('S\n%s\n%s\n%s\n' % (
            _id,
            time.time(),
            repr(args).replace('\n', '\\n'),
        ))
        return old_main(self, *args)
    finally:
        out.write('E\n%s\n%s\n' % (
            _id,
            time.time(),
        ))
        out.flush()

def new_init(self, parent):
    global old_init
    _id = id(self)
    stack = traceback.format_stack()
    out.write('C\n%s\n%s\n%s\n' % (
        _id,
        time.time(),
        stack,
    ))
    old_init(self, parent)


def patch_eventlet(_out):
    if hasattr(eventlet.greenthread.GreenThread, 'vpatched'):
        return
    eventlet.greenthread.GreenThread.vpatched = True

    global out
    out = _out

    global old_main
    old_main = eventlet.greenthread.GreenThread.main
    eventlet.greenthread.GreenThread.main = new_main

    global old_init
    old_init = eventlet.greenthread.GreenThread.__init__
    eventlet.greenthread.GreenThread.__init__ = new_init
