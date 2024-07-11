import iroh

from .authors import Authors
from .blobs import Blobs
from .collections import Collections
from .docs import Docs


class Genmai(object):
    def __init__(self, node: iroh.IrohNode):
        self._node = node
        self.authors = Authors(self._node)
        self.blobs = Blobs(self._node)
        self.collections = Collections(self._node)
        self.docs = Docs(self._node)

    @property
    def id(self):
        return self._node.node_id()
