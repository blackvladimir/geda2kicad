from pcb import Pcb
from kicad import Kicad, NetClass, Setup, Via, Segment, Line, Text, Effects, Arc, Zone, Module, Pad
from math import sin, cos, pi
import sys


def kicadLine(line, layer):
    s = Line()
    s.start = (line.x1, line.y1)
    s.end = (line.x2, line.y2)
    s.width = line.thick
    s.layer = layer
    return s

def kicadArc(arc, layer):
    a = Arc()
    a.start = (arc.x, arc.y)
    r = arc.width #pcb probably uses just width
    a.end = (arc.x - r * cos(arc.startAngle / 180 * pi), arc.y + r * sin(arc.startAngle / 180 * pi))
    a.angle = -arc.angle
    a.layer = layer
    a.width = arc.thick
    return a

def kicadText(text, x,y, dir, scale, layer, typ = None):
    t = Text()
    t.layer = layer
    t.effects = Effects()
    height = scale / 100 * 1.27e6  #defaul pcb font (height is 1.27mm)
    t.effects.size = [height, height]
    t.effects.thickness = scale / 100 * 0.2e6 #default pcb font (thick 0.2mm)
    t.effects.justify = ['left']
    t.at = (x, y  - height / 2, dir*90) #TODO placement of rotated text #TODO mirrored text (on bottom layers?)
    t.effects.italic = False
    t.t = typ
    t.text = text
    return t

def getLayerName(l): #TODO use groups and generate layer map?
    name = l.name
    if name == 'outline' and 'outline' not in l.flags:
        print('layer named outline without outline type, assuming outline')
        l.flags = {'outline'}

    if 'copper' in l.flags:
        name += '.Cu'
    elif 'outline' in l.flags:
        name = 'Edge.Cuts'
    else:
        name += '.SilkS'

    return name


def pcb2kicad(pcb):
    kicad = Kicad()
    kicad.version = '20171130'
    kicad.host = ['pcbnew', '5.0.0']

    #TODO thermal parameter in zones

    kicad.setup = Setup()
    kicad.setup.trace_min = pcb.minWidth
    kicad.setup.via_min_drill = pcb.minDrill
    kicad.setup.via_min_size = pcb.minWidth + pcb.minRing
    #TODO mask settings?

    innum = 1
    for g in pcb.groups:
        if 'c' in g:
            name = 'F'
        elif 's' in g:
            name = 'B'
        else:
            name = 'In' + str(innum)
            innum += 1
        for l in pcb.layers:
            if str(l.number) in g and l.name != 'outline': #layer named outline is presumed to be outline
                l.name = name #layers in same group will have same name so they will be merged
                l.flags.add('copper')

    topsilk = False
    for l in pcb.layers: #older versions have two layers named silk (first is bottom second is top/front)
        if (l.name == 'silk' and topsilk) or l.name == 'top silk':
            l.name = 'F'
        elif l.name in ('silk', 'bottom silk'):
            l.name = 'B'
            topsilk = True
        

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

    partsdic = {} #used for connections
    for e in pcb.elements:
        m = Module()
        partsdic[e.name] = m
        m.name = e.description
        side = 'B' if 'onsolder' in e.flags else 'F'
        m.layer = side + '.Cu'
        m.at = (e.x, e.y)
        m.texts.append(kicadText(e.name, e.textx, e.texty, e.tdir, e.tscale, side + '.SilkS', 'reference'))
        m.texts.append(kicadText(e.value, 0, 0, e.tdir, e.tscale, side + '.Fab', 'value'))
        m.texts.append(kicadText('%R', 0, 0, e.tdir, e.tscale, side + '.Fab', 'user'))
        for pad in e.pads:
            p = Pad()
            x = (pad.x1 + pad.x2) / 2
            y = (pad.y1 + pad.y2) / 2
            w = abs(pad.x1 - pad.x2) + pad.thick
            h = abs(pad.y1 - pad.y2) + pad.thick
            p.at = (x, y)
            p.size = (w, h)
            pside = 'B' if 'onsolder' in pad.flags else 'F'
            p.layers = [pside  + '.Cu', pside + '.Mask']
            if not 'nopaste' in pad.flags:
                p.layers.append(pside + '.Paste')
            p.name = pad.number
            p.t = 'smd'
            p.shape = 'rect' if 'square' in pad.flags else 'oval'
            m.pads.append(p)
        for pin in e.pins:
            p = Pad()
            p.at = (pin.x, pin.y)
            p.size = (pin.dimater, pin.dimater)
            p.drill = pin.drill
            p.layers = ['*.Cu', '*.Mask']
            p.name = pin.number
            p.t = 'np_thru_hole' if 'hole' in pin.flags else 'thru_hole'
            p.shape = 'rect' if 'square' in pin.flags else 'circle'
            m.pads.append(p)
        for line in e.lines:
            m.lines.append(kicadLine(line, side + '.SilkS'))
            m.lines.append(kicadLine(line, side + '.Fab'))  #TODO optional?
        for arc in e.arcs:
            m.arcs.append(kicadArc(arc, side + '.SilkS'))
            m.arcs.append(kicadArc(arc, side + '.Fab'))  #TODO optional?
        

        kicad.modules.append(m)

    i = 1
    for n in pcb.netlist.nets:
        kicad.nets[i] = n.name #TODO net classes if they are used
        for c in n.connects:
            try:
                m = partsdic[c.part]
                for pad in m.pads:
                    if pad.name == c.pin:
                        pad.net = (i, n.name)
            except KeyError:
                print('part %s not found: netlist connection not exported' % c.part)
        i += 1


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
                kicad.lines.append(kicadLine(line, layer))
        for text in l.texts:
            kicad.texts.append(kicadText(text.string, text.x, text.y, text.dir, text.scale, layer))
        for arc in l.arcs:
            kicad.arcs.append(kicadArc(arc, layer))    #TODO detect circles?
        for poly in l.polygons:
            z = Zone()
            z.layer = layer     #TODO detect net?
            z.pts = poly.points
            kicad.zones.append(z)
            for h in poly.holes:
                z = Zone()
                z.layer = layer
                z.pts = h.points
                z.keepouts = {'copperpour'}
                kicad.zones.append(z)
    return kicad

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('usage:\n%s infile.pcb [outfile.kicad_pcb]' % sys.argv[0])
        exit(1)
    infile = sys.argv[1]
    if len(sys.argv) == 2:
        if infile.endswith('.pcb'):
            outfile = infile[:-3] + 'kicad_pcb'
        else:
            print('infile does not end with .pcb, can not guess outfile')
            exit(1)
    else:
        outfile = sys.argv[2]

    pcb = Pcb(infile)
    kicad = pcb2kicad(pcb)
    kicad.save(outfile)
    print('kicad written to %s' % outfile)
