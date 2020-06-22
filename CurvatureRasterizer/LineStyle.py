import math
import mapnik
from CurvatureRasterizer.RainbowVis import Rainbow

class CurvatureLinesStyle(object):
    zoom = 0

    def __init__(self, zoom):
        self.zoom = zoom

        self.c1000_rainbow = Rainbow()
        self.c1000_rainbow.setSpectrum('yellow', 'red', 'magenta');
        self.c1000_rainbow.setNumberRange(0, 100);

    def get_style(self):
        s = mapnik.Style() # style object to hold rules
        for p in range(0, 100):
            self.add_style_level(s, p)
        return s

    def add_style_level(self, s, percent):
        color = "#{}".format(self.c1000_rainbow.colourAt(percent));
        width_multiplier = self.get_width_multiplier(self.zoom)

        print("")
        print(percent)
        print(self.filter_condition(False, percent))
        print(self.filter_condition(True, percent))
        print(color)

        # unpaved
        r = mapnik.Rule()
        r.filter = mapnik.Filter(self.filter_condition(False, percent))
        ls = mapnik.LineSymbolizer()
        ls.stroke = mapnik.Color(color)
        ls.stroke_width = 0.5 * width_multiplier
        r.symbols.append(ls)
        s.rules.append(r)

        #paved
        r = mapnik.Rule()
        r.filter = mapnik.Filter(self.filter_condition(True, percent))
        ls = mapnik.LineSymbolizer()
        ls.stroke = mapnik.Color(color)
        ls.stroke_width = 1 * width_multiplier
        r.symbols.append(ls)
        s.rules.append(r)

    def filter_condition(self, paved, percent):
        if not percent:
            threshold = self.curvature_threshold(1)
            curvature_condition = "[curvature] < {}".format(threshold)
        else:
            threshold = self.curvature_threshold(percent)
            curvature_condition = "[curvature] >= {}".format(threshold)
        if paved:
            return "[paved] = true and {}".format(curvature_condition)
        else:
            return "[paved] = false and {}".format(curvature_condition)

    def get_width_multiplier(self, zoom):
        # Change our width multiplier when zoomed way out to avoid crowding.
        # zoom 15 == 4.7
        # zoom 14 == 9.5
        # zoom 13 == 19.1
        if zoom >= 13:
          # At high zooms, basemap road rendering makes the line-width less distinct.
          return 1.5
        # zoom 12 == 38.2
        # zoom 11 == 76.4
        # zoom 10 == 152.8
        # zoom 9 == 305.7
        # Zoom 8 == 611.49
        # Zoom 7 == 1222.9
        if zoom >= 7:
          return 0.75
        # Zoom 6 == 2445.9
        if zoom == 6:
          return 0.5
        # Zoom 5 == 4891.9
        if zoom == 5:
          return 0.25
        # Zoom 4 == 9783.9
        if zoom == 4:
          return 0.13

        return 0.1

    def curvature_threshold(self, color_pct):
        color_pct = color_pct/100
        # We are coloring a curvature range from 1000 to 20,000 on a logarithmic
        # scale, to give a better differentiation between lower-curvature ways.
        # 1,000 is the min differentiated and 20,000 is max differentiated.
        #
        # Going the other way: y = 1-1/(10^(x*2))
        #    curvature_pct = Math.min((curvature - 1000) / (20000 - 1000), 1)
        #    color_pct = 1 - 1/Math.pow(10, curvature_pct * 2)
        #
        # We're doing the inverse to find the curvature threshold for each color
        # percentage value.
        curvature_pct = math.log10(1 / (0 - (color_pct - 1))) / 2
        return 1000 + math.ceil(curvature_pct * 19000)
