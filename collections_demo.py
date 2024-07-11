import asyncio
import os
from genmai import Genmai
import iroh


async def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    iroh_node = await iroh.IrohNode.persistent('./iroh-data')
    g = Genmai(iroh_node)
    some_bytes = {
        'alf': b'alf',
        'foo': b'foo',
        'bar': b'bar',
        'baz': b'baz',
        'gronk': b'gronk',
        'frony': b'frony',
    }

    c = await g.collections.create_from_dict(some_bytes, 'honk')

    await c.save()
    d = await g.collections.get('honk')

    for key, val in d.links.items():
        bytes_in = some_bytes[key]
        bytes_out = await d[key].to_bytes()
        print(f"{key}: {bytes_in} => {bytes_out}")


if __name__ == '__main__':
    asyncio.run(main())
