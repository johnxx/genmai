import os
from genmai import Genmai
import iroh

current_dir = os.path.dirname(os.path.abspath(__file__))
iroh_node = iroh.IrohNode('./iroh-data')
g = Genmai(iroh_node)
some_dict = {
    'foo': b'bar',
    'baz': b'qux',
    'gronk': b'frony',
    'froonk': 'fleep',
    'blonk': b'bloop'
}

d1 = g.docs.create('test')