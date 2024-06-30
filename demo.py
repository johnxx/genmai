import os
from genmai import Genmai
import iroh

current_dir = os.path.dirname(os.path.abspath(__file__))
iroh_node = iroh.IrohNode('./iroh-data')
g = Genmai(iroh_node)
with open('test.txt', 'w') as f:
    f.write('honk')
b1 = g.blobs.create_from_file('test.txt')
b2 = g.blobs.create_from_bytes(b1.to_bytes())
p1 = 'out.txt'
b2.to_file(p1)
b3 = g.blobs.create_from_file(p1)
b4 = g.blobs.create_from_bytes(b3.to_bytes(offset=0, length=len(b3)))
assert b4.to_bytes() == b1.to_bytes()
# assert len(g.blobs) == 1
for key, val in g.blobs.items():
    contents = val.to_bytes()
    print(f"{key}: {contents}")

blobbies = {
    'alf': g.blobs.create_from_bytes(b'fleep'),
    'foo': g.blobs.create_from_file('test.txt'),
    'bar': g.blobs.create_from_bytes(b'baz'),
    'baz': g.blobs.create_from_bytes(b'qux'),
    'gronk': g.blobs.create_from_bytes(b'gronk')
}
c = g.collections.create_from_blobs(blobbies, 'test')
assert len(c) == 5
c.save()
assert len(g.collections) == 1
c = g.collections['test']
assert len(c) == 5
for key, val in blobbies.items():
    bytes_in = blobbies[key].to_bytes()
    bytes_out = c[key].to_bytes()
    print(f"{key}: {bytes_in} => {bytes_out}")
