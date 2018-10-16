import re
WHITESPACE = re.compile("[ \r\t\n]*")
NAME = re.compile("[^ \r\t\n)]+") 
STRING = re.compile('"([^"]*)"')
CHAR = re.compile("'(.)'")
NUMBER = re.compile('(-?[\d.]+)(mil|mm)?')
ITEMSSTART = re.compile('[ \r\t\n]*\(')

class Version:
    def parse(self, attributes, lines):
        self.version = int(attributes[0])
        self.fileversion = int(attributes[1])
    def save(self):
        return [' '.join(['v', str(self.version), str(self.fileversion)])]

class Componnent:
    def parse(self, attributes, lines):
        self.x = int(attributes[0])
        self.y = int(attributes[1])
        self.selectable = int(attributes[2])
        self.angle = int(attributes[3])
        self.mirror = int(attributes[4])
        self.basename = attributes[5]
    def save(self):
        return [' '.join([
            'C',
            str(self.x),
            str(self.y),
            str(self.selectable),
            str(self.angle),
            str(self.mirror),
            str(self.basename),
            ])]

class Text:
    def parse(self, attributes, lines):
        self.x = int(attributes[0])
        self.y = int(attributes[1])
        self.color = int(attributes[2])
        self.siz = int(attributes[3])
        self.visibility = int(attributes[4])
        self.show_name_value = int(attributes[5])
        self.angle = int(attributes[6])
        self.alignment = int(attributes[7])
        nl = int(attributes[8])
        self.text = lines.pop(0)
        for i in range(nl - 1):
            self.text += '\n' + lines.pop(0)
    def save(self):
        lines = self.text.split('\n')
        r =  [' '.join([
            'T',
            str(self.x),
            str(self.y),
            str(self.color),
            str(self.siz),
            str(self.visibility),
            str(self.show_name_value),
            str(self.angle),
            str(self.alignment),
            str(len(lines))
            ])]
        return r + lines

class Net:
    def parse(self, attributes, lines):
        self.x1 = int(attributes[0])
        self.y1 = int(attributes[1])
        self.x2 = int(attributes[2])
        self.y2 = int(attributes[3])
        self.color = int(attributes[4])
    def save(self):
        return [' '.join([
            'N',
            str(self.x1),
            str(self.y1),
            str(self.x2),
            str(self.y2),
            str(self.color),
            ])]

class Pin:
    def parse(self, attributes, lines):
        self.x1 = int(attributes[0])
        self.y1 = int(attributes[1])
        self.x2 = int(attributes[2])
        self.y2 = int(attributes[3])
        self.color = int(attributes[4])
        self.pintype = int(attributes[5])
        self.whichend = int(attributes[6])
    def save(self):
        return [' '.join([
            'P',
            str(self.x1),
            str(self.y1),
            str(self.x2),
            str(self.y2),
            str(self.color),
            str(self.pintype),
            str(self.whichend),
            ])]

class Box:
    def parse(self, attributes, lines):
        self.x = int(attributes[0])
        self.y = int(attributes[1])
        self.width = int(attributes[2])
        self.height = int(attributes[3])
        self.color = int(attributes[4])
        self.lwidth = int(attributes[5])
        self.capstyle = int(attributes[6])
        self.dashstyle = int(attributes[7])
        self.dashlength = int(attributes[8])
        self.dashspace = int(attributes[9])
        self.filltype = int(attributes[10])
        self.fillwidth = int(attributes[11])
        self.angle1 = int(attributes[12])
        self.pitch1 = int(attributes[13])
        self.angle2 = int(attributes[14])
        self.pitch2 = int(attributes[15])
    def save(self):
        return [' '.join([
            'B', 
            str(self.x),
            str(self.y),
            str(self.width),
            str(self.height),
            str(self.color),
            str(self.lwidth),
            str(self.capstyle),
            str(self.dashstyle),
            str(self.dashlength),
            str(self.dashspace),
            str(self.filltype),
            str(self.fillwidth),
            str(self.angle1),
            str(self.pitch1),
            str(self.angle2),
            str(self.pitch2),
            ])]


def loadItems(lines, end = None):
    items = []
    while lines:
        line = lines.pop(0)
        if not line:
            continue
        attributes = line[2:].split(' ')
        t = line[0]
        if t == 'v':
            cl = Version
        elif t == 'C':
            cl = Componnent
        elif t == 'T':
            cl = Text
        elif t == 'N':
            cl = Net
        elif t == 'P':
            cl = Pin
        elif t == 'B':
            cl = Box
        elif t == '{':
            items[-1].attributes = loadItems(lines, '}')
            continue
        elif t == '[':
            items[-1].embedded = loadItems(lines, ']')
            continue
        elif t == end:
            return items
        else:
            raise Exception('unexpected object ' + t)
        i = cl()
        i.parse(attributes, lines)
        items.append(i)
    return items

def saveItems(items):
    lines = []
    for i in items:
        lines += i.save()
        if hasattr(i, 'embedded'):
            lines += ['['] + saveItems(i.embedded) + [']']
        if hasattr(i, 'attributes'):
            lines += ['{'] + saveItems(i.attributes) + ['}']
    return lines

def load(path):
    with open(path) as f:
        lines = f.read().split('\n')
        return loadItems(lines)

def save(path, items):
    lines = saveItems(items)
    with open(path,'w') as f:
        f.write('\n'.join(lines))

itms = load('lock.sch')
save('export.sch', itms)
