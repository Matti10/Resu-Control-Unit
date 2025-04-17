# TODO do we need to establish how to only store the pins we need in RAM?? Maybe a separate pins file? Or we only load pins that have a func assigned? Might be worth seeing how bad ram useage is and optimising from there


from static import *

# class RcuPin:
#     def __init__(
#         self, 
#         pinNum,
#         func
#     ):
#         self.pinNum = pinNum
#         self.func = func
        
class RcuPins:
    def __init__(
        self,  
        pinConfig,
    ):
        self.pinConfig = pinConfig
    
        
    def set_pin(self, pinID, pinFuncName, overwrite=False, callback=lambda:None):
        if not overwrite and self.pinConfig[pinID][RCUFUNC_KEY_TYPE] != PIN_UNASSIGN_NAME:
            raise PinAssigned(pinID)
        
        self.pinConfig[pinID][RCUFUNC_KEY_TYPE] = pinFuncName
        
        callback(self.pinConfig[pinID])


    def unassign_pin(self, pinID):
        self.pinConfig[pinID][RCUFUNC_KEY_TYPE] = PIN_UNASSIGN_NAME
            
            
    # def unassign_on_funcName(self,funcID):
        #raise "this shit wont work"
    #     pins = self.get_funcs_pins(funcID)
    #     try:
    #         [self.unassign_pin(pinID) for pinID in pins]
    #     except PinsNotAssigned:
    #         pass  # its already unassigned!

    def get_funcs_pins(self, funcID):
        pins = []
        # discover assigned pins
        for pinId in self.pinConfig:
            if funcID in self.pinConfig[pinId][RCUFUNC_KEY_TYPE]:
                pins.append(self.pinConfig[pinId])

        if pins == []:
            raise PinsNotAssigned

        return pins
    
    def to_dict(self):
        return self.pinConfig
    
    # def post(self,data,id):
