import re
WHITESPACE = re.compile("[ \r\t\n]*")
ITEM = re.compile("([^ \r\t\n([]*)[ \r\t\n]*[([]") 
STRING = re.compile('"([^"]*)"')
CHAR = re.compile("'(.)'")
NUMBER = re.compile('(-?[\d.]+)(mil|mm)?')
ITEMSSTART = re.compile('[ \r\t\n]*\(')

class StringValue:
    def __init__(self, value):
        self.value = value
    def save(self, f):
        f.write('"')
        f.write(self.value)
        f.write('"')
    def flags(self):
        return set(self.value.split(','))
    def array(self):
        return self.value.split(':')
    def pin(self):
        return self.value.split('-')
    def str(self):
        return self.value

def flags(f):
    return StringValue(','.join(f))

class CharValue:
    def __init__(self, value):
        self.value = value
    def char(self):
        return self.value
    def save(self, f):
        f.write("'")
        f.write(self.value)
        f.write("'")

def nm(nm):
    if nm == 0:
        return NumericValue(0, None)
    if nm % 254 == 0:
        return NumericValue(nm / 25400, "mil")
    return NumericValue(nm / 1e6, "mm")

class NumericValue:
    def __init__(self, value, unit = None):
        if isinstance(value, (int, float)):
            self.value = value
        elif '.' in value:
            self.value = float(value)
        else:
            self.value = int(value)
        self.unit = unit
    def __str__(self):
        return str(self.value) + (self.unit if self.unit else '')
    def save(self, f):
        f.write(str(self))
    def num(self):
        if self.unit:
            raise Exception('does not expect unit')
        return self.value
    def distance(self):
        """ distance in nm """
        if self.unit == 'mil':
            return round(self.value * 0.0254 * 1e6)
        elif self.unit == 'mm':
            return round(self.value * 1e6)
        elif self.value == 0:
            return 0
        else:
            raise Exception("unknown units")
            

class Item:
    def __init__(self, name, attributes, old = False, children = None):
        self.name = name
        self.attributes = attributes
        self.children = children
        self.old = old;
    def __repr__(self):
        return self.name +  repr(self.attributes) + repr(self.children)
    def save(self, f, level = 0):
        if self.name == 'comment':
            f.write('#')
            f.write(self.attributes[0])
            f.write('\n')
            return
        f.write('\t' * level)
        f.write(self.name)
        if self.attributes is not None:
            f.write('(' if self.old else '[')
            sep = ''
            for a in self.attributes:
                f.write(sep)
                sep = ' '
                a.save(f)
            f.write(')' if self.old else ']')
        if self.children is not None:
            f.write('\n'+ ('\t' * level) + '(\n')
            for c in self.children:
                c.save(f, level + 1)
            f.write(('\t' * level) + ')')
        f.write('\n')

        
def parseValue(s, idx):
    res = STRING.match(s, idx)
    if res:
        return StringValue(res.group(1)), res.end()
    res = CHAR.match(s, idx)
    if res:
        return CharValue(res.group(1)), res.end()

    res = NUMBER.match(s, idx)
    if res:
        return NumericValue(res.group(1), res.group(2)), res.end()
    raise Exception("Syntax error near idx %s, %s" % (idx, s[idx:idx+30]))


def parseString(s, idx):
    pass

def parseComment(s, idx):
    end = s.find('\n', idx)
    return Item('comment', [s[idx:end]], False, None), end

def parseAttribute(s,idx):
    if s[idx] == ')' or s[idx] == ']':
        return None, idx + 1

    return parseValue(s, idx)

def parseAttributes(s, idx):
    res = []
    while True:
        idx = WHITESPACE.match(s, idx).end()
        attr, idx = parseAttribute(s, idx)
        if attr is None:
            return res, idx
        res.append(attr)

def parseItem(s, idx):
    if idx == len(s) or s[idx] == ')' :
        return None, idx + 1
    if s[idx] == '#':
        return parseComment(s,idx+1)
    r = ITEM.match(s,idx)
    if not r:
        raise Exception("Syntax error near idx %s, %s" % (idx, s[idx:idx+30]))
    name = r.group(1)
    idx = r.end()
    old = s[idx - 1] == '('
    if name == 'Hole':  #hole does not have attributes
        attr = None
        idx -= 1 #move before items of hole
    else:
        attr, idx = parseAttributes(s, idx)
    items = None
    r = ITEMSSTART.match(s, idx)
    if r:
        items, idx = parseItems(s, r.end())
    return Item(name, attr, old, items), idx

def parseItems(s, idx):
    res = []
    while True:
        idx = WHITESPACE.match(s, idx).end()
        item, idx = parseItem(s, idx)
        if item is None:
            return res, idx
        res.append(item)

def load(path):
    with open(path) as f:
        s = f.read()
        r,idx = parseItems(s, 0)
        return r


def save(path, items):
    with open(path, 'w') as f:
        for i in items:
            i.save(f)
