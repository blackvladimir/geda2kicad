import gschem, eeschema, table
import time, sys
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

def text(kt, gt, v):
    kt.text = v
    kt.x, kt.y = coor(gt.x, gt.y)
    if gt.visibility:
        kt.flags = '0000'

if len(sys.argv) < 3:
    print("usage\n%s gschem.sch kicad.sch" % sys.argv[0])
    sys.exit(1)

ts = int(time.time())

components = table.load('symbols.csv')

gitems = gschem.load(sys.argv[1])
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
        if hasattr(gi, 'attributes'):
            for a in gi.attributes:
                k, v = a.text.split('=')
                if k == 'netname':
                    label = eeschema.Text()
                    label.type = 'Label'
                    label.shape = '~'
                    label.x, label.y = coor(a.x, a.y)
                    label.orientation = 0
                    label.size = 50
                    if v.startswith('\_') and v.endswith('\_') and len(v) > 3:
                        v = '~' + v[2:-2]
                    label.text = v
                    eitems.append(label)

    if isinstance(gi, gschem.Componnent):
        if gi.basename in components:
            name, xoff, yoff, aoff = components[gi.basename]
            xoff, yoff, aoff = int(xoff), int(yoff), int(aoff)  #TODO do this when table is loaded
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
                f.flags = '0001'    #hidden
                f.just = 'C'
                f.style = 'CNN'
                component.fields.append(f)
            if hasattr(gi, 'attributes'):
                for a in gi.attributes:
                    k, v = a.text.split('=')
                    if k == 'refdes':
                        component.ref = v
                        text(component.fields[0], a, v)
                    if k == 'value':
                        text(component.fields[1], a, v)
                        
            component.name = name
            component.N = 1
            component.mm = 1
            component.ts = ts
            ts += 1
            component.x, component.y = coor(gi.x  + xoff, gi.y + yoff)
            component.orientation = orientConv[((gi.angle + aoff) % 360, gi.mirror)]
            eitems.append(component)
        else:
            print('Skipping', gi.basename)

eeschema.save(sys.argv[2], eitems)
