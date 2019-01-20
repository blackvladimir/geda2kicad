def load(filename):
    with open(filename) as f:
        r = {}
        for line in  f.readlines():
            cells = line.split(',')
            r[cells[0]] = list(map(lambda x : x.strip(), cells[1:]))
        return r
