#import <Cocoa/Cocoa.h>

/* This class implements a verb that receives a number of arguments
and returns a string value (either a copy of the prose parameter
enclosed in quotes or, if the prose parameter is not provided, a
copy of the direct parameter enclosed in quotes). */
@interface SetBreakpoint : NSScriptCommand {

}
- (id)performDefaultImplementation;

@end
