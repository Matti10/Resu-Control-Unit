
import array
import ujson



def import_config(configPath = "src\\data\\config.json"):
    with open(configPath, "r") as file:
        return ujson.load(file)  # Parse JSON file into a dictionary


def export_config(self):
    with open(self.configPath, "w") as file:
        ujson.dump(self.config, file)




class RCU_Function:
    placeHolderFix = "%" # prefix/sufix for placeholder values

    def __init__(
        self,
        template="H:\\SteeringWheelButtons\\src\\web\\templates\\page.html",
        children=None,
        **kwargs
    ):

        if children is None:
            self.children = []
        else:
            self.children = children

        self.placeholders = kwargs
        self.importInterfaceTemplate(template)

    def importInterfaceTemplate(self):
        with open(self.template, "r") as templateFile:
            return templateFile.read()        


    def populate_placeholders(self, interface):       
        for placeholder in self.placeholders.keys():
            return interface.replace(f"{self.placeHolderFix}{placeholder}{self.placeHolderFix}",self.placeholders.get(placeholder))
        
    def build_interface(self):
        for child in self.children:
            child.build_interface()

        
    
    def add_child(self,child):           
        self.children.append(child)

    def add_placeholder(self,**kwargs):
        self.placeholders.update(kwargs)


class ShiftLights(RCU_Function):
    interfaceTemplate = "H:\\SteeringWheelButtons\\src\\web\\templates\\shiftLights.html"
    shiftLights = []
    def __init__(self,config):
        self.config = config
        super().__init__(template=self.interfaceTemplate)

        # super().__init__(
        #     template=self.interfaceTemplate,
        #     Content = ''.join(map(lambda shiftLight: shiftLight.populate_placeholders(), self.shiftLights))
        # )
        # for shiftLightConfig in config['ShiftLights']:
        #     self.shiftLights.append(ShiftLight(shiftLightConfig))
    

class ShiftLight(RCU_Function):
    interfaceTemplate = "H:\\SteeringWheelButtons\\src\\web\\templates\\shiftLight.html"

    def __init__(self,config):
        self.config = config
        self.color = Color(config['color'])
        self.active = False
        super().__init__(
            template=self.interfaceTemplate,
            Color = self.color.toHTMLString(),
            ID = id
        )


class WebInterface(RCU_Function):
    interfaceTemplate = "H:\\SteeringWheelButtons\\src\\web\\templates\\webInterface.html"


    def __init__(self):
        self.html = super().__init__(template=self.interfaceTemplate)

    def add_rcu_function(self, rcu_function):
        self.pages.append(rcu_function)

    def build_interface(self):
        for child in self.children:
            print("placeholder")



class Color:
    def __init__(self,config):
        self.red = config['red']
        self.green = config['green']
        self.blue = config['blue']

    def toHTMLString(self):
        return f"rgb({self.red}, {self.green}, {self.blue})"