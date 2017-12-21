from itertools import islice

def read(filename):
    m = Midi()
    m.read_from_file(filename)
    return m

toInt = lambda bs: int.from_bytes(bs, 'big')

class Midi:
    def __init__(self):
        self.format_type = 0
        self.number_of_track = 0
        self.time_division = 0
        self.tracks = []
    def read_header(self, f):
        bChunkId = f.read(4)
        if bChunkId != b'MThd':
            raise Exception("Chunk is not a header")
        bChunkSize = f.read(4)
        bFormatType = f.read(2)
        self.format_type = toInt(bFormatType)
        bNumberOfTrack = f.read(2)
        self.number_of_track = toInt(bNumberOfTrack)
        bTimeDivision = f.read(2)
        self.time_division = toInt(bTimeDivision)
    def read_track(self, f):
        bChunkId = f.read(4)
        if bChunkId != b'MTrk':
            raise Exception("Chunk is not a track")
        bChunkSize = f.read(4)
        chunkSize = toInt(bChunkSize)
        data = f.read(chunkSize)
        self.tracks.append(Track(data))
    def read_from_file(self, filename):
        with open(filename, "rb") as f:
            self.read_header(f)
            for i in range(self.number_of_track):
                self.read_track(f)

def read_variable_length(bs):
    val = 0
    for i in range(4):
        b = next(bs)
        val = (val << 7) | b & 0x7F
        if b < 0x80:
            break
    return val
    
read_delta_time = read_variable_length

def read_event(bs):
    typ = next(bs)
    if typ < 0xF0:
        return read_midi_event(typ, bs)
    if typ == 0xFF:
        return read_meta_event(bs)
    raise Exception("unknown event type found: {0}".format(typ))

def read_midi_event(typ, bs):
    if typ & 0xF0 == 0x80:
        k = next(bs)
        v = next(bs)
        return ("note_off", k, v)
    if typ & 0xF0 == 0x90:
        k = next(bs)
        v = next(bs)
        return ("note_on", k, v)
    if typ & 0xF0 == 0xB0:
        c = next(bs)
        d = next(bs)
        return ("control_change", c, d)
    raise Exception("unknown midi-event type found: {0}".format(typ))

def take(n, bs):
    return bytes(islice(bs, n))

def read_meta_event(bs):
    typ = next(bs)
    l = read_variable_length(bs)
    return ("meta", hex(typ), take(l, bs))

def read_track_event(bs):
    dt = read_delta_time(bs)
    ev = read_event(bs)
    return (dt, ev)

class Track:
    def __init__(self, data):
        self.data = data
        self.events = []
        self.set_data()
    def set_data(self):
        it = iter(self.data)
        try:
            while True:
                ev = read_track_event(it)
                self.events.append(ev)
        except StopIteration:
            pass
