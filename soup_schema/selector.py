from bs4 import BeautifulSoup

from .error import ValidationError


class Selector(object):
    def __init__(self, selector, required=False, as_list=False):
        self.selector = selector
        self.as_list = as_list
        self.required = required

    def _get_value(self, elm):
        if elm is None:
            return None
        if 'content' in elm.attrs:
            return elm.attrs['content']
        return elm.text

    def resolve(self, soup):
        if isinstance(soup, (str, bytes)):
            soup = BeautifulSoup(soup, 'html.parser')
        value = None
        if self.as_list:
            value = [self._get_value(elm) for elm in soup.select(self.selector)]
        else:
            elm = soup.select_one(self.selector)
            value = self._get_value(elm)

        if not value and self.required:
            raise ValidationError(
                'Expected at least 1 element matching selector "{selector}", none was found'
                .format(selector=self.selector)
            )
        return value


class AttrSelector(Selector):
    def __init__(self, selector, attribute, *args, **kwargs):
        super(AttrSelector, self).__init__(selector=selector, *args, **kwargs)
        self.attribute = attribute

    def _get_value(self, elm):
        if elm is None:
            return None
        return elm.attrs.get(self.attribute)


class SchemaSelector(Selector):
    def __init__(self, selector, schema, *args, **kwargs):
        super(AttrSelector, self).__init__(selector=selector, *args, **kwargs)
        self.schema = schema

    def _get_value(self, elm):
        return self.schema.resolve(elm)


class AnySelector(Selector):
    def __init__(self, selectors, required=False):
        self.selectors = selectors
        self.required = required

    def resolve(self, soup):
        for selector in self.selectors:
            try:
                value = selector.resolve(soup)
                if value:
                    return value
            except ValidationError:
                # DEV: It is ok if one fails, we will try the next one
                pass

        if self.required:
            raise ValidationError(
                'Expected at least 1 element matching selector "{selectors}", none was found'
                .format(selectors=self.selectors)
            )
