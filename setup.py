'''
About
=====
swsg (static web site generator) is a tool to create static websites using
human-readable markup languages like ReST_. It was highly-inspired by SR_.
The advantage of SWSG against directly using (X)HTML files is that you have one
(or more) templates and do not have to rewrite every your main layout on ebery
single site. You can concentrate on the main content: the text; the content is
seperated from the templates.

Features
========
- supports many markup languages: Markdown_, Creole_, Textile_, ReST_
- supports many template engines: Jinja2_, Mako_, Genshi_, and also a very simple
  template language for those who do not need control structures like loops or
  if-conditions -> only the simple template language is supported yet.
- supports clevercss_ beside the usual CSS as a markup language for the
  stylesheets -> not yet!
- provides multiple interfaces: until now, only a CLI is implemented, but others
  are planned:

  - PIDA_-Plugin
  - web interface
  - possibly a GTK+ or Qt application, but I think using the PIDA-Plugin is more
    comfortable

Requirements
============
- either Python 2.7 or Python 2.6 with the python package argparse_ installed
- at least one of the following markup languages:
  - ReST (the corresponding python package is called docutils_)
  - `markdown (PyPI)`_
  - `creole (PyPI)`_
  - `textile (PyPI)`_
- optional: one or more of the following template engines, also installed as
  python packages:
  - `jinja2 (PyPI)`_
  - `mako (PyPI)`_
  - `genshi (PyPI)`_

.. _ReST: http://docutils.sourceforge.net/rst.html
.. _SR: http://bitbucket.org/tiax/sr/overview
.. _Markdown: http://daringfireball.net/projects/markdown/
.. _Creole: http://www.wikicreole.org/
.. _Textile: http://textile.thresholdstate.com/
.. _Jinja2: http://jinja.pocoo.org/2/
.. _Mako: http://www.makotemplates.org/
.. _Genshi: http://genshi.edgewall.org/
.. _clevercss: http://sandbox.pocoo.org/clevercss/
.. _PIDA: http://pida.co.uk/
.. _argparse: http://pypi.python.org/pypi/argparse
.. _docutils: http://pypi.python.org/pypi/docutils
.. _markdown (PyPI): http://pypi.python.org/pypi/Markdown
.. _creole (PyPI): http://pypi.python.org/pypi/creole
.. _textile (PyPI): http://pypi.python.org/pypi/textile
.. _jinja2 (PyPI): http://pypi.python.org/pypi/Jinja2/
.. _mako (PyPI): http://pypi.python.org/pypi/Mako
.. _genshi (PyPI): http://pypi.python.org/pypi/Genshi
'''

from setuptools import setup

from swsg import __version__

setup(
    name='swsg',
    description='SWSG (Static WebSite Generator) is a tool to generate static HTML pages.',
    long_description=__doc__,
    version=__version__,
    author='Simon Liedtke',
    author_email='liedtke.simon@googlemail.com',
    url='http://github.com/derdon/swsg',
    license='WTFPL',
    packages=['swsg'],
    install_requires=['docutils'],
    extras_require={
        'markdown': ['markdown'],
        'textile': ['textile'],
        'creole': ['creole'],
        'mako': ['mako'],
        'jinja2': ['jinja2']
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        #'Environment :: Console :: Curses',
        #'Environment :: Plugins',
        #'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Text Processing',
        'Topic :: Text Processing :: Markup'
    ],
    entry_points = {
        'console_scripts': [
            'swsg-cli = swsg.cli:main',
         ]
    }
)
