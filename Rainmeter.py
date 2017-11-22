import collections
import re

class Skin():
    def __init__(self, name, **args):
        self.components = []
        self.args = args

    def add_component(self, component):
        assert isinstance(component, Component)
        self.components.append(component)

    def ini(self):
        text = ""
        text += self.rm_header()
        text += self.lua_variables()
        text += self.code()
        return text

    def rm_header(self):
        header = "[Rainmeter]\n"
        for arg in self.args:
            header+=arg+"="+str(self.args[arg])+"\n"
        header+="\n"
        return header

    def lua_variables(self):
        first = True
        variables = ""
        for component in self.components:
            for var in component.variables:
                if first:
                    variables = "[Variables]\n"
                    first = False
                variables += var+"="+str(component.variables[var])+"\n"
        variables+="\n"
        return variables

    def code(self):
        code = ""
        for component in self.components:
            code += component.code()
            code+="\n"
        return code

class Component():
    class MeterIndexAlreadyExists(Exception):
        pass
    class MeterAlreadyExists(Exception):
        pass 
    id = 0

    def __init__(self, name,x=0,y=0):
        self.meters = dict()
        self.measures = []
        self.variables = dict()
        self.id = Component.id
        self.name = name
        self.block_id = 0
        self.x = x
        self.y = y
        Component.id+=1

    def add_block(self, block, index=None):
        assert isinstance(block, Block)
        if isinstance(block, Meter):
            if index is None:
                if len(self.meters) > 0:
                    index = max(self.meters.keys())+1
                else:
                    index = 0
            if index in self.meters:
                raise Component.MeterIndexAlreadyExists("Index "+str(index)+": "+str(self.meters[i].name))
            if block in [blocks for _ , blocks in self.meters.items()]:
                raise Component.MeterAlreadyExists("Block "+str(block.unique_name()))
            self.meters[index] = block
            block.assign_component(self)
        if isinstance(block, Measure):
            self.measures.append(block)    
            block.assign_component(self)

    def add_variable(self, name, val):
        name = "Component"+str(self.id)+"."+self.name+"."+name
        self.variables[name] = val

    def code(self):
        code = ""
        for block in self.measures:
            code += block.code()
        for _ , block in self.meters.items():
            code += block.code()
        return code 

    def unique_name(self):
        return "Component"+str(self.id)+"_"+self.name

    def copy(self):
        copy = type(self)(self.name, self.x, self.y)
        for meter in self.meters:
            copy.add_block(self.meters[meter].copy())
        for measure in self.measures:
            copy.add_block(measure.copy())
        return copy

    def translate(self, x=0, y=0):
        self.x += x
        self.y += y
        for meter in self.meters:
            self.meters[meter].refresh()
        
        return self

class Block():
    all_params = ["Meter"]

    class InvalidParameter(Exception):
        pass
    class RequiredParameterMissing(Exception):
        pass

    def __init__(self, name, **args):
        self.name = name
        self.args = args

    def copy(self):
        return type(self)(self.name, **self.args)

    def update(self, **args):
        for a in args:
            self.args[a] = args[a]
        return self

    def assign_component(self, component):
        self.component = component
        self.id = component.block_id

        

        component.block_id += 1

    def unique_name(self):
        return self.component.unique_name()+"_"+type(self).block_identifier+str(self.id)+"_"+self.name

    def code(self):
        code = "["+self.unique_name()+ "]" + "\n"
        for arg in self.args:
            code += arg+"="+str(self.args[arg])+"\n"
        code+="\n"
        return code

class Meter(Block):
    accepts_measures = True
    measure_ids = []

    def __init__(self, name, x=None, y=None, **args):     
        
        #Defining Location
        assert not (x is not None and 'X' in args)
        assert not (y is not None and 'Y' in args)
        
        if x is None:
            if 'X' in args:
                self.x = args['X']
            else:
                self.x = 0
                args['X'] = 0
        else:
            self.x = x
            args['X'] = x

        if y is None:
            if 'Y' in args:
                self.y = args['Y']
            else:
                self.y = 0
                args['Y'] = 0
        else:
            self.y = y
            args['Y'] = y

        #Handle Measures during declaration
        measure_pattern = re.compile("(MeasureName)(\d*)")
        for arg in args:
            if measure_pattern.match(arg):
                pass

        super().__init__(name, **args)

    def refresh(self):
        if self.component is not None:
            self.args['X'] = self.component.x + self.x
            self.args['Y'] = self.component.y + self.y

    def add_measure(self, measure):
        if type(self).accepts_measures:
            pass


        else:
            assert False #TODO: Replace with Exception

    def assign_component(self, component):
        if not 'X' in self.args:
            self.args['X'] = component.x
        else: 
            self.args['X'] += component.x

        if not 'Y' in self.args:
            self.args['Y'] = component.y
        else: 
            self.args['Y'] += component.y
        super().assign_component(component)

class StringMeter(Meter):
    all_params = ["SolidColor","Meter", "Text", "FontFace", "FontSize", "FontColor", "FontWeight", "StringAlign", "StringStyle", "StringCase"]
    block_identifier = "StringMeter"

    def __init__(self, name, **args):
        args["Meter"] = "String"
        super(StringMeter, self).__init__(name, **args)

class ImageMeter(Meter):
    all_params = ["Meter", "SolidColor", "X", "Y", "W", "H"]
    block_identifier = "ImageMeter"

    def __init__(self, name, **args):
        args["Meter"] = "Image"
        super(ImageMeter, self).__init__(name, **args)

class Measure(Block):
    block_identifier = "Measure"

class TimeMeasure(Measure):
    block_identifier = "TimeMeasure"

    def __init__(self, name, **args):
        args["Measure"] = "Time"
        super().__init__(name, **args)

class Color():

    def __init__(self, r, g, b):
        assert r >= 0 and g >= 0 and b >= 0
        assert r <= 255 and g <= 255 and b <= 255
        self.red = r
        self.green = g
        self.blue = b 

    def __str__(self):
        return str(self.red)+", "+str(self.green)+", "+str(self.blue)

    def RED():
        return Color(255,0,0)
    def BLUE():
        return Color(0, 0, 255)

    def shift(start, end, step):
        assert isinstance(start, Color)
        assert isinstance(end, Color)

        rdiff = -1*(start.red - end.red)
        gdiff = -1*(start.green - end.green)
        bdiff = -1*(start.blue - end.blue)

        rstep = rdiff/step
        gstep = gdiff/step
        bstep = bdiff/step

        colors = [start]
        for i in range(step):
            start = start + (rstep, gstep, bstep)
            colors.append(start)
        return colors

    def __add__(self, other):
        if isinstance(other, Color):
            r = self.red + other.red 
            g = self.green + other.green 
            b = self.blue + other.blue
        if isinstance(other, collections.Sequence):
            r = self.red + other[0]
            g = self.green + other[1] 
            b = self.blue + other[2]

        color = Color.__constrain(r,g,b)
        return Color(*color)

    def __sub__(self, other):
        if isinstance(other, Color):
            r = self.red - other.red 
            g = self.green - other.green 
            b = self.blue - other.blue
        if isinstance(other, collections.Sequence):
            r = self.red - other[0]
            g = self.green - other[1] 
            b = self.blue - other[2]

        color = Color.__constrain(r,g,b)
        return Color(*color)
        

    def __constrain(r, g, b):
        r = r if (r <= 255) else 255
        g = g if (g <= 255) else 255
        b = b if (b <= 255) else 255

        r = r if (r >= 0) else 0
        g = g if (g >= 0) else 0
        b = b if (b >= 0) else 0

        return (r,g,b)

