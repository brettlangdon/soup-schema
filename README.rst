soup-schema
===========

Define schemas for parsing HTML with BeautifulSoup4_.

.. _BeautifulSoup4: https://www.crummy.com/software/BeautifulSoup/

Installing
----------

.. code:: bash

    pip install soup_schema


Example usage
-------------

.. code:: python

    from soup_schema import Schema, Selector, AttrSelector

    class PageSchema(Schema):
        content = Selector('#content', required=True)
        description = Selector('[name=description]')
        stylesheets = AttrSelector('[rel=stylesheet]', 'href', as_list=True)
        title = Selector('title', required=True)


    html = """
    <html>
      <head>
        <title>My page title</title>
        <link rel="stylesheet" href="/dist/css/third-party.css" />
        <link rel="stylesheet" href="/dist/css/style.css" />
        <meta name="description" content="This is my page description" />
      </head>
      <body>
        <div id="content">
          <p>This is my page content</p>
        </div>
      </body>
    </html>
    """

    page = PageSchema.parse(html)
    print(page)
    # PageSchema(
    #   content='\nThis is my page content\n',
    #   description='This is my page description',
    #   stylesheets=['/dist/css/third-party.css', '/dist/css/style.css'],
    #   title='My page title'
    # )
