import os
from genmai import Genmai
import iroh

current_dir = os.path.dirname(os.path.abspath(__file__))
iroh_node = iroh.IrohNode('./iroh-data')
g = Genmai(iroh_node)
some_bytes = {
    'alf': b'alf',
    'foo': b'foo',
    'bar': b'bar',
    'baz': b'baz',
    'gronk': b'gronk',
    'frony': b'frony',
}

c = g.collections.create_from_dict(some_bytes, 'honk')

c.save()
d = g.collections['honk']

for key, val in d.links.items():
    bytes_in = some_bytes[key]
    bytes_out = d[key].to_bytes()
    # print(f"{key}: {bytes_in} => {bytes_out}")
