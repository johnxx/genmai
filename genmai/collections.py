from helpers import ensure_bytes
from .core import Genmai
from .blobs import Blob
import iroh


class Collections(object):
    def __init__(self, genmai: Genmai):
        self._genmai = genmai

    def __getitem__(self, name):
        name = ensure_bytes(name)
        collections = self._genmai.node.blobs_list_collections()
        for collection_info in collections:
            if collection_info.tag == name:
                return Collection(self._genmai, collection_info.hash)

    def __len__(self):
        return len(self._genmai.node.blobs_list_collections())

    def create_from_blobs(self, blobs: {Blob}, name: str or bytes | None = None):
        return Collection.from_blobs(self._genmai, blobs, name)

    def delete(self, name):
        name = ensure_bytes(name)
        self._genmai.node.tags_delete(name)


class Collection(object):
    def __init__(self, genmai: Genmai, hash_val: str | iroh.Hash | None = None):
        self._genmai = genmai
        if not hash_val:
            self._collection = iroh.Collection()
        else:
            if not isinstance(hash_val, iroh.Hash):
                hash_val = iroh.Hash.from_string(hash_val)
            self._collection = genmai.node.blobs_get_collection(hash_val)
        self._name = None

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
    def from_blobs(cls, genmai: Genmai, blobs: {Blob}, name: str or bytes | None = None):
        collection = Collection(genmai, None)
        for k, v in blobs.items():
            collection.add_blob(k, v)
        collection.name = name
        return collection

    @property
    def links(self):
        res = self._collection.blobs()
        links = {}
        for ln in res:
            out = Blob(self._genmai, ln.link).to_bytes()
            print(f"name: {ln.name}, link: {out}")
            links[ln.name] = Blob(self._genmai, ln.link)
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

    def save(self):
        if not self.name:
            tag = iroh.SetTagOption.auto()
        else:
            tag = iroh.SetTagOption.named(self.name)
        th = self._genmai.node.blobs_create_collection(self._collection, tag, [])
        return th.tag, th.hash
