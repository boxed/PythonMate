# coding=UTF-8

#import modules required by application
import objc
import Foundation
import AppKit
import CoreData

from PyObjCTools import AppHelper

# import modules containing classes required to start application and load MainMenu.nib
import PythonMate_AppDelegate

import os
os.putenv("USE_PDB", "1")

# pass control to AppKit
AppHelper.runEventLoop()
