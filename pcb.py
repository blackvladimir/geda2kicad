import parsepcb 

class Style:
    def __init__(self, string):
        fields = string.split(',')
        self.name = fields[0]
        self.thick = fields[1]  #TODO parse number
        self.diameter= fields[2]
        self.drill = fields[3]
        self.spacing = fields[4]

class SymbolLine:
    def __init__(self, item):
        self.x1 = item.attributes[0]
        self.y1 = item.attributes[1]
        self.x2 = item.attributes[2]
        self.y2 = item.attributes[3]
        self.thick = item.attributes[4]

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
        self.flags = item.attributes[8].split(',')

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
        self.flags = item.attributes[9].split(',')

class Symbol:
    def __init__(self, item):
        self.char = item.attributes[0]
        self.delta = item.attributes[1]
        self.lines = []
        for c in item.children:
            if c.name != 'SymbolLine':
                raise Exception('unknown item %s in Symbol' % c.name)
            self.lines.append(SymbolLine(c))

class Via:
    def __init__(self, item):
        a = item.attributes;
        self.x = a[0]
        self.y = a[1]
        self.diameter = a[2]
        self.spacing = a[3]
        self.mask = a[4]
        self.drill = a[5]
        if len(a) == 10: #burried
            self.burrFrom = a[6]
            self.burrTo = a[7]
            self.name = a[8]
            self.flags = a[9].split(',')
        else:
            self.name = a[6]
            self.flags = a[7].split(',')

class Element:
    def __init__(self, item):
        a = item.attributes
        self.flags = a[0].split(',')
        self.description = a[1]
        self.name = a[2]
        self.value = a[3]
        self.x = a[4]
        self.y = a[5]
        self.textx = a[6]
        self.texty = a[7]
        self.tdir = int(a[8])
        self.tscale = a[9]
        self.tflags = a[10].split(',')

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
                print(c.name)


class Pcb:
    def __init__(self, items):
        self.comments = []
        self.symbols = []
        self.attributes = {}
        self.vias = []
        self.elements = []
        for item in items:
            if item.name == "comment":
                self.comments.append(item.attributes[0])
            elif item.name == "FileVersion":
                self.version = item.attributes[0]
            elif item.name == "PCB":
                self.name = item.attributes[0]
                self.width = item.attributes[1]
                self.height = item.attributes[2]
            elif item.name == "Grid":
                self.gridStep = item.attributes[0]
                self.gridX = item.attributes[1]
                self.gridY = item.attributes[2]
                self.gridVisible = item.attributes[3]
            elif item.name == "PolyArea":
                self.polyArea = item.attributes[0]
            elif item.name == "Thermal":
                self.thermal = item.attributes[0]
            elif item.name == "DRC":
                self.minSpace = item.attributes[0]
                self.minOverlap = item.attributes[1]
                self.minWidth = item.attributes[2]
                self.minSilk = item.attributes[3]
                self.minDrill = item.attributes[4]
                self.minRing = item.attributes[5]
            elif item.name == "Flags":
                self.flags = item.attributes[0].split(',')
            elif item.name == "Groups":
                self.groups = []
                for group in item.attributes[0].split(':'):
                    self.groups.append(group.split(','))
            elif item.name == "Styles":
                self.styles = []
                for s in item.attributes[0].split(':'):
                    self.styles.append(Style(s))
            elif item.name == "Symbol":
                self.symbols.append(Symbol(item))
            elif item.name == "Attribute":
                self.attributes[item.attributes[0]] = item.attributes[1]
            elif item.name == "Via":
                self.vias.append(Via(item))
            elif item.name == "Element":
                self.elements.append(Element(item))
            else:
                print(item.name)


p = Pcb(parsepcb.load("lock.pcb"))
print(p.elements[3].attributes)
