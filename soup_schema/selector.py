from bs4 import BeautifulSoup

from .error import ValidationError


class Selector(object):
    """
    Base selector class used for defining properties on a :class:`soup_schema.schema.Schema`

    A selector is used to define how a property should be parsed from the HTML document.

    :Example:

    .. code:: python

        class CustomSchema(Schema):
            # Parse the `<title></title>` element from the document
            title = Selector('title', required=True)
            # ... define other selectors
    """
    def __init__(self, selector, required=False, as_list=False):
        """
        Constructor for defining a new :class:`soup_schema.selector.Selector`.

        .. seealso:
          `BeautifulSoup CSS Selectors <https://www.crummy.com/software/BeautifulSoup/bs4/doc/#css-selectors>`_

        :param selector: The CSS selector to use for finding a given element in the HTML document.
        :type selector: str
        :param required: Whether or not an exception should be thrown if this selector could not be parsed.
        :type required: bool
        :param as_list: Whether this selector should be parsed as a list. Default behavior is to parse only the first
          element matching the provided ``selector``
        :type as_list: bool
        """
        self.selector = selector
        self.as_list = as_list
        self.required = required

    def _get_value(self, elm):
        """Internal method for parsing the value from a BeautifulSoup element"""
        if elm is None:
            return None
        if 'content' in elm.attrs:
            return elm.attrs['content']
        return elm.text

    def resolve(self, soup):
        """
        Resolve the value for this selector from the provided HTML document (or BeautifulSoup element).

        :param soup: HTML document content as a string or BeautifulSoup object to parse this selector from
        :type soup: :class:`bs4.BeautifulSoup`, :class:`bs4.element.Tag`, str, or bytes
        :returns: The parsed element value, will be a str if a single element, list if ``as_list is True``, or
          else ``None`` if no matching element was found.
        :rtype: str, list, None
        :raises: :class:`soup_schema.error.ValidationError` if ``required is True`` and no matching element was found.
        """
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
    """
    Selector type which parses it's value from an element attribute

    :Example:

    .. code:: python

        class CustomSchema(Schema):
            # Parse the `href` attribute from all links in the HTML document
            hrefs = AttrSelector('a', 'href', as_list=True)
            # ... define other selectors
    """
    def __init__(self, selector, attribute, *args, **kwargs):
        """
        Constructor for defining a new :class:`soup_schema.selector.AttrSelector`.

        .. seealso:
          `BeautifulSoup CSS Selectors <https://www.crummy.com/software/BeautifulSoup/bs4/doc/#css-selectors>`_

        :param selector: The CSS selector to use for finding a given element in the HTML document.
        :type selector: str
        :param attribute: The name of the attribute to parse from the matching element
        :type: attribute: str
        :param required: Whether or not an exception should be thrown if this selector could not be parsed.
        :type required: bool
        :param as_list: Whether this selector should be parsed as a list. Default behavior is to parse only the first
          element matching the provided ``selector``
        :type as_list: bool
        """
        super(AttrSelector, self).__init__(selector=selector, *args, **kwargs)
        self.attribute = attribute

    def _get_value(self, elm):
        """Internal method for parsing an attribute from an element"""
        if elm is None:
            return None
        return elm.attrs.get(self.attribute)


class SchemaSelector(Selector):
    """
    Selector type which uses a :class:`soup_schema.schema.Schema` to parse it's value

    :Example:

    .. code:: python

        example_html_doc = \"\"\"
        <html>
          <head></head>
          <body>
            <div class="review">
              <div class="review__author">Author Name</div>
              <div class="review__content">This review is awesome</div>
            </div>
            <div class="review">
              <div class="review__author">Another reviewer</div>
              <div class="review__content">This review is not as awesome as the last</div>
            </div>
          </body>
        </html>
        \"\"\"

        class ReviewSchema(Schema):
            author = Selector('.review__author', required=True)
            review = Selector('.review__content', required=True)

        class DocumentSchema(Schema):
            # This selector will using `ReviewSchema` to parse each instance of `.review` in the document
            reviews = SchemaSelector('.review', ReviewSchema, as_list=True)
    """
    def __init__(self, selector, schema, *args, **kwargs):
        """
        Constructor for defining a new :class:`soup_schema.selector.SchemaSelector`.

        .. seealso:
          `BeautifulSoup CSS Selectors <https://www.crummy.com/software/BeautifulSoup/bs4/doc/#css-selectors>`_

        :param selector: The CSS selector to use for finding a given element in the HTML document.
        :type selector: str
        :param schema: The name of the attribute to parse from the matching element
        :type: schema: :class:`soup_schema.schema.Schema`
        :param required: Whether or not an exception should be thrown if this selector could not be parsed.
        :type required: bool
        :param as_list: Whether this selector should be parsed as a list. Default behavior is to parse only the first
          element matching the provided ``selector``
        :type as_list: bool
        """
        super(AttrSelector, self).__init__(selector=selector, *args, **kwargs)
        self.schema = schema

    def _get_value(self, elm):
        """Internal method for parsing a Schema from an element"""
        return self.schema.resolve(elm)


class AnySelector(Selector):
    """
    Selector type which is used as a boolean "or" for parsing an elements value.

    This selector type is useful when you want to be able to search multiple locations for a properties value.

    :Example:

    .. code:: python

        example_html_doc = \"\"\"
        <html>
          <head>
            <meta name="description" content="My description" />
            <meta name="og:description" content="My description" />
          </head>
          <body></body>
        </html
        \"\"\"

        class CustomSchema(Schema):
            # - Try to parse the `<meta name="description" />` element
            # - if that was not found, then try to parse the `<meta name="og:description" />` element
            # - if that was also not found, then raise an exception (because of `required=True`)
            description = AnySelector([
                Selector('[name=description]'),
                Selector('[name=og:description]'),
            ], required=True)
    """
    def __init__(self, selectors, required=False):
        """
        Constructor for defining a new :class:`AnySelector`.

        :param selectors: The :class:`soup_schema.selector.Selector`s to use when searching for this properties value
        :type selectors: list of :class:`soup_schema.selector.Selector`
        :param required: Whether or not an exception should be thrown if this selector could not be parsed.
        :type required: bool
        """
        self.selectors = selectors
        self.required = required

    def resolve(self, soup):
        """
        Resolve the value for this selector from the provided HTML document (or BeautifulSoup element).

        .. seealso: :meth:`soup_schema.selector.Selector.resolve`

        :param soup: HTML document content as a string or BeautifulSoup object to parse this selector from
        :type soup: :class:`bs4.BeautifulSoup`, :class:`bs4.element.Tag`, str, or bytes
        :returns: The value of the first matches ``selectors`` from this selector.
        :rtype: str, list, None
        :raises: :class:`soup_schema.error.ValidationError` if ``required is True`` and no matching element was found.
        """
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
