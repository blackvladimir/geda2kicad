import re
WHITESPACE = re.compile("[ \r\t\n]*")
NAME = re.compile("[^ \r\t\n)]+") 
STRING = re.compile('"([^"]*)"')
CHAR = re.compile("'(.)'")
NUMBER = re.compile('(-?[\d.]+)(mil|mm)?')
ITEMSSTART = re.compile('[ \r\t\n]*\(')

class S:
    def __init__(self, name, items):
        self.name = name
        self.items = items
    def __repr__(self):
        return '%s:%r' % (self.name, self.items)

    def save(self, f, level):
        f.write(' ' * level)
        f.write('(')
        f.write(self.name)
        for i in self.items:
            if isinstance(i, S):
                f.write('\n')
                i.save(f, level + 1)
            else:
                f.write(' ')
                if not i:
                    f.write('""')
                elif '(' in i or ')' in i or ' ' in i:
                    f.write('"')
                    f.write(i)
                    f.write('"')
                else:
                    f.write(i)
        f.write(')')

def parseQuoted(s, idx):
    start = idx
    while True:
        if s[idx] == '"':
            idx += 1
            if s[idx] != '"':
                return s[start:idx-1], idx
        idx += 1

def parseItem(s, idx):
    idx = WHITESPACE.match(s,idx).end()
    if s[idx] == ')':
        return None, idx + 1
    if s[idx] == '"':
        return parseQuoted(s, idx + 1)
    if s[idx] == '(':
        return parseS(s, idx + 1)
    e = NAME.match(s, idx).end()
    return s[idx:e], e


def parseS(s, idx):
    name, idx =  parseItem(s,idx)
    items = []
    while True:
        value, idx = parseItem(s, idx)
        if value is None:
            return S(name, items), idx
        items.append(value)


def load(path):
    with open(path) as f:
        s = f.read()
        if s[0] != '(':
            raise Exception('file must start with (')
        r,idx = parseS(s,1)
        return r

def save(path, s):
    with open(path,'w') as f:
        s.save(f, 0)

a = load('kicadtest.kicad_pcb')
save('pok.kicad_pcb', a)
