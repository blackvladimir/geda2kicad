import re

def loadFields(s):
    fields = s.split(' ')
    r = []
    while fields:
        f = fields.pop(0)
        if f:
            if f[0] == '"':
                f = f[1:]
                if f and f[-1] == '"':
                    f = f[0:-1]
                else:
                    p = fields.pop(0)
                    while p == "" or p[-1] != '"':
                        f += ' ' + p
                        p = fields.pop(0)
                    f += ' ' + p[0:-1]
            r.append(f)
    return r

def saveFields(*fields):
    r = []
    for f in fields:
        f = str(f)
        if ' ' in f and f[0] != '"':
            r.append('"' + f + '"')
        else:
            r.append(f)
    return ' '.join(r)

def q(s):
    return '"' + s + '"'


class Version:
    def parse(self, attributes, lines):
        self.version = int(attributes[4])
    def save(self):
        return ['EESchema Schematic File Version ' +  str(self.version)]

class Libs:
    def parse(self, attributes, lines): #libs are not used so it is not needed for export
        self.fields = attributes
    def save(self):
        return [saveFields(*self.fields)]

class Layers:
    def parse(self, attributes, lines):
        self.nn = int(attributes[1])    #documentation does not say what this is
        self.mm = int(attributes[2])
        if lines[0] != 'EELAYER END':
            raise "Don't know what to do with layers"
        lines.pop(0)
    def save(self):
        return ['EELAYER %s %s' % (self.nn, self.mm), 'EELAYER END']

class Page:
    def parse(self, attributes, lines):
        self.format = attributes[1]
        self.dimx = int(attributes[2])
        self.dimy = int(attributes[3])
        self.fields = {}
        line = lines.pop(0)
        while line != '$EndDescr':
            k, v = line.split(' ', 1)
            self.fields[k] = v
            line = lines.pop(0)
    def save(self):
        r =  ['$Descr %s %s %s' % (self.format, self.dimx, self.dimy)]
        for k, v in self.fields.items():
            r.append(k + ' ' + v)
        r.append('$EndDescr')
        return r

class Field:
    def parse(self, fields):
        self.text = fields[2]
        self.orientation = fields[3]
        self.x = int(fields[4])
        self.y = int(fields[5])
        self.size = int(fields[6])
        self.flags = fields[7]
        self.just = fields[8]
        self.style = fields[9]
        if len(fields) > 10:
            self.name = fields[10]
    def save(self, number):
        if hasattr(self,"name"):
            return saveFields('F', number, q(self.text), self.orientation, self.x, self.y, self.size, self.flags, self.just, self.style, q(self.name))
        else:
            return saveFields('F', number, q(self.text), self.orientation, self.x, self.y, self.size, self.flags, self.just, self.style)

class Text:
    def parse(self, attributes, lines):
        self.type = attributes[1]
        self.x = int(attributes[2])
        self.y = int(attributes[3])
        self.orientation = int(attributes[4])
        self.size = int(attributes[5])
        self.shape = attributes[6]
        self.text = lines.pop(0)
    def save(self):
        return [saveFields('Text', self.type, self.x, self.y, self.orientation, self.size, self.shape), self.text]

class Componnent:
    def parse(self, attributes, lines):
        f = loadFields(lines.pop(0))
        self.fields = []
        while f[0] != '$EndComp':
            if f[0] == 'L':
                self.name = f[1]
                self.ref = f[2]
            elif f[0] == 'U':
                self.N = f[1]  #number of instance in package 
                self.mm = f[2] #don't know what it is
                self.ts = int(f[3], 16)
            elif f[0] == 'P':
                self.x = f[1]  #number of instance in package 
                self.y = f[2] #don't know what it is
            elif f[0] == 'F':
                field = Field()
                field.parse(f)
                self.fields.append(field)
            else:
                if len(f) == 4:
                    f[0] = f[0].strip()
                    self.orientation = f
            f = loadFields(lines.pop(0))
    def save(self):
        r =  ['$Comp']
        r.append(saveFields('L', self.name, self.ref))
        r.append(saveFields('U', self.N, self.mm, hex(self.ts)[2:]))
        r.append(saveFields('P', self.x, self.y))
        for i, f in enumerate(self.fields):
            r.append(f.save(i))
        r.append(saveFields('\t%s' % self.N, self.x, self.y))
        r.append('\t' + saveFields(*self.orientation))
        r.append('$EndComp')
        return r
        
class Wire:
    def parse(self, attributes, lines):
        self.type = attributes[1]
        attributes = loadFields(lines.pop(0))
        self.x1 = int(attributes[0])
        self.y1 = int(attributes[1])
        self.x2 = int(attributes[2])
        self.y2 = int(attributes[3])
    def save(self):
        return [saveFields('Wire', self.type, 'Line'), '\t' + saveFields(self.x1, self.y1, self.x2, self.y2)]

class Connection:
    def parse(self, attributes, lines):
        self.x = int(attributes[2])
        self.y = int(attributes[3])
    def save(self):
        return [saveFields('Connection', '~', self.x, self.y)]

def loadItems(lines, end = None):
    items = []
    while lines:
        line = lines.pop(0)
        if not line:
            continue
        attributes = loadFields(line)
        t = attributes[0]
        cl = None
        if t == 'EESchema':
            cl = Version
        elif t.startswith('LIBS'):
            cl = Libs
        elif t == 'EELAYER':
            cl = Layers
        elif t == '$Descr':
            cl = Page
        elif t == '$Comp':
            cl = Componnent
        elif t == 'Wire':
            cl = Wire
        elif t == 'Connection':
            cl = Connection
        elif t == 'Text':
            cl = Text
        elif t == '$EndSCHEMATC':
            return items
        else:
            raise(Exception('unknown type ' + t))
        i = cl()
        i.parse(attributes, lines)
        items.append(i)

    raise(Exception('no end'))

def saveItems(items):
    lines = []
    for i in items:
        lines += i.save()
    lines += ['$EndSCHEMATC']
    return lines

def load(path):
    with open(path) as f:
        lines = f.read().split('\n')
        return loadItems(lines)

def save(path, items):
    lines = saveItems(items)
    with open(path,'w') as f:
        f.write('\n'.join(lines))

