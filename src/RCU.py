import array

class RCU:
    configPath = ""

    def import_config(json):


    def export_config()



class Page:
    placeHolderFix = "%"

    def __init__(self,template="H:\\SteeringWheelButtons\\src\\web\\templates\\page.html",**kwargs):
        self.placeholders = kwargs
        self.template = template

    def read_template():
        with open(self.template, "r") as templateFile:
            content = templateFile.read()  # Reads the entire file as a string
        
        return content

    def populate_placeholders():
        content = read_template()

        for placeholder in placegolders.keys():
            content.replace(f"{placeHolderFix}{placeholder}{placeHolderFix}",placeholders.get(placeholder))

        return content


class ShiftLights(Page):
    shiftLights = array.array("O",[])
    interfaceTemplate = "H:\\SteeringWheelButtons\\src\\web\\templates\\shiftLights.html"

    def __init__(self,config):
        self.limitPattern = config['limitPattern']
        self.limitColor = config['limitColor']
        self.pin = config['pin']

        for shiftLightConfig in config['shiftLights']:
            self.shiftLights.append(ShiftLight(shiftLightConfig))
    
        super().__init__(
            template=interfaceTemplate,
            Content = ''.join(map(lambda shiftLight: shiftLight.populate_placeholders(), shiftLights))
        )



class ShiftLight(Page):
    interfaceTemplate = "H:\\SteeringWheelButtons\\src\\web\\templates\\shiftLight.html"

    def __init__(self,config):
        self.id = config['id']
        self.color = Color(config['color'])
        self.active = False
        super().__init__(
            template=self.interfaceTemplate,
            Color = self.color.toHTMLString(),
            ID = id
        )




class WebInterface(Page):
    interfaceTemplate = "H:\\SteeringWheelButtons\\src\\web\\templates\\webInterface.html"

    def __init__(self, config, **kwargs):
        self.shiftLights = ShiftLights(config(ShiftLights))
    



class Color:
    def __init__(self,config):
        self.red = config['red']
        self.green = config['green']
        self.blue = config['blue']

    def toHTMLString():
        return f"rgb({red}, {green}, {blue})"