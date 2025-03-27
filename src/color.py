import RcuFunction

KEY_COLOR = "color"
KEY_RED = "r"
KEY_GREEN = "g"
KEY_BLUE = "b"

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
            "color": {
                KEY_RED: self.r,
                KEY_GREEN: self.g,
                KEY_BLUE: self.b,
            }
        }
    def to_npColor(self):
        return (self.r,self.g,self.b)
    
    @staticmethod
    def from_loadedJson(jsonLoadedObj):
        return Color(
            jsonLoadedObj["id"],
            jsonLoadedObj[KEY_RED],
            jsonLoadedObj[KEY_GREEN],
            jsonLoadedObj[KEY_BLUE],
        )
        

