Information for developers
==========================

How to run the tests
--------------------
SWSG uses py.test_ as a library for unittesting. To check whether the test
fail or pass, execute the following command (assuming :file:`~/swsg/tests`
points to a SWSG repository)::

    py.test ~/swsg/tests --pastebin=failed

If there have been any python tracebacks or other errors, a :abbr:`URL
(Uniform Resource Locator)` will appear at the end of the output. If this
is the case and you use the latest release of SWSG, I will be glad if you
open a new issue on `the issue tracker on the github repository of SWSG`_.

..
    - explain how to subclass ``swsg.Project`` to alter paths like
      ``swsg.Project.source_dir``
    - explain how to add custom template languages by subclassing
      ``swsg.templates.BaseTemplate``
    - only an idea: adding custom markup languages by subclassing
      ``swsg.sources.BaseSource``?
    - HOWTO write a custom interface (!)

.. HOWTO add custom template functions / values

.. _py.test: http://codespeak.net/py/dist/test/index.html
.. _the issue tracker on the github repository of SWSG: http://github.com/derdon/swsg/issues
