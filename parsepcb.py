import re
WHITESPACE = re.compile("[ \r\t\n]*")
ITEM = re.compile("([^ \r\t\n([]*)[ \r\t\n]*[([]")  #allow no name items
#ITEM = re.compile("([^ \r\t\n([]+)[ \r\t\n]*[([]")
STRING = re.compile('"([^"]*)"')
CHAR = re.compile("'(.)'")
NUMBER = re.compile('(-?[\d.]+)(mil|mm)?')
ITEMSSTART = re.compile('[ \r\t\n]*\(')

class Item:
    def __init__(self, name, attributes = [], old = False, children = []):
        self.name = name
        self.attributes = attributes
        self.children = children
        self.old = old;
    def __repr__(self):
        return self.name +  repr(self.attributes) + repr(self.children)

def parseString(s, idx):
    pass

def parseComment(s, idx):
    end = s.find('\n', idx)
    return Item('comment', [s[idx:end - idx]]), end

def parseAttribute(s,idx):
    if s[idx] == ')' or s[idx] == ']':
        return None, idx + 1

    res = STRING.match(s, idx)
    if res:
        return res.group(1), res.end()

    res = CHAR.match(s, idx)
    if res:
        return res.group(1), res.end()

    res = NUMBER.match(s, idx)
    if res:
        if res.group(2) is None:
            n = float(res.group(1))
        elif res.group(2) == 'mil':
            n = float(res.group(1)) * 100
        else: #mm
            n = float(res.group(1)) / 254e-6
        return n, res.end()
    raise Exception("Syntax error near idx %s, %s" % (idx, s[idx:idx+30]))

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
