import midi

p = midi.read("bach.mid")
print("Number of Track: {0}".format(p.number_of_track))
for (i, t) in enumerate(p.tracks):
    print("Track {0}: ".format(i))
    for e in t.events:
        print(e)
    print()
