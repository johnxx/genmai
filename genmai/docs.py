from .blobs import Blob
from .authors import Author
import iroh

from .helpers import ensure_bytes, SubscribeCallback


class Docs(object):
    def __init__(self, node: iroh.IrohNode):
        self._node = node

    async def items(self):
        for doc in await self._node.doc_list():
            yield doc.namespace, await Doc.open(self._node, doc.namespace)

    async def get(self, doc_id: str):
        return await Doc.open(self._node, doc_id)

    async def create(self):
        return await Doc.create(self._node)

    async def create_from_bytes(self, bytes_dict: {str | bytes: bytes}):
        return await Doc.from_bytes(self._node, bytes_dict)


class Doc(object):
    def __init__(self, node: iroh.IrohNode, doc: iroh.Doc):
        self._node = node
        self._doc = doc
        if not self._doc:
            raise Exception(f"Invalid doc: {doc}")
        self.query = QueryBuilder(self._doc)

    async def set_bytes(self, key: str | bytes, value: bytes, author: str | Author = None):
        if not author:
            author = Author(self._node, await self._node.author_default())
        if isinstance(author, str):
            author = Author(self._node, author)
        key = ensure_bytes(key)
        await self._doc.set_bytes(author.id, key, value)

    async def set_blob(self, key: str | bytes, blob: Blob, author: str | Author = None):
        if not author:
            author = self._node.author_default()
        if isinstance(author, str):
            author = Author(self._node, author)
        key = ensure_bytes(key)
        await self._doc.set_hash(author.id, key, blob.hash, await blob.size)

    @classmethod
    async def open(cls, node: iroh.IrohNode, doc_id: str):
        doc = await node.doc_open(doc_id)
        return Doc(node, doc)

    @classmethod
    async def create(cls, node: iroh.IrohNode):
        _doc = await node.doc_create()
        return Doc(node, _doc)

    @classmethod
    async def from_bytes(cls, node: iroh.IrohNode, bytes_dict: {str | bytes: bytes}):
        _doc = await node.doc_create()
        doc = Doc(node, _doc)
        for k, v in bytes_dict.items():
            await doc.set_bytes(k, v)
        return doc

    @classmethod
    async def join(cls, node: iroh.IrohNode, doc_ticket: str, subscribe: bool = False):
        if subscribe:
            iroh_doc = node.doc_join_and_subscribe(doc_ticket, cb=SubscribeCallback())
        else:
            iroh_doc = await node.doc_join(doc_ticket)
        return Doc.open(node, str(iroh_doc.id()))

    def items(self):
        return self.query.all().many()


class QueryBuilder(object):
    def __init__(self, iroh_doc: iroh.Doc):
        self._iroh_doc = iroh_doc

    @classmethod
    def _to_query_opts(cls, sort_by: str = 'author', order: str = 'asc', offset: int = 0, limit: int = 0):
        if sort_by == 'author':
            sort_by = iroh.SortBy.AUTHOR_KEY
        elif sort_by == 'key':
            sort_by = iroh.SortBy.KEY_AUTHOR
        else:
            raise Exception(f"Unknown sort_by: {sort_by}")

        if order == 'asc':
            order = iroh.SortDirection.ASC
        elif order == 'desc':
            order = iroh.SortDirection.DESC
        else:
            raise Exception(f"Unknown order: {order}")

        return iroh.QueryOptions(sort_by=sort_by, direction=order, offset=offset, limit=limit)

    def all(self, latest_only: bool = False, sort_by: str = 'author', order: str = 'asc', offset: int = 0,
            limit: int = 0):
        if latest_only:
            return Query(self._iroh_doc, iroh.Query.single_latest_per_key(self._to_query_opts(sort_by, order, offset, limit)))
        else:
            return Query(self._iroh_doc, iroh.Query.all(self._to_query_opts(sort_by, order, offset, limit)))

    def by_key(self, key: str | bytes, latest_only: bool = False, sort_by: str = 'author', order: str = 'asc',
               offset: int = 0, limit: int = 0):
        key = ensure_bytes(key)
        if latest_only:
            return Query(self._iroh_doc, iroh.Query.single_latest_per_key_exact(key))
        else:
            return Query(self._iroh_doc, iroh.Query.key_exact(key, self._to_query_opts(sort_by, order, offset, limit)))

    def by_prefix(self, prefix: str | bytes, latest_only: bool = False, sort_by: str = 'author',
                  order: str = 'asc', offset: int = 0, limit: int = 0):
        prefix = ensure_bytes(prefix)
        if latest_only:
            return Query(self._iroh_doc, iroh.Query.single_latest_per_key_prefix(prefix, self._to_query_opts(sort_by, order, offset, limit)))
        else:
            return Query(self._iroh_doc, iroh.Query.key_prefix(prefix, self._to_query_opts(sort_by, order, offset,
                                                                                           limit)))

    def by_author(self, author: str | Author, sort_by: str = 'author', order: str = 'asc',
                  offset: int = 0, limit: int = 0):
        return Query(self._iroh_doc, iroh.Query.author(author.id, self._to_query_opts(sort_by, order, offset, limit)))

    def by_key_author(self, key: str | bytes, author: str | Author):
        key = ensure_bytes(key)
        return Query(self._iroh_doc, iroh.Query.author_key_exact(author.id, key))

    def by_prefix_author(self, prefix: str | bytes, author: str | Author, sort_by: str = 'author',
                         order: str = 'asc', offset: int = 0, limit: int = 0):
        prefix = ensure_bytes(prefix)
        return Query(self._iroh_doc, iroh.Query.author_key_prefix(author.id, prefix, self._to_query_opts(sort_by, order, offset, limit)))


class Query(object):
    def __init__(self, iroh_doc: iroh.Doc, query: iroh.Query):
        self._iroh_doc = iroh_doc
        self._query = query

    async def one(self):
        entry = await self._iroh_doc.get_one(self._query)
        entry = Entry(self._iroh_doc, entry)
        return entry.key, entry

    async def many(self):
        for entry in await self._iroh_doc.get_many(self._query):
            entry = Entry(self._iroh_doc, entry)
            yield entry.key, entry


class Entry(object):
    def __init__(self, doc: Doc, entry: iroh.Entry):
        self._doc = doc
        self._entry = entry

    @property
    def key(self):
        return self._entry.key()

    @property
    def author(self):
        return Author(self._doc._node, self._entry.author())

    @property
    def timestamp(self):
        return self._entry.timestamp()

    @property
    def size(self):
        return self._entry.content_len()

    async def to_bytes(self):
        return await self._entry.content_bytes(self._doc)

    def to_blob(self):
        return Blob(self._doc._node, self._entry.content_hash())
