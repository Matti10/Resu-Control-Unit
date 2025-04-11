import RcuFunction
from static import *


class Color:
    def __init__(self, id, *args):
        self.id = id # Do we really need and ID? (no, we can use index but so many changes #TODO)
        if len(args) == 3:
            self.r, self.g, self.b = args
        elif len(args) == 0:
            self.r, self.g, self.b = 0, 45, 12  # Default values
        else:
            raise ValueError("Color must be initialized with either 3 or 0 arguments")
        
    def to_dict(self):
        return {
            RcuFunction.RCUFUNC_KEY_ID: self.id,
            KEY_COLOR: {
                KEY_RED: self.r,
                KEY_GREEN: self.g,
                KEY_BLUE: self.b,
            }
        }
    def to_npColor(self):
        return (self.r,self.g,self.b)
    
    @staticmethod
    def build_fromDict(obj):
        return Color(
            obj[RCUFUNC_KEY_ID],
            obj[KEY_RED],
            obj[KEY_GREEN],
            obj[KEY_BLUE],
        )
        

