from .blobs import Blob
from .authors import Author
import iroh

from .helpers import ensure_bytes


class Docs(object):
    def __init__(self, node: iroh.IrohNode):
        self._node = node

    def __iter__(self):
        for doc in self._node.doc_list():
            yield Doc(self._node, doc.namespace)

    def __getitem__(self, doc_id: str):
        return Doc(self._node, doc_id)


class Doc(object):
    def __init__(self, node: iroh.IrohNode, doc: iroh.Doc | str):
        self._node = node
        self._doc = doc
        if isinstance(doc, str):
            self._doc = node.doc_open(self._doc)
        if not self._doc:
            raise Exception(f"Doc {self._doc.id} not found")
        self._query_builder = QueryBuilder(self._doc)

    @classmethod
    def create(cls, node: iroh.IrohNode):
        doc = node.doc_create()
        return Doc(node, doc)

    @classmethod
    def join(cls, node: iroh.IrohNode, doc_ticket: str, subscribe: bool = False):
        if subscribe:
            iroh_doc = node.doc_join_and_subscribe(doc_ticket)
        else:
            iroh_doc = node.doc_join(doc_ticket)
        return Doc(node, str(iroh_doc.id()))


class QueryBuilder(object):
    def __init__(self, iroh_doc: iroh.Doc):
        self._iroh_doc = iroh_doc

    @classmethod
    def _to_query_opts(cls, sort_by: str = 'author', order: str = 'asc', offset: int = None, limit: int = None):
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

    def all(self, latest_only: bool = False, sort_by: str = 'author', order: str = 'asc', offset: int = None,
            limit: int = None):
        if latest_only:
            return Query(self._iroh_doc, iroh.Query.single_latest_per_key(self._to_query_opts(sort_by, order, offset, limit)))
        else:
            return Query(self._iroh_doc, iroh.Query.all(self._to_query_opts(sort_by, order, offset, limit)))

    def by_key(self, key: str | bytes, latest_only: bool = False, sort_by: str = 'author', order: str = 'asc',
               offset: int = None, limit: int = None):
        key = ensure_bytes(key)
        if latest_only:
            return Query(self._iroh_doc, iroh.Query.single_latest_per_key_exact(key))
        else:
            return Query(self._iroh_doc, iroh.Query.key_exact(key, self._to_query_opts(sort_by, order, offset, limit)))

    def by_prefix(self, prefix: str | bytes, latest_only: bool = False, sort_by: str = 'author',
                  order: str = 'asc', offset: int = None, limit: int = None):
        prefix = ensure_bytes(prefix)
        if latest_only:
            return Query(self._iroh_doc, iroh.Query.single_latest_per_key_prefix(prefix, self._to_query_opts(sort_by, order, offset, limit)))
        else:
            return Query(self._iroh_doc, iroh.Query.key_prefix(prefix, self._to_query_opts(sort_by, order, offset,
                                                                                           limit)))

    def by_author(self, doc: Doc, author: str | Author, sort_by: str = 'author', order: str = 'asc',
                  offset: int = None, limit: int = None):
        return Query(self._iroh_doc, iroh.Query.author(author.id, self._to_query_opts(sort_by, order, offset, limit)))

    def by_key_author(self, key: str | bytes, author: str | Author):
        key = ensure_bytes(key)
        return Query(self._iroh_doc, iroh.Query.author_key_exact(author.id, key))

    def by_prefix_author(self, prefix: str | bytes, author: str | Author, sort_by: str = 'author',
                         order: str = 'asc', offset: int = None, limit: int = None):
        prefix = ensure_bytes(prefix)
        return Query(self._iroh_doc, iroh.Query.author_key_prefix(author.id, prefix, self._to_query_opts(sort_by, order, offset, limit)))


class Query(object):
    def __init__(self, iroh_doc: iroh.Doc, query: iroh.Query):
        self._iroh_doc = iroh_doc
        self._query = query

    def one(self):
        return self._iroh_doc.get_one(self._query)

    def __iter__(self):
        for entry in self._iroh_doc.get_many(self._query):
            yield entry



