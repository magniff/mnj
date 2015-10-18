from __future__ import print_function

from six import with_metaclass

from mnj.base import BaseDoc, SortedDict
from mnj.compat import OrderedDict, ChainMap
from mnj.doc_registry import doc_registry


__all__ = ['d']


class DocMeta(type):

    meta_defaults = {
        'sorted': False,
        'magic': False,
        'class_name': None,  # actual class name is used by default
    }

    def __new__(cls, name, bases, attrs):

        # process meta
        meta = ChainMap(
            attrs.pop('meta', {}),
            {'class_name': name},
            cls.meta_defaults,
        )

        # prepare bases for modification
        bases = list(bases)

        # is sorted
        if meta['sorted']:
            if OrderedDict in bases:
                bases[bases.index(OrderedDict)] = SortedDict
            else:
                bases.append(SortedDict)

        # is magic (keep this section last)
        if meta['magic']:
            if Doc in bases:
                bases.insert(bases.index(Doc), MagicMixin)
            else:
                bases.append(MagicMixin)
            print(attrs)
            attrs['_cls'] = meta['class_name']
            type_new = type.__new__(cls, name, tuple(bases), attrs)
            doc_registry.register_class(type_new)
            return type_new
        else:
            return type.__new__(cls, name, tuple(bases), attrs)


class MagicMixin(object):
    _allowed_keys = ('_id', '_cls',)
    _cls = None

    def __setattr__(self, name, value):
        if name.startswith('_') and name not in self._allowed_keys:
            super(MagicMixin, self).__setattr__(name, value)
        self[name] = value

    def __getattr__(self, name):
        if name.startswith('_') and name not in self._allowed_keys:
            return self.__getattribute__(name)
        return self[name]


class Doc(with_metaclass(DocMeta, BaseDoc)):
    pass


d = Doc
