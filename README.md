# geda2kicad
Converts [gEDA PCB](http://pcb.geda-project.org/) files to [KiCAD PCB](http://kicad-pcb.org/). It needs only pure python, it does not need gEDA PCB or KiCAD to run. 
It can also load KiCAD and save gEDA so conversion in oposite direction can come in the future.

## What works
- graphics elemetns
- traces
- vias
- footprints (creates fab layer by copying silk)
- netlist
- polygons with holes

## Limitations

It is a work in progres and it was tested only on few boards. There are probably lots of boards which won't work now.

- It was tested only on two side boards with delault layer naming
- It completly ignores thermals as KiCAD is usig completly different logic for zones/polygons
- It does not support burried vias
- Components are exported with zero rotation (rotated components have different footprint), if you swap exported footpritns for library ones you would need to ratate them
- Netlis does not associate net classes
- Circles are exported as arcs (same as drawn in gEDA)
- Exported zones (polygons in gEDA) does not have associated net
- Arcs on copper layers (KiCAD does not support it)
- Placement of text is sometimes different

## Usage

`python pcb2kicad somefile.pcb`

or

`python pcb2kicad somefile.pcb output.kicad_pcb`
