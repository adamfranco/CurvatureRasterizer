import mapnik

class CurvatureLinesStyle(object):

    def get_style(self):
        s = mapnik.Style() # style object to hold rules

        r = mapnik.Rule()
        ls = mapnik.LineSymbolizer()
        ls.stroke = mapnik.Color('yellow')
        ls.stroke_width = 0.5
        r.symbols.append(ls)
        s.rules.append(r)

        r = mapnik.Rule()
        ls = mapnik.LineSymbolizer()
        ls.stroke_width = 1.0
        ls.stroke = mapnik.Color('yellow')
        r.symbols.append(ls)
        r.filter = mapnik.Filter("[paved] = true")
        s.rules.append(r)


        r = mapnik.Rule()
        ls = mapnik.LineSymbolizer()
        ls.stroke = mapnik.Color('orange')
        ls.stroke_width = 0.5
        r.symbols.append(ls)
        r.filter = mapnik.Filter("[paved] = false and [curvature] >= 2000")
        s.rules.append(r)

        r = mapnik.Rule()
        ls = mapnik.LineSymbolizer()
        ls.stroke = mapnik.Color('orange')
        ls.stroke_width = 1.0
        r.symbols.append(ls)
        r.filter = mapnik.Filter("[paved] = true and [curvature] >= 2000")
        s.rules.append(r)


        r = mapnik.Rule()
        ls = mapnik.LineSymbolizer()
        ls.stroke = mapnik.Color('red')
        ls.stroke_width = 0.5
        r.symbols.append(ls)
        r.filter = mapnik.Filter("[paved] = false and [curvature] >= 4000")
        s.rules.append(r)

        r = mapnik.Rule()
        ls = mapnik.LineSymbolizer()
        ls.stroke = mapnik.Color('red')
        ls.stroke_width = 1.0
        r.symbols.append(ls)
        r.filter = mapnik.Filter("[paved] = true and [curvature] >= 4000")
        s.rules.append(r)


        r = mapnik.Rule()
        ls = mapnik.LineSymbolizer()
        ls.stroke = mapnik.Color('magenta')
        ls.stroke_width = 0.5
        r.symbols.append(ls)
        r.filter = mapnik.Filter("[paved] = false and [curvature] >= 8000")
        s.rules.append(r)

        r = mapnik.Rule()
        ls = mapnik.LineSymbolizer()
        ls.stroke = mapnik.Color('red')
        ls.stroke_width = 1.0
        r.symbols.append(ls)
        r.filter = mapnik.Filter("[magenta] = true and [curvature] >= 8000")
        s.rules.append(r)

        return s
