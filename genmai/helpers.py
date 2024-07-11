import iroh


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

    async def progress(self, progress: iroh.AddProgress):
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


class SubscribeCallback(iroh.SubscribeCallback):
    async def event(self, event: iroh.LiveEvent):
        event_type = event.type()
        # Event types: INSERT_LOCAL, INSERT_REMOTE, CONTENT_READY, NEIGHBOR_UP, NEIGHBOR_DOWN
        # SYNC_FINISHED, PENDING_CONTENT_READY
        if event_type == iroh.LiveEventType.INSERT_LOCAL:
            entry = event.as_insert_local()
        elif event_type == iroh.LiveEventType.INSERT_REMOTE:
            insert_remote = event.as_insert_remote()
        elif event_type == iroh.LiveEventType.CONTENT_READY:
            hash_val = event.as_content_ready()
        elif event_type == iroh.LiveEventType.NEIGHBOR_UP:
            pub_key = event.as_neighbor_up()
        elif event_type == iroh.LiveEventType.NEIGHBOR_DOWN:
            pub_key = event.as_neighbor_down()
        elif event_type == iroh.LiveEventType.SYNC_FINISHED:
            sync_event = event.as_sync_finished()
        else:
            raise Exception(f"Unknown event type: {event_type}")


def ensure_bytes(text):
    if isinstance(text, bytes):
        return text
    if isinstance(text, str):
        return text.encode('utf8')
    raise TypeError('Cannot convert {} type into bytes'.format(type(text)))

