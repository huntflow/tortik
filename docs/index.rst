.. title:: Tortik

|Tortik|
========

.. |Tortik| image:: parallel.png
    :alt: Tortik
    :width: 427


Tortik is a frontend micro framework atop of Python Tornado making easier to develop SOA-based applications.


Short explanation of tortik features: `<http://glibin.github.io/tortik>`_

Documentation and installation instructions  `<http://tortik.readthedocs.org/en/latest/>`_


SOA (microservices) and tortik use cases at PyCon RU 2014 (in Russian) `<http://glibin.github.io/lections/pycon2014/>`_



Installation
------------

**Automatic installation**::

    pip install tortik

Tortik is listed in `PyPI <http://pypi.python.org/pypi/tortik>`_ and
can be installed with ``pip`` or ``easy_install``.

If you plan to use XML backends it's highly recommended to install `lxml <http://lxml.de/>`_
package (tortik will use it if available) which is much faster than native implementation
and have more features and additional libraries.


Documentation
-------------

.. toctree::
    :titlesonly:

    page

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
