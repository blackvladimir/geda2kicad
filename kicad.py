from parsekicad import load, distance, save, S

class StringField:
    def loadS(s, parent):
        parent.__setattr__(s.name, s.items[0])

class ClassField:
    def __init__(self, c):
        self.c = c
    def loadS(self, s, parent):
        obj = self.c()
        obj.loadS(s)
        parent.__setattr__(s.name, obj)

class ArrayField:
    def __init__(self, c, name):
        self.c = c
        self.name = name
    def loadS(self, s, parent):
        obj = self.c()
        obj.loadS(s)
        parent.__getattribute__(self.name).append(obj)

class LayersField:
    def loadS(s, parent):
        parent.layers = [Layer(int(l.name), l.items[0], l.items[1]) for l in s.items]

class NetsField:
    def loadS(s, parent):
        parent.nets[int(s.items[0])] = s.items[1]

class DistanceField:
    def loadS(s, parent):
        parent.__setattr__(s.name, distance(s.items[0]))
class IntField:
    def loadS(s, parent):
        parent.__setattr__(s.name, int(s.items[0]))
class SizeField:
    def loadS(s, parent):
        parent.__setattr__(s.name, (distance(s.items[0]), distance(s.items[1])))
class BoolField:
    def loadS(s, parent):
        parent.__setattr__(s.name, s.items[0] in ['yes', 'true'])
class HexField:
    def loadS(s, parent):
        parent.__setattr__(s.name, int(s.items[0], 16))
class NetArrayField:
    def loadS(s, parent):
        parent.nets.append(s.items[0])
class NetField:
    def loadS(s, parent):
        parent.net = (int(s.items[0]), s.items[1])
class PosField:
    def loadS(s, parent):
        if len(s.items) == 3:
            parent.__setattr__(s.name, (distance(s.items[0]), distance(s.items[1]), float(s.items[2])))
        else:
            parent.__setattr__(s.name, (distance(s.items[0]), distance(s.items[1])))
class FontField:
    def loadS(s, parent):
        parent.italic = False
        for c in s.items:
            if c == 'italic':
                parent.italic = True
            elif c.name == 'size':
                SizeField.loadS(c, parent)
            elif c.name == 'thickness':
                DistanceField.loadS(c, parent)
            else:
                raise Exception('unknown field ' + c.name)

class LayerSelectionField:
    def loadS(s, parent):
        l1, l2 = s.items[0].split('_')
        parent.lselect1 = int(l1[2:], 16)
        parent.lselect2 = int(l2, 16)
class FlagField:
    def loadS(s, parent):
        parent.__setattr__(s.name, set(s.items))
class Pos3DField:
    def loadS(s, parent):
        pos = s.items[0]
        if pos.name != 'xyz':
            raise Exception('unknown coordinates ' + pos.name)
        parent.__setattr__(s.name, (distance(pos.items[0]), distance(pos.items[1]), distance(pos.items[2])))
class FloatField:
    def loadS(s, parent):
        parent.__setattr__(s.name, float(s.items[0]))
class HatchField:
    def loadS(s, parent):
        parent.hatchtype = s.items[0]
        parent.hatchsize = distance(s.items[1])
class ConnectField:
    def loadS(s, parent):
        if s.items[0] in ['no', 'yes', 'thru_hole_only']:
            parent.connect = s.items[0]
            clr = s.items[1]
        else:
            parent.connect = 'thermal'
            clr = s.items[0]
        if clr.name != 'clearance':
            raise Exception('expected clearance')
        parent.clearance = distance(clr.items[0])
class KeepoutsField:
    def loadS(s, parent):
        parent.keepouts = set()
        for i in s.items:
            if i.items[0] != 'not_allowed':
                raise Exception('unknown keyword '  + i.items[0])
            parent.keepouts.add(i.name)
class PointsField:
    def loadS(s, parent):
        parent.pts = []
        if s.items[0].name != 'pts':
            raise Exception('expect points')
        for c in s.items[0].items:
            if c.name != 'xy':
                raise Exception('expect coordinates')
            parent.pts.append((distance(c.items[0]), distance(c.items[1])))

class Loadable:
    def loadS(self,s):
        self.loadFields(s.items)
    def loadFields(self, items):
        for i in items:
            self.fields[i.name].loadS(i, self)


class General(Loadable):
    fields = {
            'thickness' : DistanceField,
            'drawings' : IntField,
            'tracks' : IntField,
            'zones' : IntField,
            'modules' : IntField,
            'nets' : IntField
            }
    def loadS(self, s):
        self.loadFields(s.items)

class Layer:
    def __init__(self, num, name, t):
        self.num = num
        self.name = name
        self.t = t

class PlotParams(Loadable):
    fields = {
        'usegerberextensions' : BoolField,
        'usegerberattributes' : BoolField,
        'usegerberadvancedattributes' : BoolField,
        'creategerberjobfile' : BoolField,
        'excludeedgelayer' : BoolField,
        'plotframeref' : BoolField,
        'viasonmask' : BoolField,
        'useauxorigin' : BoolField,
        'psnegative' : BoolField,
        'psa4output' : BoolField,
        'plotreference' : BoolField,
        'plotvalue' : BoolField,
        'plotinvisibletext' : BoolField,
        'padsonsilk' : BoolField,
        'subtractmaskfromsilk' : BoolField,
        'mirror' : BoolField,
        'linewidth' : DistanceField,
        'hpglpendiameter' : DistanceField,
        'outputformat' : IntField,
        'drillshape' : IntField,
        'scaleselection' : IntField,
        'mode' : IntField,
        'hpglpennumber' : IntField,
        'hpglpenspeed' : IntField,
        'outputdirectory' : StringField,
        'layerselection' : LayerSelectionField
        }

class Setup(Loadable):
    fields = {
            'last_trace_width' : DistanceField,
            'trace_clearance' : DistanceField,
            'zone_clearance' : DistanceField,
            'trace_min' : DistanceField,
            'segment_width' : DistanceField,
            'edge_width' : DistanceField,
            'via_size' : DistanceField,
            'via_drill' : DistanceField,
            'via_min_size' : DistanceField,
            'via_min_drill' : DistanceField,
            'uvia_size' : DistanceField,
            'uvia_drill' : DistanceField,
            'uvia_min_size' : DistanceField,
            'uvia_min_drill' : DistanceField,
            'pcb_text_width' : DistanceField,
            'mod_edge_width' : DistanceField,
            'mod_text_width' : DistanceField,
            'pad_drill' : DistanceField,
            'pad_to_mask_clearance' : DistanceField,
            'mod_text_size' : SizeField,
            'pad_size' : SizeField,
            'pcb_text_size' : SizeField,
            'aux_axis_origin' : SizeField,
            'grid_origin' : SizeField,
            'uvias_allowed' : BoolField,
            'zone_45_only' : BoolField,
            'visible_elements' : HexField,
            'pcbplotparams' : ClassField(PlotParams)
            }


class netClass(Loadable):
    nets = []
    fields = {
            'clearance' : DistanceField,
            'trace_width' : DistanceField,
            'via_dia' : DistanceField,
            'via_drill' : DistanceField,
            'uvia_dia' : DistanceField,
            'uvia_drill' : DistanceField,
            'add_net' : NetArrayField
            }

    def loadS(self, s):
        self.name = s.items[0]
        self.descr = s.items[1]
        self.loadFields(s.items[2:])

class Effects(Loadable):
    fields = {
            'font' : FontField,
            'justify' : FlagField
            }


class Text(Loadable):
    fields = {
            'at' : PosField,
            'layer' : StringField,
            'effects' : ClassField(Effects)
            }
    def loadS(self, s):
        self.key = s.name
        i = 1
        if s.name == 'fp_text':
            self.t = s.items[0]
            i += 1
        self.text = s.items[i]
        self.loadFields(s.items[i:])


class Line(Loadable):
    fields = {
            'start' : PosField,
            'end' : PosField,
            'width' : DistanceField,
            'layer' : StringField,
            'net' : StringField,
            'tstamp' : HexField
            }
    def loadS(self, s):
        self.key = s.name
        self.loadFields(s.items)


class Circle(Loadable):
    fields = {
            'center' : PosField,
            'start' : PosField, #TODO alias, center is for circle star tis for arc - meand same thing?
            'end' : PosField,
            'width' : DistanceField,
            'layer' : StringField,
            'angle' : FloatField
            }
    def loadS(self, s):
        self.t = s.name
        self.loadFields(s.items)
    angle = 360

class Pad(Loadable):
    fields = {
            'at' : PosField,
            'size' : SizeField,
            'drill' : DistanceField,
            'layers' : FlagField,
            'net' : NetField,
            }
    def loadS(self, s):
        self.name = s.items[0]
        self.t = s.items[1]
        self.shape = s.items[2]
        self.loadFields(s.items[3:])
    pass

class Via(Loadable):
    fields = {
            'at' : PosField,
            'size' : DistanceField,
            'drill' : DistanceField,
            'layers' : FlagField,
            'net' : IntField
            }

class Model(Loadable):
    fields = {
            'at' : Pos3DField,
            'scale' : Pos3DField,
            'rotate' : Pos3DField
            }
    def loadS(self, s):
        self.path = s.items[0]
        self.loadFields(s.items[1:])

class Module(Loadable):
    fields = {
            'tedit' : HexField,
            'tstamp' : HexField,
            'at' : PosField,
            'fp_text' : ArrayField(Text, 'texts'),
            'fp_line' : ArrayField(Line, 'lines'),
            'fp_circle' : ArrayField(Circle, 'circles'),
            'fp_arc' : ArrayField(Circle, 'circles'),
            'pad' : ArrayField(Pad, 'pads'),
            'model' : ClassField(Model),
            'attr' : StringField,
            'layer' : StringField,
            'descr' : StringField,
            'tags' : StringField,
            'path' : StringField,
            }

    texts = []
    lines = []
    pads = []
    circles = []
    def loadS(self, s):
        self.name = s.items[0]
        self.loadFields(s.items[1:])

class Fill(Loadable):
    fields = {
                'arc_segments': IntField,
                'thermal_gap': DistanceField,
                'smoothing': StringField,
                'thermal_bridge_width': DistanceField,
                'radius': DistanceField
            }

class Zone(Loadable):
    fields = {
            'net': IntField,
            'net_name': StringField,
            'timestamp': HexField,
            'hatch' : HatchField,
            'connect_pads' : ConnectField,
            'min_thickness' : DistanceField,
            'keepout' : KeepoutsField,
            'fill' : ClassField(Fill),
            'polygon' : PointsField,
            'layer' : StringField,
            'tstamp' : HexField
            }
    pts = []

class Kicad(Loadable):
    fields = {
            'version' : StringField,
            'host' : StringField,
            'general' : ClassField(General),
            'version' : StringField,
            'page' : StringField,
            'layers' : LayersField,
            'setup' : ClassField(Setup),
            'net':  NetsField,
            'net_class': ArrayField(netClass, 'classes'),
            'module': ArrayField(Module, 'modules'),
            'gr_arc': ClassField(Circle),
            'gr_circle': ArrayField(Circle, 'circles'),
            'gr_line': ArrayField(Line, 'lines'),
            'segment': ArrayField(Line, 'lines'),
            'gr_text': ArrayField(Text, 'texts'),
            'via': ArrayField(Via, 'vias'),
            'zone': ArrayField(Zone, 'zones')
    }
    nets = {}
    classes = []
    modules = []
    circles = []
    lines = []
    texts = []
    vias = []
    zones = []
    def toS(self):
        return S('kicad_pcb', [])
    def loadS(self, s):
        if s.name != 'kicad_pcb':
            raise Exception('Unknown format')
        self.loadFields(s.items)



s = load('kicadtest.kicad_pcb')
pcb = Kicad()
pcb.loadS(s)
print(pcb.layers)
#pcb = loadPcb(a)
#s = pcb.toS()
#save('exp.kicad_pcb', s)

