import iroh

from .blobs import Blobs
from .collections import Collections
from .docs import Docs


class Genmai(object):
    def __init__(self, node: iroh.IrohNode):
        self._node = node
        self.blobs = Blobs(self._node)
        self.docs = Docs(self._node)
        # No collections for now: See collections_issue.py
        # self.collections = Collections(self)

    @property
    def id(self):
        return self._node.node_id()
