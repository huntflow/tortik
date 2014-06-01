Simple tortik application
=========================

Usage: ``./server.py --help``.

Simple application demonstrating tortik capabilities.

Description
-----------

Pointing to ``/`` page makes two request to the services (Steam featured games and HH API dictionaries)
returning JSON data and postprocessing it (return list of images for featured games).

Pointing to ``/?debug`` will show the page processing.

Pointing to ``/exception`` will show debug page because of exception in page handler (division by zero).
