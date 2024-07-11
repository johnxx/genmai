import os
import asyncio
from genmai import Genmai
import iroh


async def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    iroh_node = await iroh.IrohNode.persistent('./iroh-data')
    g = Genmai(iroh_node)

    d1 = await g.docs.create()
    await d1.set_bytes('foo', b'bar')
    await d1.set_bytes('baz', b'qux')
    await d1.set_bytes('gronk', b'frony')
    async for key, entry in d1.items():
        val = await entry.to_bytes()
        print(f"{key}: {val}")

    some_dict = {
        'foo': b'bar',
        'baz': b'qux',
        'gronk': b'frony',
        'froonk': b'fleep',
        'blonk': b'bloop'
    }
    d2 = await g.docs.create_from_bytes(some_dict)
    async for key, entry in d2.items():
        val = await entry.to_bytes()
        print(f"{key}: {val}")

if __name__ == '__main__':
    asyncio.run(main())
