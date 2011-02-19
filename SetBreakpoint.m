
#import "SetBreakpoint.h"


@implementation SetBreakpoint

/* This class implements a verb that receives a number of arguments
and returns a string value (either a copy of the prose parameter
enclosed in quotes or, if the prose parameter is not provided, a
copy of the direct parameter enclosed in quotes). */


- (id)performDefaultImplementation {
    [[[NSApplication sharedApplication] delegate] toggleBreakpoint:[self directParameter]];
	
	return @"success";
}



@end
