import re
WHITESPACE = re.compile("[ \r\t\n]*")
ITEM = re.compile("([^ \r\t\n]+)[ \r\t\n]*[([]")
STRING = re.compile('"([^"]*)"')
CHAR = re.compile("'([^;])'")
NUMBER = re.compile('(-?[\d.]+)(mil|mm)?')

class Item:
    def __init__(self, name, attributes = [], children = []):
        self.name = name
        self.attributes = attributes
        self.children = children
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

def parseAttributes(s, idx):    #TODO almost same as parse items
    res = []
    while True:
        idx = WHITESPACE.match(s, idx).end()
        attr, idx = parseAttribute(s, idx)
        if attr is None:
            return res, idx
        res.append(attr)

def parseItem(s, idx):
    if s[idx] == ')' or idx == len(s):
        return None, idx + 1
    if s[idx] == '#':
        return parseComment(s,idx)
    r = ITEM.match(s,idx)
    if not r:
        raise Exception("Syntax error near idx %s, %s" % (idx, s[idx:idx+30]))
    name = r.group(1)
    attr, idx = parseAttributes(s, r.end())
    return Item(name, attr), idx

def parseItems(s, idx):
    res = []
    while True:
        idx = WHITESPACE.match(s, idx).end()
        item, idx = parseItem(s, idx)
        if item is None:
            return res, idx
        res.append(item)

with open("lock.pcb") as f:
    s = f.read()
    r,idx = parseItems(s, 0)
    print(r)
