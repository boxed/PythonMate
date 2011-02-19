# -*- coding: UTF-8 -*-
from objc import YES, NO, IBAction, IBOutlet, ivar
from Foundation import *
from AppKit import *
from CoreData import *
import os
import pickle
import inspect

import debugger

def textMate_moveCursor(filename, lineno):
    print 'TextMate:', filename, lineno
    tm_url = 'txmt://open/?url=file://%s&line=%s' % (filename, f.lineno)
    osa_cmd = 'tell application "TextMate" to get url "%s"' % tm_url
    from os import system
    system('osascript -e \'%s\'' % osa_cmd)


class Frame(NSObject):
    lineno = ivar("lineno", objc._C_INT)
    filename = ivar("filename")
    functionName = ivar("functionName")
    
    def setFrame_(self, frame):
        self.frame = frame
        self.lineno = frame.f_lineno
        self.filename = frame.f_code.co_filename
        self.functionName = frame.f_code.co_name

class Variable(NSObject):
    name = ivar("name")
    value = ivar("value")
    
    def setName_Value_(self, name, value):
        self.name, self.value = str(name), str(value)
        
class Breakpoint(NSObject):
    filename = ivar('filename')
    line = ivar('line', objc._C_INT)

    def setFilename_line_(self, filename, line):
        self.filename, self.line = filename, line
        
    def __cmp__(self, other):
        foo = self.filename.__cmp__(other.filename)
        if foo == 0:
            return self.line - other.line
        else:
            return foo
    
    def __eq__(self, other):
        return self.filename == other.filename and self.line == other.line
        
    def __hash__(self):
        return self.filename.__hash__() + self.line
        
    def __repr__(self):
        return '%s:%s' % (self.filename, self.line)

class PythonMate_AppDelegate(NSObject):
    window = IBOutlet()
    stackController = IBOutlet()
    localsController = IBOutlet()
    breakpointsController = IBOutlet()
    stackUI = IBOutlet()
    localsUI = IBOutlet()
    breakpointsUI = IBOutlet()
    
    stack = []
    locals = []
    breakpoints = set()
    breakpointList = []

    def applicationDidFinishLaunching_(self, sender):
        self.window.makeKeyWindow()
        NSThread.detachNewThreadSelector_toTarget_withObject_(self.startDebugger_, self, None)
        #self.stack.append({'key':'foo'})
        #self.window.makeFirstResponder_(self.answer_UI)
        #from pudb import runscript
        #try:
        #    #runscript('debug_me.py')    
        #    from pudb.debugger import Debugger
        #    dbg = Debugger(steal_output=False)
        #    dbg._runscript('debug_me.py')
        #except:
        #    import traceback
        #    traceback.print_exc()
        
    def startDebugger_(self, params):
        self.debugger = debugger.Debugger()
        self.debugger.delegate = self
        pool = NSAutoreleasePool.alloc().init()
        try:
            self.debugger.runscript('/Users/boxed/Projects/PythonMate/debug_me.py')
        except:
            import traceback
            traceback.print_exc()
        print 'breakpoints:', self.debugger.get_all_breaks()
        
    def runDebugger(self):
        self.debugger.go = True
        self.stack[:] = []
        self.locals[:] = []
        self.stackController.rearrangeObjects()
        self.localsController.rearrangeObjects()
    
    @IBAction
    def step_(self, sender):
        self.debugger.set_step()
        self.runDebugger()

    @IBAction
    def next_(self, sender):
        self.debugger.set_next(self.frame)
        self.runDebugger()

    @IBAction
    def out_(self, sender):
        self.debugger.set_return(self.frame)
        self.runDebugger()

    @IBAction
    def until_(self, sender):
        self.debugger.set_until(self.frame)
        self.runDebugger()

    @IBAction
    def continue_(self, sender):
        self.debugger.set_continue()
        self.runDebugger()

    def removeBreakpoint(self, breakpoint):
        self.breakpoints.remove(breakpoint)
        self.debugger.clear_break(breakpoint.filename, breakpoint.line)
    
    def toggleBreakpoint_(self, s):
        file, line_s = s.split(':')
        breakpoint = Breakpoint.alloc().init()
        breakpoint.setFilename_line_(file, int(line_s))
        if breakpoint in self.breakpoints:
            self.removeBreakpoint(breakpoint)
        else:
            self.breakpoints.add(breakpoint)
            self.debugger.set_break(file, int(line_s))
        self.updateBreakpoints()

    def updateBreakpoints(self):
        self.breakpointList[:] = list(self.breakpoints)
        self.breakpointsController.rearrangeObjects()
    
    @IBAction
    def removeBreakpoint_(self, sender):
        self.removeBreakpoint(self.breakpointList[self.breakpointsUI.selectedRow()])
        self.updateBreakpoints()
    
    def applicationSupportFolder(self):
        paths = NSSearchPathForDirectoriesInDomains(NSApplicationSupportDirectory, NSUserDomainMask, YES)
        basePath = paths[0] if (len(paths) > 0) else NSTemporaryDirectory()
        return os.path.join(basePath, "PythonMate")
        
    def tableViewSelectionDidChange_(self, notification):
        self.window.makeFirstResponder_(self.answer_UI)
        
    def applicationShouldTerminate_(self, sender):
        return NSTerminateNow

    ######## GUI #######
    def tableViewSelectionDidChange_(self, notification):
        # selection in stack frame changed, update locals
        if notification.object() == self.stackUI:
            selection = self.stackUI.selectedRow()
            if selection != -1:
                self.outputLocals(self.stack[selection].frame)

    ######## display data ######
    def outputStack(self):
        del self.stack[:]
        frame = self.frame
        while frame.f_back:
            f = Frame.alloc().init()
            f.setFrame_(frame)
            self.stack.append(f)
            if frame == self.frame and f.filename and not f.filename.startswith('<'):
                textMate_moveCursor(f.filename, f.lineno)
            frame = frame.f_back
        self.stackController.rearrangeObjects()
        
    def outputCode(self):
        #co_argcount	number of arguments (not including * or ** args)	 
        #co_code	string of raw compiled bytecode	 
        #co_consts	tuple of constants used in the bytecode	 
        #co_filename	name of file in which this code object was created	 
        #co_firstlineno	number of first line in Python source code	 
        #co_flags	bitmap: 1=optimized | 2=newlocals | 4=*arg | 8=**arg	 
        #co_lnotab	encoded mapping of line numbers to bytecode indices	 
        #co_name	name with which this code object was defined	 
        #co_names	tuple of names of local variables	 
        #co_nlocals	number of local variables	 
        #co_stacksize	virtual machine stack space required	 
        #co_varnames    
        #print code.co_name, code.co_filename
        pass
        
    def outputFrame(self, frame):
        self.frame = frame
        self.outputStack()
        self.outputLocals(frame)
        self.stackUI.selectRowIndexes_byExtendingSelection_(NSIndexSet.indexSetWithIndex_(0), False)
        #try:
        #    self.code.setStringValue_(inspect.getsource(frame))
        #except IOError:
        #    self.code.setStringValue_('<code not available>')
        #f_back	next outer frame object (this frame’s caller)	 
        #f_builtins	builtins namespace seen by this frame	 
        #f_code	code object being executed in this frame	 
        #f_exc_traceback	traceback if raised in this frame, or None	 
        #f_exc_type	exception type if raised in this frame, or None	 
        #f_exc_value	exception value if raised in this frame, or None	 
        #f_globals	global namespace seen by this frame	 
        #f_lasti	index of last attempted instruction in bytecode	 
        #print frame.f_code
        self.outputCode()
        #f_locals	local namespace seen by this frame	 
        #f_restricted	0 or 1 if frame is in restricted execution mode	 
        #f_trace
    
    def outputLocals(self, frame):
        del self.locals[:]
        for name, value in frame.f_locals.items():
            v = Variable.alloc().init()
            v.setName_Value_(name, value)
            self.locals.append(v)
        self.localsController.rearrangeObjects()