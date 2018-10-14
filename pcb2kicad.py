from pcb import Pcb
from kicad import Kicad, NetClass, Setup, Via, Segment, Line, Text, Effects, Arc
from math import sin, cos, pi


def getLayerName(l): #TODO use groups and generate layer map?
    name = l.name
    if name in {'bottom', 'bottom silk'}:
        name = 'B'
    if name in {'top', 'top silk'}:
        name = 'F'
    if 'copper' in l.flags:
        name += '.Cu'
    elif 'outline' in l.flags:
        name = 'Edge.Cuts'
    else:
        name += '.SilkS'
    return name


pcb = Pcb('lock.pcb')
kicad = Kicad()
kicad.version = '20171130'
kicad.host = ['pcbnew', '5.0.0']

#TODO thermal parameter in zones

kicad.setup = Setup()
kicad.setup.trace_min = pcb.minWidth
kicad.setup.via_min_drill = pcb.minDrill
kicad.setup.via_min_size = pcb.minWidth + pcb.minRing

for s in pcb.styles:
    c = NetClass()
    c.name = s.name
    c.descr = s.name
    c.clearance = s.spacing
    c.trace_width = s.thick
    c.via_dia = s.diameter
    c.via_drill = s.drill
    kicad.classes.append(c)

for pv in pcb.vias:
    v = Via()
    v.at = (pv.x, pv.y)
    v.size = pv.diameter
    v.drill = pv.drill
    v.layers = [ 'F.Cu' , 'B.Cu'] #TODO burried
    kicad.vias.append(v)

for l in pcb.layers:
    layer = getLayerName(l)
    for line in l.lines:
        if 'copper' in l.flags:
            s = Segment()
            s.start = (line.x1, line.y1)
            s.end = (line.x2, line.y2)
            s.width = line.thick
            s.layer = layer
            kicad.segments.append(s)
        else:
            s = Line()
            s.start = (line.x1, line.y1)
            s.end = (line.x2, line.y2)
            s.width = line.thick
            s.layer = layer
            kicad.lines.append(s)
    for text in l.texts:
        t = Text()
        t.layer = layer
        t.effects = Effects()
        height = text.scale / 100 * 1.27e6  #defaul pcb font (height is 1.27mm)
        t.effects.size = [height, height]
        t.effects.thickness = text.scale / 100 * 0.2e6 #default pcb font (thick 0.2mm)
        t.effects.justify = ['left']
        t.at = (text.x, text.y - height / 2, text.dir)
        t.effects.italic = False
        t.text = text.string
        t.t = None
        kicad.texts.append(t)
    for arc in l.arcs:
        a = Arc()
        a.start = (arc.x, arc.y)
        r = arc.width #pcb probably uses just width
        a.end = (arc.x - r * cos(arc.startAngle / 180 * pi), arc.y + r * sin(arc.startAngle / 180 * pi))
        a.angle = -arc.angle
        a.layer = layer
        a.width = arc.thick
        kicad.arcs.append(a)    #TODO detect circles?
    for poly in l.polygons:
        pass

kicad.save('export.kicad_pcb')
