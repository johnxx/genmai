from .helpers import ensure_bytes
from .blobs import Blob
import iroh


class Collections(object):
    def __init__(self, node):
        self._node = node

    async def get(self, name):
        name = ensure_bytes(name)
        collections = await self._node.blobs_list_collections()
        for collection_info in collections:
            if collection_info.tag == name:
                return await Collection.open(self._node, collection_info.hash)

    def __len__(self):
        return len(self._node.blobs_list_collections())

    def create_from_dict(self, bytes_dict: {str: bytes}, name: str or bytes | None = None):
        return Collection.from_dict(self._node, bytes_dict, name)

    def create_from_blobs(self, blobs: {Blob}, name: str or bytes | None = None):
        return Collection.from_blobs(self._node, blobs, name)

    def delete(self, name):
        name = ensure_bytes(name)
        self._node.tags_delete(name)


class Collection(object):
    def __init__(self, node, collection: iroh.Collection):
        self._node = node
        self._collection = collection
        self._name = None

    @classmethod
    def create(cls, node):
        _collection = iroh.Collection()
        return cls(node, _collection)

    @classmethod
    async def open(cls, node, hash_val: str | iroh.Hash):
        if not isinstance(hash_val, iroh.Hash):
            hash_val = iroh.Hash.from_string(hash_val)
        _collection = await node.blobs_get_collection(hash_val)
        return cls(node, _collection)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name: str | bytes | None):
        if not name:
            self._name = None
        else:
            self._name = ensure_bytes(name)

    @classmethod
    async def from_dict(cls, node, bytes_dict: {str: bytes}, name: str or bytes | None = None):
        collection = Collection.create(node)
        for k, v in bytes_dict.items():
            collection.add_blob(k, await Blob.from_bytes(node, v))
        collection.name = name
        return collection

    @classmethod
    def from_blobs(cls, node, blobs: {Blob}, name: str or bytes | None = None):
        collection = Collection.create(node)
        for k, v in blobs.items():
            collection.add_blob(k, v)
        collection.name = name
        return collection

    @property
    def links(self):
        res = self._collection.blobs()
        links = {}
        for ln in res:
            # out = await Blob(self._node, ln.link).to_bytes()
            # print(f"name: {ln.name}, link: {out}")
            links[ln.name] = Blob(self._node, ln.link)
        return links

    def add_blob(self, name: str, blob: Blob):
        self.add_hash(name, blob.hash)

    def add_hash(self, name: str, hash_val: str or iroh.Hash):
        if isinstance(hash_val, str):
            hash_val = iroh.Hash.from_string(hash_val)
        self._collection.push(name, hash_val)

    def __len__(self):
        return self._collection.len()

    def __getitem__(self, name):
        return self.links[name]

    async def save(self):
        if not self.name:
            tag = iroh.SetTagOption.auto()
        else:
            tag = iroh.SetTagOption.named(self.name)
        th = await self._node.blobs_create_collection(self._collection, tag, [])
        return th.tag, th.hash
