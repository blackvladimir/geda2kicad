import gschem, eeschema
def coor(x,y):
    return x // 2, -y // 2  #TODO configurable scale TODO move inside page 

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

eeschema.save('kicadexp.sch', eitems)
