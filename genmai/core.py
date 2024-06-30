import iroh

from .blobs import Blobs
from .collections import Collections

class Genmai(object):
    def __init__(self, node: iroh.IrohNode):
        self.node = node
        self.blobs = Blobs(self)
        self.collections = Collections(self)

    class AddCallback(iroh.AddCallback):
        def __init__(self):
            self._status = None
            self._result = {}

        @property
        def success(self):
            return self._status == iroh.AddProgressType.ALL_DONE

        @property
        def result(self):
            return self._result

        def progress(self, progress: iroh.AddProgress):
            self._status = progress.type()
            if self._status == iroh.AddProgressType.FOUND:
                p = progress.as_found()
                self._result[p.id] = {'name': p.name, 'size': p.size}
            elif self._status == iroh.AddProgressType.PROGRESS:
                p = progress.as_progress()
                self._result[p.id]['offset'] = p.offset
            elif self._status == iroh.AddProgressType.DONE:
                p = progress.as_done()
                self._result[p.id]['hash'] = p.hash
            elif self._status == iroh.AddProgressType.ALL_DONE:
                p = progress.as_all_done()
                self._result['all'] = {'hash': p.hash, 'format': p.format, 'tag': p.tag}
            elif self._status == iroh.AddProgressType.ABORT:
                p = progress.as_abort()
                self._result['error'] = p.error
            else:
                self._result['error'] = f"Unknown event adding blob: {self._status}"


