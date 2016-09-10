from bs4 import BeautifulSoup

from .selector import Selector


class Schema(object):
    """
    Base class to inherit from for defining custom HTML schemas

    :Example:

    .. code:: python

        class CustomSchema(Schema):
            # Parse the `<title></title>` element from the document
            title = Selector('title', required=True)
            # ... define other selectors here

        html = \"\"\"
        <html>
          <head>
            <title>My page title</title>
          </head>
          <body>
          </body>
        </html>
        \"\"\"
        parsed = CustomSchema.parse(html)
    """
    @classmethod
    def _get_selectors(cls):
        """Helper to get all the selectors defined on this Schema"""
        for name, value in cls.__dict__.items():
            if isinstance(value, Selector):
                yield name, value

    @classmethod
    def parse(cls, html):
        """
        Parse the provided html document into this schema.

        :param html: The text content of the HTML document to parse
        :type html: (str, bytes)
        :return: An instance of :class:`soup_schema.schema.Schema` which has had it's selectors parsed from ``html``
        :rtype: :class:`soup_schema.schema.Schema`
        :raises: :class:`soup_schema.error.ValidationError` if there was a problem parsing a selector
          (e.g. one was required but none was found)
        """
        instance = cls()
        soup = BeautifulSoup(html, 'html.parser')
        for name, value in cls._get_selectors():
            setattr(instance, name, value.resolve(soup))
        return instance

    def __repr__(self):
        properties = []
        for name, _ in self.__class__._get_selectors():
            value = getattr(self, name, None)
            properties.append('{name}={value}'.format(name=name, value=repr(value)))
        return (
            '{name}({properties})'
            .format(name=self.__class__.__name__, properties=', '.join(properties))
        )
