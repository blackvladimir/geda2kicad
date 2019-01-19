import gschem, eeschema
from table import components
import time
orientConv = {
    (0, 0):   [1, 0,  0, -1],
    (90, 0):  [ 0, -1, -1, 0],
    (180, 0): [-1, 0, 0, 1],
    (270, 0): [0, 1, 1, 0],
    (0, 1):   [-1, 0, 0, -1],  
    (90, 1):  [0, -1, 1, 0],
    (180, 1): [1, 0, 0, 1],
    (270, 1): [0, 1, -1, 0],
}

def coor(x,y):
    return x // 2, -y // 2  #TODO configurable scale TODO move inside page 

ts = int(time.time())

gitems = gschem.load('lock.sch')
eitems = []

ver = eeschema.Version()
ver.version = 4
eitems.append(ver)

layers = eeschema.Layers()
layers.nn = 26
layers.mm = 0
eitems.append(layers)

page = eeschema.Page()
page.format = 'A4'
page.dimx = 11693
page.dimy = 8268
page.fields = {}
eitems.append(page)

for gi in gitems:
    if isinstance(gi, gschem.Net):
        wire = eeschema.Wire()
        wire.x1, wire.y1 = coor(gi.x1, gi.y1)
        wire.x2, wire.y2 = coor(gi.x2, gi.y2)
        wire.type = 'Wire'
        eitems.append(wire)

        con = eeschema.Connection()
        con.x, con.y = coor(gi.x1, gi.y1)
        eitems.append(con)

        con = eeschema.Connection()
        con.x, con.y = coor(gi.x2, gi.y2)
        eitems.append(con)

    if isinstance(gi, gschem.Componnent):
        if gi.basename in components:
            name, xoff, yoff, aoff = components[gi.basename]
            if gi.mirror:
                xoff = -xoff
            if gi.angle == 90:
                xoff, yoff = -yoff, xoff
            if gi.angle == 180:
                xoff, yoff = -xoff, -yoff
            if gi.angle == 270:
                xoff, yoff = yoff, -xoff
            component = eeschema.Componnent()
            component.fields = []
            component.ref = 'X'
            for i in range(3):  #defailt fields
                f = eeschema.Field()
                f.text = ''
                f.orientation = 'H'
                f.x, f.y = coor(gi.x, gi.y)
                f.size = 50
                f.flags = '0000'
                f.just = 'C'
                f.style = 'CNN'
                component.fields.append(f)
            if hasattr(gi, 'attributes'):
                for a in gi.attributes:
                    k, v = a.text.split('=')
                    if k == 'refdes':
                        component.ref = v
                        component.fields[0].text = v
                    if k == 'value':
                        component.fields[1].text = v
                        
            component.name = name
            component.N = 1
            component.mm = 1
            component.ts = ts
            ts += 1
            component.x, component.y = coor(gi.x  + xoff, gi.y + yoff)
            component.orientation = orientConv[((gi.angle + aoff) % 360, gi.mirror)]
            eitems.append(component)

eeschema.save('kicadexp.sch', eitems)
