import parsepcb 

class Style:
    def __init__(self, string):
        fields = string.split(',')
        self.name = fields[0]
        self.thick = parsepcb.parseValue(fields[1], 0)[0].distance()
        self.diameter= parsepcb.parseValue(fields[2], 0)[0].distance()
        self.drill = parsepcb.parseValue(fields[3], 0)[0].distance()
        self.spacing = parsepcb.parseValue(fields[4], 0)[0].distance()
    def __str__(self):
        return self.name + ',' + str(parsepcb.nm(self.thick)) + ',' + str(parsepcb.nm(self.diameter)) + ',' + str(parsepcb.nm(self.drill)) + ',' + str(parsepcb.nm(self.spacing))

class SymbolLine:
    def __init__(self, item):
        self.x1 = item.attributes[0].distance()
        self.y1 = item.attributes[1].distance()
        self.x2 = item.attributes[2].distance()
        self.y2 = item.attributes[3].distance()
        self.thick = item.attributes[4].distance()
    def itemize(self):
        return parsepcb.Item('SymbolLine', [parsepcb.nm(self.x1), parsepcb.nm(self.y1), parsepcb.nm(self.x2), parsepcb.nm(self.y2), parsepcb.nm(self.thick)], False, None)

class ElementArc:
    def __init__(self, item):
        self.x = item.attributes[0]
        self.y = item.attributes[1]
        self.width = item.attributes[2]
        self.height= item.attributes[3]
        self.startAngle = item.attributes[4]
        self.angle = item.attributes[5]
        self.thick = item.attributes[6]

class Pin:
    def __init__(self, item):
        self.x = item.attributes[0]
        self.y = item.attributes[1]
        self.dimater = item.attributes[2]
        self.spacing= item.attributes[3]
        self.mask = item.attributes[4]
        self.drill = item.attributes[5]
        self.name = item.attributes[6]
        self.number = item.attributes[7]
        self.flags = item.attributes[8].flags()

class Pad:
    def __init__(self, item):
        self.x1 = item.attributes[0]
        self.y1 = item.attributes[1]
        self.x2 = item.attributes[2]
        self.y2 = item.attributes[3]
        self.thick = item.attributes[4]
        self.spacing= item.attributes[5]
        self.mask = item.attributes[6]
        self.name = item.attributes[7]
        self.number = item.attributes[8]
        self.flags = item.attributes[9].flags()

class Symbol:
    def __init__(self, item):
        self.char = item.attributes[0].char()
        self.delta = item.attributes[1].distance()
        self.lines = []
        for c in item.children:
            if c.name != 'SymbolLine':
                raise Exception('unknown item %s in Symbol' % c.name)
            self.lines.append(SymbolLine(c))
    def itemize(self):
        return parsepcb.Item("Symbol", [parsepcb.CharValue(self.char), parsepcb.nm(self.delta)], False, [l.itemize() for l in self.lines])

class Via:
    def __init__(self, item):
        a = item.attributes;
        self.x = a[0].distance()
        self.y = a[1].distance()
        self.diameter = a[2].distance()
        self.spacing = a[3].distance()
        self.mask = a[4].distance()
        self.drill = a[5].distance()
        if len(a) == 10: #burried
            self.burrFrom = a[6]
            self.burrTo = a[7]
            self.name = a[8]
            self.flags = a[9].flags()
        else:
            self.name = a[6]
            self.flags = a[7].flags()

class Element:
    def __init__(self, item):
        a = item.attributes
        self.flags = a[0].flags()
        self.description = a[1]
        self.name = a[2]
        self.value = a[3]
        self.x = a[4].distance()
        self.y = a[5].distance()
        self.textx = a[6].distance()
        self.texty = a[7].distance()
        self.tdir = a[8].num()
        self.tscale = a[9].num()
        self.tflags = a[10].flags()

        self.attributes = {}
        self.lines = []

        for c in item.children:
            if c.name == "Attribute":
                self.attributes[c.attributes[0]] = c.attributes[1]
            elif c.name == "ElementLine":
                self.lines.append(SymbolLine(c))
            elif c.name == "ElementArc":
                self.lines.append(ElementArc(c))
            elif c.name == "Pin":
                self.lines.append(Pin(c))
            elif c.name == "Pad":
                self.lines.append(Pad(c))
            else:
                raise Exception("unknown item %s" % c.name)

class Line:
    def __init__(self, item):
        self.x1 = item.attributes[0].distance()
        self.y1 = item.attributes[1].distance()
        self.x2 = item.attributes[2].distance()
        self.y2 = item.attributes[3].distance()
        self.thick = item.attributes[4].distance()
        self.spacing = item.attributes[5].distance()
        self.flags = item.attributes[6].flags()

class Arc:
    def __init__(self, item):
        self.x = item.attributes[0].distance()
        self.y = item.attributes[1].distance()
        self.width = item.attributes[2].distance()
        self.height= item.attributes[3].distance()
        self.thick = item.attributes[4].distance()
        self.spacing = item.attributes[5].distance()
        self.startAngle = item.attributes[6].num()
        self.angle = item.attributes[7].num()
        self.flags = item.attributes[8].flags()

class Text:
    def __init__(self, item):
        self.x = item.attributes[0].distance()
        self.y = item.attributes[1].distance()
        self.dir = item.attributes[2].num()
        self.scale = item.attributes[3].num()
        self.string = item.attributes[4]
        self.flags = item.attributes[5].flags()

class Hole:
    def __init__(self, item):
        self.points = []
        for c in item.children:
            if c.name == '': #point
                self.points.append((c.attributes[0].distance(), c.attributes[1].distance()))

class Polygon:
    def __init__(self, item):
        self.flags = item.attributes[0].flags()
        self.points = []
        self.holes = []
        for c in item.children:
            if c.name == '': #point
                self.points.append((c.attributes[0].distance(), c.attributes[1].distance()))
            elif c.name == 'Hole':
                self.holes.append(Hole(c))
            else:
                raise Exception("unknown item %s" % c.name)

class Layer:
    def __init__(self, item):
        self.number = item.attributes[0].num()
        self.name = item.attributes[1]
        self.flags = item.attributes[1].flags()

        self.lines = []
        self.texts = []
        self.arcs = []
        self.polygons = []
    
        for c in item.children:
            if c.name == "Line":
                self.lines.append(Line(c))
            elif c.name == "Text":
                self.texts.append(Text(c))
            elif c.name == "Arc":
                self.arcs.append(Arc(c))
            elif c.name == "Polygon":
                self.polygons.append(Polygon(c))
            else:
                raise Exception("unknown item %s" % c.name)

class Connect:
    def __init__(self, item):
        self.part, self.pin = item.attributes[0].pin()

class Net:
    def __init__(self, item):
        self.name = item.attributes[0]
        self.style = item.attributes[1]

        self.connects = []
        for c in item.children:
            if c.name == "Connect":
                self.connects.append(Connect(c))
            else:
                raise Exception("unknown item %s" % c.name)

class Netlist:
    def __init__(self, item):
        self.nets = []
        for c in item.children:
            if c.name == "Net":
                self.nets.append(Net(c))
            else:
                raise Exception("unknown item %s" % c.name)

class Rat:
    def __init__(self, item):
        self.x1 = item.attributes[0].distance()
        self.y1 = item.attributes[1].distance()
        self.g1 = item.attributes[2]
        self.x2 = item.attributes[3].distance()
        self.y2 = item.attributes[4].distance()
        self.g2 = item.attributes[5]
        self.flags = item.attributes[6].flags()

class Pcb:
    def __init__(self, items):
        self.comments = []
        self.symbols = []
        self.attributes = {}
        self.vias = []
        self.elements = []
        self.layers = []
        self.rats = []
        for item in items:
            if item.name == "comment":
                self.comments.append(item.attributes[0])
            elif item.name == "FileVersion":
                self.version = item.attributes[0]
            elif item.name == "PCB":
                self.name = item.attributes[0]
                self.width = item.attributes[1].distance()
                self.height = item.attributes[2].distance()
            elif item.name == "Grid":
                self.gridStep = item.attributes[0].distance()
                self.gridX = item.attributes[1].distance()
                self.gridY = item.attributes[2].distance()
                self.gridVisible = item.attributes[3]
            elif item.name == "PolyArea":
                self.polyArea = item.attributes[0].num()
            elif item.name == "Thermal":
                self.thermal = item.attributes[0].num()
            elif item.name == "DRC":
                self.minSpace = item.attributes[0].distance()
                self.minOverlap = item.attributes[1].distance()
                self.minWidth = item.attributes[2].distance()
                self.minSilk = item.attributes[3].distance()
                self.minDrill = item.attributes[4].distance()
                self.minRing = item.attributes[5].distance()
            elif item.name == "Flags":
                self.flags = item.attributes[0].flags()
            elif item.name == "Groups":
                self.groups = []
                for group in item.attributes[0].array():
                    self.groups.append(group.split(','))
            elif item.name == "Styles":
                self.styles = []
                for s in item.attributes[0].array():
                    self.styles.append(Style(s))
            elif item.name == "Symbol":
                self.symbols.append(Symbol(item))
            elif item.name == "Attribute":
                self.attributes[item.attributes[0]] = item.attributes[1]
            elif item.name == "Via":
                self.vias.append(Via(item))
            elif item.name == "Element":
                self.elements.append(Element(item))
            elif item.name == "Layer":
                self.layers.append(Layer(item))
            elif item.name == "NetList":
                self.netlist = Netlist(item)
            elif item.name == "Rat":
                self.rats.append(Rat(item))
            else:
                raise Exception("unknown item %s" % item.name)

    def itemize(self):
        items = []
        for c in self.comments:
            items.append(parsepcb.Item("comment", [c], False, None))
        items.append(parsepcb.Item("FileVersion", [self.version], False, None))
        items.append(parsepcb.Item("PCB", [self.name, parsepcb.nm(self.width), parsepcb.nm(self.height)], False, None))
        items.append(parsepcb.Item("Grid", [parsepcb.nm(self.gridStep), parsepcb.nm(self.gridX),parsepcb.nm(self.gridY), self.gridVisible], False, None))
        items.append(parsepcb.Item("PolyArea", [parsepcb.NumericValue(self.polyArea, None)], False, None))
        items.append(parsepcb.Item("Thermal", [parsepcb.NumericValue(self.thermal, None)], False, None))
        items.append(parsepcb.Item("DRC", [parsepcb.nm(self.minSpace), parsepcb.nm(self.minOverlap),parsepcb.nm(self.minWidth),parsepcb.nm(self.minSilk), parsepcb.nm(self.minDrill), parsepcb.nm(self.minRing)], False, None))
        items.append(parsepcb.Item("Flags", [parsepcb.StringValue(",".join(self.flags))], True, None))
        items.append(parsepcb.Item("Groups", [parsepcb.StringValue(':'.join([','.join(g) for g in self.groups]))], True, None))
        items.append(parsepcb.Item("Styles", [parsepcb.StringValue(':'.join([str(s) for s in self.styles]))], False, None))
        for s in self.symbols:
            items.append(s.itemize())
        return items


p = Pcb(parsepcb.load("lock.pcb"))
parsepcb.save("lockexp.pcb", p.itemize())
