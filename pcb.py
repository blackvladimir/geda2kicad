from parsepcb import Item, parseValue, nm, NumericValue, CharValue, StringValue, load, save, flags

class Style:
    def __init__(self, string):
        fields = string.split(',')
        self.name = fields[0]
        self.thick = parseValue(fields[1], 0)[0].distance() #helper function parse distance?
        self.diameter= parseValue(fields[2], 0)[0].distance()
        self.drill = parseValue(fields[3], 0)[0].distance()
        self.spacing = parseValue(fields[4], 0)[0].distance()
    def __str__(self):
        return self.name + ',' + str(nm(self.thick)) + ',' + str(nm(self.diameter)) + ',' + str(nm(self.drill)) + ',' + str(nm(self.spacing))

class SymbolLine:
    def __init__(self, item, element):
        self.x1 = item.attributes[0].distance()
        self.y1 = item.attributes[1].distance()
        self.x2 = item.attributes[2].distance()
        self.y2 = item.attributes[3].distance()
        self.thick = item.attributes[4].distance()
        self.element = element
    def itemize(self):
        return Item('ElementLine' if self.element else 'SymbolLine', [nm(self.x1), nm(self.y1), nm(self.x2), nm(self.y2), nm(self.thick)])

class ElementArc:
    def __init__(self, item):
        self.x = item.attributes[0].distance()
        self.y = item.attributes[1].distance()
        self.width = item.attributes[2].distance()
        self.height= item.attributes[3].distance()
        self.startAngle = item.attributes[4].num()
        self.angle = item.attributes[5].num()
        self.thick = item.attributes[6].distance()
    def itemize(self):
        return Item('ElementArc', [nm(self.x), nm(self.y), nm(self.width), nm(self.height), NumericValue(self.startAngle), NumericValue(self.angle), nm(self.thick)])

class Pin:
    def __init__(self, item):
        self.x = item.attributes[0].distance()
        self.y = item.attributes[1].distance()
        self.dimater = item.attributes[2].distance()
        self.spacing= item.attributes[3].distance()
        self.mask = item.attributes[4].distance()
        self.drill = item.attributes[5].distance()
        self.name = item.attributes[6].str()
        self.number = item.attributes[7].str()
        self.flags = item.attributes[8].flags()
    def itemize(self):
        return Item('Pin', [nm(self.x), nm(self.y), nm(self.dimater), nm(self.spacing), nm(self.mask), nm(self.drill), StringValue(self.name), StringValue(self.number), flags(self.flags)])

class Pad:
    def __init__(self, item):
        self.x1 = item.attributes[0].distance()
        self.y1 = item.attributes[1].distance()
        self.x2 = item.attributes[2].distance()
        self.y2 = item.attributes[3].distance()
        self.thick = item.attributes[4].distance()
        self.spacing= item.attributes[5].distance()
        self.mask = item.attributes[6].distance()
        self.name = item.attributes[7].str()
        self.number = item.attributes[8].str()
        self.flags = item.attributes[9].flags()
    def itemize(self):
        return Item('Pad', [nm(self.x1), nm(self.y1), nm(self.x2), nm(self.y2), nm(self.thick), nm(self.spacing), nm(self.mask), StringValue(self.name), StringValue(self.number), flags(self.flags)])

class Symbol:
    def __init__(self, item):
        self.char = item.attributes[0].char()
        self.delta = item.attributes[1].distance()
        self.lines = []
        for c in item.children:
            if c.name != 'SymbolLine':
                raise Exception('unknown item %s in Symbol' % c.name)
            self.lines.append(SymbolLine(c, False))
    def itemize(self):
        return Item("Symbol", [CharValue(self.char), nm(self.delta)], False, [l.itemize() for l in self.lines])

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
            self.burrFrom = None
            self.burrTo = None
            self.name = a[6]
            self.flags = a[7].flags()
    def itemize(self):
        return Item('Via', [nm(self.x), nm(self.y), nm(self.diameter), nm(self.spacing), nm(self.mask), nm(self.drill)] + ([self.burrFrom, self.burrTo] if self.burrTo else [])  + [self.name, flags(self.flags)])

class Element:
    def __init__(self, item):
        a = item.attributes
        self.flags = a[0].flags()
        self.description = a[1].str()
        self.name = a[2].str()
        self.value = a[3].str()
        self.x = a[4].distance()
        self.y = a[5].distance()
        self.textx = a[6].distance()
        self.texty = a[7].distance()
        self.tdir = a[8].num()
        self.tscale = a[9].num()
        self.tflags = a[10].flags()

        self.attributes = {}
        self.lines = []
        self.arcs = []
        self.pins = []
        self.pads = []

        for c in item.children:
            if c.name == "Attribute":
                self.attributes[c.attributes[0].str()] = c.attributes[1].str()
            elif c.name == "ElementLine":
                self.lines.append(SymbolLine(c, True))
            elif c.name == "ElementArc":
                self.lines.append(ElementArc(c))
            elif c.name == "Pin":
                self.lines.append(Pin(c))
            elif c.name == "Pad":
                self.lines.append(Pad(c))
            else:
                raise Exception("unknown item %s" % c.name)
    def itemize(self):
        items = []
        for k,v in self.attributes.items():
            items.append(Item('Attribute', [StringValue(k), StringValue(v)], True))   #TODO functions for attributes?
        return Item('Element', [flags(self.flags), StringValue(self.description), StringValue(self.name), StringValue(self.value), nm(self.x), nm(self.y), nm(self.textx), nm(self.texty), 
            NumericValue(self.tdir), NumericValue(self.tscale), flags(self.flags)], False, items + [l.itemize() for l in (self.lines + self.arcs + self.pins + self.pads)])

class Line:
    def __init__(self, item):
        self.x1 = item.attributes[0].distance()
        self.y1 = item.attributes[1].distance()
        self.x2 = item.attributes[2].distance()
        self.y2 = item.attributes[3].distance()
        self.thick = item.attributes[4].distance()
        self.spacing = item.attributes[5].distance()
        self.flags = item.attributes[6].flags()
    def itemize(self):
        return Item('Line', [nm(self.x1), nm(self.y1), nm(self.x2), nm(self.y2), nm(self.thick), nm(self.spacing), flags(self.flags)])

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
    def itemize(self):
        return Item('Arc', [nm(self.x), nm(self.y), nm(self.width), nm(self.height), nm(self.thick), nm(self.spacing), NumericValue(self.startAngle), NumericValue(self.angle), flags(self.flags)])

class Text:
    def __init__(self, item):
        self.x = item.attributes[0].distance()
        self.y = item.attributes[1].distance()
        self.dir = item.attributes[2].num()
        self.scale = item.attributes[3].num()
        self.string = item.attributes[4].str()
        self.flags = item.attributes[5].flags()
    def itemize(self):
        return Item('Text', [nm(self.x), nm(self.y), NumericValue(self.dir), NumericValue(self.scale), StringValue(self.string), flags(self.flags)])

class Hole:
    def __init__(self, item):
        self.points = []
        for c in item.children:
            if c.name == '': #point
                self.points.append((c.attributes[0].distance(), c.attributes[1].distance()))
    def itemize(self):
        return Item('Hole', None, False, [Item('', [nm(p[0]), nm(p[1])]) for p in self.points])  #TODO refactor point export?


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
    def itemize(self):
        return Item('Polygon', [flags(self.flags)], True, [Item('', [nm(p[0]), nm(p[1])]) for p in self.points] + [h.itemize() for h in self.holes]) #TODO holes

class Layer:
    def __init__(self, item):
        self.number = item.attributes[0].num()
        self.name = item.attributes[1].str()
        self.flags = item.attributes[2].flags()

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
    def itemize(self):
        return Item('Layer', [NumericValue(self.number), StringValue(self.name), flags(self.flags)], True, [g.itemize() for g in (self.lines + self.texts + self.arcs + self.polygons)])

class Connect:
    def __init__(self, item):
        self.part, self.pin = item.attributes[0].pin()
    def itemize(self):
        return Item('Connect', [StringValue(self.part + '-' + self.pin)], True)

class Net:
    def __init__(self, item):
        self.name = item.attributes[0].str()
        self.style = item.attributes[1].str()

        self.connects = []
        for c in item.children:
            if c.name == "Connect":
                self.connects.append(Connect(c))
            else:
                raise Exception("unknown item %s" % c.name)
    def itemize(self):
        return Item('Net', [StringValue(self.name), StringValue(self.style)], True, [c.itemize() for c in self.connects])

class Netlist:
    def __init__(self, item):
        self.nets = []
        for c in item.children:
            if c.name == "Net":
                self.nets.append(Net(c))
            else:
                raise Exception("unknown item %s" % c.name)
    def itemize(self):
        return Item('NetList', [], True, [net.itemize() for net in self.nets])

class Rat:
    def __init__(self, item):
        self.x1 = item.attributes[0].distance()
        self.y1 = item.attributes[1].distance()
        self.g1 = item.attributes[2].num()
        self.x2 = item.attributes[3].distance()
        self.y2 = item.attributes[4].distance()
        self.g2 = item.attributes[5].num()
        self.flags = item.attributes[6].flags()
    def itemize(self):
        return Item('Rat', [nm(self.x1), nm(self.y1), NumericValue(self.g1), nm(self.x2), nm(self.y2), NumericValue(self.g2), flags(self.flags)])

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
                self.attributes[item.attributes[0].str()] = item.attributes[1].str()
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
            items.append(Item("comment", [c]))
        items.append(Item("FileVersion", [self.version]))
        items.append(Item("PCB", [self.name, nm(self.width), nm(self.height)]))
        items.append(Item("Grid", [nm(self.gridStep), nm(self.gridX),nm(self.gridY), self.gridVisible]))
        items.append(Item("PolyArea", [NumericValue(self.polyArea)])) #helper function number
        items.append(Item("Thermal", [NumericValue(self.thermal)]))  
        items.append(Item("DRC", [nm(self.minSpace), nm(self.minOverlap),nm(self.minWidth),nm(self.minSilk), nm(self.minDrill), nm(self.minRing)]))
        items.append(Item("Flags", [flags(self.flags)], True)) 
        items.append(Item("Groups", [StringValue(':'.join([','.join(g) for g in self.groups]))], True))   #TODO helper function array?
        items.append(Item("Styles", [StringValue(':'.join([str(s) for s in self.styles]))], False))
        for s in self.symbols:
            items.append(s.itemize())
        for k,v in self.attributes.items():
            items.append(Item('Attribute', [StringValue(k), StringValue(v)], True))
        for v in self.vias:
            items.append(v.itemize())
        for e in self.elements:
            items.append(e.itemize())
        for r in self.rats:
            items.append(r.itemize())
        for l in self.layers:
            items.append(l.itemize())
        items.append(self.netlist.itemize())
        return items

