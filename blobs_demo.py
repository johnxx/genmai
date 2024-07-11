import os
from genmai import Genmai
import iroh
import asyncio


async def main():
    iroh.iroh_ffi.uniffi_set_event_loop(asyncio.get_running_loop())
    current_dir = os.path.dirname(os.path.abspath(__file__))
    iroh_node = await iroh.IrohNode.persistent('./iroh-data')
    g = Genmai(iroh_node)
    with open('test.txt', 'w') as f:
        f.write('honk')
    b1 = await g.blobs.create_from_file('test.txt')
    b2 = await g.blobs.create_from_bytes(await b1.to_bytes())
    p1 = 'out.txt'
    await b2.to_file(p1)
    b3 = await g.blobs.create_from_file(p1)
    b4 = await g.blobs.create_from_bytes(await b3.to_bytes(offset=0, length=await b3.size))
    assert await b4.to_bytes() == await b1.to_bytes()
    # assert len(g.blobs) == 1
    async for key, val in g.blobs.items():
        contents = await val.to_bytes()
        print(f"{key}: {contents}")

if __name__ == '__main__':
    asyncio.run(main())
