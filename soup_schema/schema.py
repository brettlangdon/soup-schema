from bs4 import BeautifulSoup

from .selector import Selector


class Schema(object):
    __version__ = 1

    @classmethod
    def _get_selectors(cls):
        for name, value in cls.__dict__.items():
            if isinstance(value, Selector):
                yield name, value

    @classmethod
    def parse(cls, html):
        instance = cls()
        soup = BeautifulSoup(html, 'html.parser')
        for name, value in cls._get_selectors():
            setattr(instance, name, value.resolve(soup))
        return instance

    def __repr__(self):
        properties = []
        for name, _ in self.__class__._get_selectors():
            value = getattr(self, name, None)
            properties.append('{name}={value}'.format(name=name, value=value))
        return (
            '{name}({properties})'
            .format(name=self.__class__.__name__, properties=', '.join(properties))
        )
