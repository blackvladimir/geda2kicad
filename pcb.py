import parsepcb 

class Style:
    def __init__(self, string):
        fields = string.split(',')
        self.name = fields[0]
        self.width = fields[1]  #TODO parse number
        self.diameter= fields[2]
        self.drill = fields[3]
        self.spacing = fields[4]

class SymbolLine:
    def __init__(self, item):
        self.x1 = item.attributes[0]
        self.y1 = item.attributes[1]
        self.x2 = item.attributes[2]
        self.y2 = item.attributes[3]
        self.width = item.attributes[4]

class Symbol:
    def __init__(self, item):
        self.char = item.attributes[0]
        self.delta = item.attributes[1]
        self.lines = []
        for c in item.children:
            if c.name != 'SymbolLine':
                raise Exception('unknown item %s in Symbol' % c.name)
            self.lines.append(SymbolLine(c))


class Pcb:
    def __init__(self, items):
        self.comments = []
        self.symbols = []
        self.attributes = {}
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
            else:
                print(item.name)


p = Pcb(parsepcb.load("lock.pcb"))
print(p.attributes)
