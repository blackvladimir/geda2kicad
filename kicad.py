from parsekicad import load, distance


def loadGeneral(s):
    g = General
    for c in s.items:
        if c.name == 'thickness':
            g.thickness = distance(c.items[0])
        elif c.name == 'drawings':
            g.drawings = int(c.items[0])
        elif c.name == 'tracks':
            g.tracks = int(c.items[0])
        elif c.name == 'zones':
            g.zones = int(c.items[0])
        elif c.name == 'modules':
            g.modules = int(c.items[0])
        elif c.name == 'nets':
            g.nets = int(c.items[0])
        else:
            print(c.name)
    return g

class General:
    pass

class Layer:
    def __init__(self, num, name, t):
        self.num = num
        self.name = name
        self.t = t

plotbool = [
      'usegerberextensions',
      'usegerberattributes',
      'usegerberadvancedattributes',
      'creategerberjobfile',
      'excludeedgelayer',
      'plotframeref',
      'viasonmask',
      'useauxorigin',
      'psnegative',
      'psa4output',
      'plotreference',
      'plotvalue',
      'plotinvisibletext',
      'padsonsilk',
      'subtractmaskfromsilk',
      'mirror']

plotdistance = [
      'linewidth',
      'hpglpendiameter',]

plotint = [
      'outputformat',
      'drillshape',
      'scaleselection',
      'mode',
      'hpglpennumber',
      'hpglpenspeed']

def loadPlotParams(s):
    r = Setup()
    for c in s.items:
        if c.name == 'layerselection':
            l1, l2 = c.items[0].split('_')
            r.lselect1 = int(l1[2:], 16)
            r.lselect2 = int(l2, 16)
        elif c.name == 'outputdirectory':
            r.outdir = c.items[0]
        elif c.name in plotbool:
            r.__setattr__(c.name, c.items[0] == 'true')
        elif c.name in plotdistance:
            r.__setattr__(c.name, distance(c.items[0]))
        elif c.name in plotint:
            r.__setattr__(c.name, int(c.items[0]))
        else:
            print('x', c.name)

    return r

class PlotParams:
    pass

setupdistance = [
    'last_trace_width',
    'trace_clearance',
    'zone_clearance',
    'trace_min',
    'segment_width',
    'edge_width',
    'via_size',
    'via_drill',
    'via_min_size',
    'via_min_drill',
    'uvia_size',
    'uvia_drill',
    'uvia_min_size',
    'uvia_min_drill',
    'pcb_text_width',
    'mod_edge_width',
    'mod_text_width',
    'pad_drill',
    'pad_to_mask_clearance']

setupsize = [
    'mod_text_size',
    'pad_size',
    'pcb_text_size',
    'aux_axis_origin',
    'grid_origin']

setupbool = [
    'uvias_allowed',
    'zone_45_only']


def loadSetup(s):
    r = Setup()
    for c in s.items:
        if c.name in setupdistance:
            r.__setattr__(c.name, distance(c.items[0]))
        elif c.name in setupsize:
            r.__setattr__(c.name, (distance(c.items[0]), distance(c.items[1])))
        elif c.name == 'visible_elements':
            r.visible_elements = int(c.items[0], 16)
        elif c.name in setupbool:
            r.__setattr__(c.name, c.items[0] == 'yes')
        elif c.name == 'pcbplotparams':
            r.plotparams = loadPlotParams(c)
        else:
            print('x', c.name)

    return r

class Setup:
    pass

classdistance = [
    'clearance',
    'trace_width',
    'via_dia',
    'via_drill',
    'uvia_dia',
    'uvia_drill']

def loadClass(s):
    r = netClass()
    r.name = s.items[0]
    r.descr = s.items[1]
    for c in s.items[2:]:
        if c.name in classdistance:
            r.__setattr__(c.name, distance(c.items[0]))
        elif c.name == 'add_net':
            r.nets.append(c.items[0])
        else:
            print('x', c.name)

    return r


class netClass:
    nets = []

modulestrings = [
        'layer',
        'descr',
        'tags',
        'path']

def loadText(s):
    r = Text()
    r.t = s.name
    i = 1
    if s.name == 'fp_text':
        r.t = s.items[0]
        i += 1
    r.text = s.items[i]
    for c in s.items[i:]:
        if c.name == 'at':
            r.pos = loadPos(c)
        elif c.name == 'layer':
            r.layer = c.items[0]
        elif c.name == 'effects':   #TODO function for efects parsing
            for c2 in c.items:
                if c2.name == 'font':
                    for c3 in c2.items:
                        if c3 == 'italic':
                            r.italic = True
                        elif c3.name == 'size':
                            r.sx = distance(c3.items[0])
                            r.sy = distance(c3.items[1])
                        elif c3.name == 'thickness':
                            r.thickness = distance(c3.items[0])
                        else:
                            print(c3.name)
                elif c2.name == 'justify':
                    for c3 in c2.items:
                        r.justify.add(c3)
                else:
                    print(c2.name)
        else:
            print('T', c.name)


class Text:
    italic = False
    justify = set()

def loadLine(s):
    r = Line()
    r.t = s.name
    for c in s.items:
        if c.name == 'start':
            r.start = (distance(c.items[0]), distance(c.items[1]))
        elif c.name == 'end':
            r.end = (distance(c.items[0]), distance(c.items[1]))
        elif c.name == 'width':
            r.widht = distance(c.items[0])
        elif c.name == 'layer':
            r.layer = c.items[0]
        elif c.name == 'net':
            r.net = c.items[0]
        elif c.name == 'tstamp':
            r.tstamp = int(c.items[0],16)
        else:
            print(c.name)
    return r


class Line:
    net = None
    tstamp = None

def loadCircle(s):
    r = Circle()
    r.t = s.name
    for c in s.items:
        if c.name == 'center' or c.name == 'start':
            r.center = (distance(c.items[0]), distance(c.items[1]))
        elif c.name == 'end':
            r.end = (distance(c.items[0]), distance(c.items[1]))
        elif c.name == 'width':
            r.widht = distance(c.items[0])
        elif c.name == 'layer':
            r.layer = c.items[0]
        elif c.name == 'angle':
            r.angle = float(c.items[0])
        else:
            print(c.name)


class Circle:
    angle = 360

def loadPad(s):
    r =  Pad()
    r.name = s.items[0]
    r.t = s.items[1]
    r.shape = s.items[2]
    for c in s.items[3:]:
        if c.name == 'at':
            r.pos = loadPos(c)
        elif c.name == 'size':  
            r.size = (distance(c.items[0]), distance(c.items[1]))    #todo load size
        elif c.name == 'drill':  
            r.drill = distance(c.items[0])
        elif c.name == 'layers':  
            r.layers = c.items
    return r

class Pad:
    pass

def loadVia(s):
    r =  Pad()
    for c in s.items:
        if c.name == 'at':
            r.pos = loadPos(c)
        elif c.name == 'size':  
            r.size = distance(c.items[0])
        elif c.name == 'drill':  
            r.drill = distance(c.items[0])
        elif c.name == 'layers':  
            r.layers = c.items
    return r

class Via:
    pass

def load3DPos(s):
    if s.name == 'xyz':
        return distance(s.items[0]), distance(s.items[1]), distance(s.items[2])
    raise Exception('unknown coordinates ' + s.name) 


def loadModel(s):
    r = Model()
    r.path = s.items[0]
    for c in s.items[1:]:
        if c.name == 'at':
            r.pos = load3DPos(c.items[0])
        elif c.name == 'scale':
            r.scale = load3DPos(c.items[0])
        elif c.name == 'rotate':
            r.rotate = load3DPos(c.items[0])
        else:
            print(c)


class Model:
    pass

def loadPos(s):
    return distance(s.items[0]), distance(s.items[1]), float(s.items[2]) if len(s.items) == 3 else 0

def loadModule(s):
    r = Module()
    r.name = s.items[0]
    for c in s.items[1:]:
        if c.name in modulestrings:
            r.__setattr__(c.name, c.items[0])
        elif c.name == 'tedit':
            r.tedit = int(c.items[0],16)
        elif c.name == 'tstamp':
            r.tstamp = int(c.items[0],16)
        elif c.name == 'at':
            r.pos = loadPos(c)
        elif c.name == 'fp_text':
            r.texts.append(loadText(c))
        elif c.name == 'fp_line':
            r.lines.append(loadLine(c))
        elif c.name == 'fp_circle':
            r.circles.append(loadCircle(c))
        elif c.name == 'pad':
            r.pads.append(loadPad(c))
        elif c.name == 'model':
            r.model = loadModel(c)
        elif c.name == 'attr':
            r.attr = c.items[0]
        else:
            print('x', c.name)

    return r

class Module:
    texts = []
    lines = []
    pads = []
    circles = []

    

def loadZone(s):
    r = Zone()
    for c in s.items:
        if c.name == 'net':
            r.net = int(c.items[0])
        elif c.name == 'net_name':
            r.net_name = c.items[0]
        elif c.name == 'tstamp':
            r.tstamp = int(c.items[0], 16)
        elif c.name == 'layer':
            r.layer = c.items[0]
        elif c.name == 'hatch':
            r.hatchtype = c.items[0]
            r.hatchsize = distance(c.items[1])
        elif c.name == 'connect_pads':
            if c.items[0] in ['no', 'yes', 'thru_hole_only']:
                r.connect = c.items[0]
                clr = c.items[1]
            else:
                r.connect = 'thermal'
                clr = c.items[0]
            if clr.name != 'clearance':
                raise Exception('expected clearance')
            r.clearance = distance(clr.items[0])
        elif c.name == 'min_thickness':
            r.minthick = distance(c.items[0])
        elif c.name == 'keepout':
            for i in c.items:
                if i.items[0] != 'not_allowed':
                    raise Exception('unknown keyword '  + i.items[0])
                r.keepouts.add(i.name)
        elif c.name == 'fill':
            for c2 in c.items:
                if c2.name == 'arc_segments':
                    r.arc_segments = int(c2.items[0])
                elif c2.name == 'thermal_gap':
                    r.thermal_gap = distance(c2.items[0])
                elif c2.name == 'smoothing':
                    r.smoothing = c2.items[0]
                elif c2.name == 'thermal_bridge_width':
                    r.thermal_bridge_width = distance(c2.items[0])
                elif c2.name == 'radius':
                    r.radis = distance(c2.items[0])
        elif c.name == 'polygon':
            if c.items[0].name != 'pts':
                raise Exception('expect points')
            for c2 in c.items[0].items:
                if c2.name != 'xy':
                    raise Exception('expect coordinates')
                r.pts.append((distance(c2.items[0]), distance(c2.items[1])))
        else:
            print(c.name)

class Zone:
    keepouts = set()
    pts = []

def loadPcb(s):
    if s.name != 'kicad_pcb':
        raise Exception('Unknown format')
    pcb = Kicad()
    for c in s.items:
        if c.name == 'version':
            pcb.version = c.items[0]
        elif c.name == 'host':
            pcb.host = c.items
        elif c.name == 'general':
            pcb.general = loadGeneral(c)
        elif c.name == 'page':
            pcb.page = c.items[0]
        elif c.name == 'layers':
            pcb.layers = [Layer(int(l.name), l.items[0], l.items[1]) for l in c.items]
        elif c.name == 'setup':
            pcb.setup = loadSetup(c)
        elif c.name == 'net':
            pcb.nets[int(c.items[0])] = c.items[1]
        elif c.name == 'net_class':
            pcb.classes.append(loadClass(c))
        elif c.name == 'module':
            pcb.modules.append(loadModule(c))
        elif c.name == 'gr_arc' or c.name == 'gr_circle':
            pcb.circles.append(loadCircle(c))
        elif c.name == 'gr_line' or c.name == 'segment':
            pcb.lines.append(loadLine(c))
        elif c.name == 'gr_text':
            pcb.texts.append(loadText(c))
        elif c.name == 'via':
            pcb.vias.append(loadVia(c))
        elif c.name == 'zone':
            pcb.zones.append(loadZone(c))
        else:
            print('U', c.name)

class Kicad:
    nets = {}
    classes = []
    modules = []
    circles = []
    lines = []
    texts = []
    vias = []
    zones = []

a = load('kicadtest.kicad_pcb')
loadPcb(a)
