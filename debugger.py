# coding=UTF-8
from Foundation import *
from AppKit import *
import bdb

# http://docs.python.org/library/bdb.html

class Debugger(bdb.Bdb):        
    go = False
    #def user_call(self, frame, argument_list):
    #    return
        
    def user_line(self, frame):
        """This function is called when we stop or break at this line."""
        print 'waiting...'
        self.delegate.outputFrame(frame)
        while not self.go:
            #NSRunLoop.currentRunLoop().runMode_beforeDate_(NSDefaultRunLoopMode, NSDate.dateWithTimeIntervalSinceNow_(0.1))
            NSThread.sleepForTimeInterval_(0.1)
        self.go = False
        print 'broke out of user_line'
    
    def runscript(self, filename):
        # Start with fresh empty copy of globals and locals and tell the script
        # that it's being run as __main__ to avoid scripts being able to access
        # the debugger's namespace.
        globals_ = {"__name__" : "__main__", "__file__": filename }
        locals_ = globals_

        # When bdb sets tracing, a number of call and line events happens
        # BEFORE debugger even reaches user's code (and the exact sequence of
        # events depends on python version). So we take special measures to
        # avoid stopping before we reach the main script (see user_line and
        # user_call for details).
        self._wait_for_mainpyfile = 1
        self.mainpyfile = self.canonic(filename)
        statement = 'execfile( "%s")' % filename
        self.run(statement, globals=globals_, locals=locals_)