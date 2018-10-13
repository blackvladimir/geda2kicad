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
    'aux_axis_origin']

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
        else:
            print('U', c.name)

class Kicad:
    nets = {}
    classes = []

a = load('kicadtest.kicad_pcb')
loadPcb(a)
