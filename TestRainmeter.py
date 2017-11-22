import unittest
import re
from Rainmeter import Skin, Component, Block, Meter, ImageMeter, StringMeter, Color, TimeMeasure

class TestRainmeter(unittest.TestCase):
    def test_BlackSquare(self):
        skin = Skin("BlackSquare", Update=1000, AccurateText=1)
        component = Component("BlackSquare")
        skin.add_component(component)
        m = ImageMeter("BlackSquare", 
            Meter="Image", 
            SolidColor=Color.RED(),
            X=0,
            Y=0,
            W=100,
            H=100)
        component.add_block(m, index=0)
        

        print(skin.ini())
    def test_Color(self):

        skin = Skin("Gradient", Update=1000, AccurateText=1)
        component = Component("Gradient")
        skin.add_component(component)

        red = Color.RED()
        yellow = Color(255,255,0)
        green = Color(0,255,0)
        step = 10
        width = 5
        height = 2
        i = 0
        for color in Color.shift(red, yellow, step):
            component.add_block(
                ImageMeter("Square",
                    SolidColor=color,
                    X=width*i,
                    Y=0,
                    W=width,
                    H=height
                ), index=i)
            i += 1
        for color in Color.shift(yellow, green, step):
            component.add_block(
                ImageMeter("Square",
                    SolidColor=color,
                    X=width*i,
                    Y=0,
                    W=width,
                    H=height
                ), index=i)
            i += 1
        comp_x = 0
        comp_y = 0
        for k in range(20):
            new_comp = component.copy().translate(y=comp_y+(k*(height+2)))
            skin.add_component(new_comp)

        with open("Skins\Test\Gradient.ini", 'w') as f:
            f.write(skin.ini())

    def test_Clock(self):
        skin = Skin("Clock", Update=1000, AccurateText=1)
        component = Component("Clock")

        measure = TimeMeasure("Clock", format="%H:%M")
        meter = StringMeter("ClockDisplay")
        meter.add_measure(measure)
        component.add_block(meter)
        component.add_block(measure)
        skin.add_component(component)

        with open("Skins\Test\Clock.ini", 'w') as f:
            f.write(skin.ini())

    def test_regex(self):
        measure_pattern = re.compile("(MeasureName)(\d*)")
        self.assertTrue(measure_pattern.match("MeasureName1"))
        self.assertTrue(measure_pattern.match("MeasureName"))
        self.assertTrue(measure_pattern.match("MeasureName10"))
if __name__ == "__main__":
    unittest.main()