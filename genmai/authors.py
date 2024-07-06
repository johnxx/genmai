import iroh


class Authors(object):
    def __init__(self, node: iroh.IrohNode):
        self._node = node

    def create(self):
        return Author(self._node, self._node.author_create())

    def __iter__(self):
        for author in self._node.author_list():
            yield Author(self._node, author)

    def __getitem__(self, author_id: str or iroh.AuthorId):
        return Author(self._node, author_id)

    def __len__(self):
        return len(self._node.author_list())

    @property
    def default(self):
        return Author(self._node, self._node.author_default())


class Author(object):
    def __init__(self, node: iroh.IrohNode, author_id: str or iroh.AuthorId):
        self._node = node
        self._author = iroh.Author.from_string(author_id)

    @property
    def id(self):
        return self._author

    def __str__(self):
        return str(self._author)
