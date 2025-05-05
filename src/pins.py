# TODO do we need to establish how to only store the pins we need in RAM?? Maybe a separate pins file? Or we only load pins that have a func assigned? Might be worth seeing how bad ram useage is and optimising from there


from static import *

# class RcuPin:
#     def __init__(
#         self, 
#         pinID,
#         func
#     ):
#         self.pinID = pinID
#         self.func = func
        
class RcuPins:
    def __init__(
        self,  
        pinConfig,
        instance_register
    ):
        self.pinConfig = pinConfig
        self.instance_register = instance_register
        
    def set_pin(self, pinID, pinFuncName, overwrite=False, callback=lambda:None):
        if not overwrite and self.pinConfig[pinID][RCUFUNC_KEY_TYPE] != PIN_UNASSIGN_NAME:
            raise PinAssigned(pinID)
        
        self.pinConfig[pinID][RCUFUNC_KEY_TYPE] = pinFuncName
        
        callback(self.pinConfig[pinID])

    def unassign_func(self,funcID):
        for pin in self.get_funcs_pins(funcID):
            pin[RCUFUNC_KEY_TYPE] = PIN_UNASSIGN_NAME

    def unassign_pin(self, pinID):
            self.pinConfig[pinID][RCUFUNC_KEY_TYPE] = PIN_UNASSIGN_NAME
        

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
    
    def post(self,funcID,pinID):
        # try:
        self.set_pin(pinID,funcID)
        print("self.set_pin(pinID,funcID)")
        rcuFunc = self.get_rcuFunc_byPinType(pinID)
        print("rcuFunc = self.get_rcuFunc_byPinType(pinID)")
        if None != rcuFunc: # rcuFunc wont exist in instance register if its not been inited
            rcuFunc.set_assigned_pins(self.get_funcs_pins(rcuFunc.functionID)) 
            print("rcuFunc.set_assigned_pins(self")
        else:
            print(f"{funcID} isnt in instnace register: {self.instance_register}")
        
        return {'message':f"Pin {pinID} set to {funcID}"}, 200
    # except Exception as e:
            
        return {'message':f"Failed to Save. Error:{e}"}, 500
        
    def get_rcuFunc_byPinType(self, pinType):
        for rcuFunc in self.instance_register:
            if rcuFunc.functionID in pinType:
                return rcuFunc
        return None
    

