def load(filename):
    with open(filename) as f:
        r = {}
        for line in  f.readlines():
            cells = line.split(',')
            if len(cells) < 5:
                raise(Exception('not enaugh fields for ' + cells[0]))
            r[cells[0]] = list(map(lambda x : x.strip(), cells[1:]))
        return r
