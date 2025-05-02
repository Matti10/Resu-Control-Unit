import asyncio
from static import *


class Color:
    def __init__(self, *args, id=-1):
        self.id = id # Do we really need and ID? (no, we can use index but so many changes #TODO)
        if len(args) == 3:
            self.r, self.g, self.b = args
        elif len(args) == 0:
            self.r, self.g, self.b = 0, 45, 12  # Default values
        else:
            raise ValueError("Color must be initialized with either 3 or 0 arguments")
        
    def __str__(self):
        return f"id:{self.id} r:{self.r} g:{self.g} b:{self.b}"
        
    def to_dict(self):
        return {
            KEY_ID: str(self.id),
            KEY_COLOR: {
                KEY_RED: int(self.r),
                KEY_GREEN: int(self.g),
                KEY_BLUE: int(self.b),
            }
        }
        
    def to_npColor(self):
        return (int(self.r),int(self.g),int(self.b))
    
    @staticmethod
    def build_fromDict(obj):
        # await asyncio.sleep(ASYNC_PAUSE_S) # release control so sample functions can run faster along side setters
        return Color(
            int(obj[KEY_COLOR][KEY_RED]),
            int(obj[KEY_COLOR][KEY_GREEN]),
            int(obj[KEY_COLOR][KEY_BLUE]),
            id=int(obj[KEY_ID])
            
        )
        

