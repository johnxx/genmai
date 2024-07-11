import iroh


class Authors(object):
    def __init__(self, node: iroh.IrohNode):
        self._node = node

    def create(self):
        return Author(self._node, self._node.author_create())

    async def list(self):
        for author in await self._node.author_list():
            yield Author(self._node, author)

    def __getitem__(self, author_id: str or iroh.AuthorId):
        return Author(self._node, author_id)

    async def len(self):
        return await self._node.author_list()

    @property
    def default(self):
        return Author(self._node, self._node.author_default())


class Author(object):
    def __init__(self, node: iroh.IrohNode, author_id: str or iroh.AuthorId):
        self._node = node
        if not isinstance(author_id, iroh.AuthorId):
            author_id = iroh.AuthorId.from_string(author_id)
        self._author = author_id

    @property
    def id(self):
        return self._author

    def __str__(self):
        return str(self._author)
