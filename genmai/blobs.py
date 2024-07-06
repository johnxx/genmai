from .helpers import AddCallback, ensure_bytes

import iroh
import os


class Blobs(object):
    def __init__(self, node: iroh.IrohNode):
        self._node = node

    def __getitem__(self, hash_val):
        return Blob(self._node, hash_val)

    def items(self):
        for h in self._node.blobs_list():
            yield str(h), self[h]

    def __len__(self):
        return len(self._node.blobs_list())

    def create_from_file(self, *args, **kwargs):
        return Blob.from_file(self._node, *args, **kwargs)

    def create_from_bytes(self, *args, **kwargs):
        return Blob.from_bytes(self._node, *args, **kwargs)


class Blob(object):
    def __init__(self, node, hash_val: str or iroh.Hash):
        self._node = node
        if not isinstance(hash_val, iroh.Hash):
            hash_val = iroh.Hash.from_string(hash_val)
        self.size = self._node.blobs_size(hash_val)
        self.hash = hash_val

    @classmethod
    def from_file(cls, node, path, collection_tag=None, wrap=None):
        if not collection_tag:
            collection_tag = iroh.SetTagOption.auto()
        elif isinstance(collection_tag, str or bytes):
            collection_tag = ensure_bytes(collection_tag)
            collection_tag = iroh.SetTagOption.named(collection_tag)
        else:
            raise Exception(f"Unknown collection tag format: {collection_tag}")

        if not wrap:
            wrap = iroh.WrapOption.no_wrap()
        elif isinstance(wrap, str):
            wrap = iroh.WrapOption.wrap(wrap)

        add_progress = AddCallback()
        node.blobs_add_from_path(os.path.realpath(path), in_place=False, tag=collection_tag, wrap=wrap,
                                 cb=add_progress)
        if not add_progress.success:
            raise Exception(add_progress.result['error'])
        return cls(node, add_progress.result['all']['hash'])

    @classmethod
    def from_bytes(cls, node, data):
        result = node.blobs_add_bytes(data)
        return cls(node, result.hash)

    def to_file(self, path, export_format='blob', export_mode='copy'):
        if export_format == 'blob':
            export_format = iroh.BlobExportFormat.BLOB
        elif export_format == 'collection':
            export_format = iroh.BlobExportFormat.COLLECTION
        else:
            raise Exception(f"Unknown export format: {export_format}")

        if export_mode == 'copy':
            export_mode = iroh.BlobExportMode.COPY
        elif export_mode == 'try_reference':
            export_mode = iroh.BlobExportMode.TRY_REFERENCE
        else:
            raise Exception(f"Unknown export mode: {export_mode}")

        self._node.blobs_export(self.hash, os.path.realpath(path), export_format, export_mode)

    def to_bytes(self, offset=0, length=None):
        if offset == 0 and length is None:
            return self._node.blobs_read_to_bytes(self.hash)
        elif offset > 0 or length <= self.size:
            return self._node.blobs_read_at_to_bytes(self.hash, offset, length)
        else:
            raise Exception("Invalid offset or length")

    def __len__(self):
        return self.size

    def __del__(self):
        self._node.blobs_delete_blob(self.hash)

    def share(self, blob_format='raw', ticket_options='relay_and_addresses'):
        if blob_format == 'raw':
            blob_format = iroh.BlobFormat.RAW
        elif blob_format == 'hash_seq':
            blob_format = iroh.BlobFormat.HASH_SEQ
        else:
            raise Exception(f"Unknown blob format: {blob_format}")

        if ticket_options == 'relay_and_addresses':
            ticket_options = iroh.AddrInfoOptions.RELAY_AND_ADDRESSES
        elif ticket_options == 'relay':
            ticket_options = iroh.AddrInfoOptions.RELAY
        elif ticket_options == 'addresses':
            ticket_options = iroh.AddrInfoOptions.ADDRESSES
        else:
            raise Exception(f"Unknown ticket options: {ticket_options}")

        return self._node.blobs_share(self.hash, blob_format, ticket_options)
