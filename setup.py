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
- supports many template engines: Jinja2_, Mako_, Genshi_, and also a very
  simple template language for those who do not need control structures like
  loops or if-conditions -> only the simple template language is supported yet.
- supports clevercss_ beside the usual CSS as a markup language for the
  stylesheets -> not yet!
- provides multiple interfaces: until now, only a CLI is implemented, but
  others are planned:

  - PIDA_-Plugin
  - web interface
  - possibly a GTK+ or Qt application, but I think using the PIDA-Plugin is
    more comfortable

Requirements
============
- either Python 2.7 or Python 2.6 with the python package argparse_ installed
- texttable_
- `py`_
- at least one of the following markup languages:

  - ReST_
  - markdown_
  - creole_
  - textile_
- optional: one or more of the following template engines, also installed as
  python packages:

  - `jinja2`_
  - `mako`_
  - `genshi`_

.. _ReST: http://docutils.sourceforge.net/rst.html
.. _SR: http://bitbucket.org/tiax/sr/overview
.. _markdown: http://daringfireball.net/projects/markdown/
.. _creole: http://www.wikicreole.org/
.. _textile: http://textile.thresholdstate.com/
.. _jinja2: http://jinja.pocoo.org/2/
.. _mako: http://www.makotemplates.org/
.. _Genshi: http://genshi.edgewall.org/
.. _clevercss: http://sandbox.pocoo.org/clevercss/
.. _PIDA: http://pida.co.uk/
.. _argparse: http://code.google.com/p/argparse/
.. _texttable: http://pypi.python.org/pypi/texttable
.. _py: http://pypi.python.org/pypi/py
'''

from __future__ import print_function

from setuptools import Command, setup

from swsg import __version__, LOGFILE as DEFAULT_LOGFILE


class LogfileCreater(Command):
    'a setup.py command to create an empty log file in the default location'
    user_options = [
        ('log-file=', 'l', 'the name of the log file'),
    ]

    def initialize_options(self):
        self.log_file = DEFAULT_LOGFILE

    def finalize_options(self):
        pass

    def run(self):
        'create an empty logfile'
        with open(self.log_file, 'w') as f:
            print('Creating {0}'.format(f.name))

short_description = (
    'SWSG (Static Web Site Generator) is a tool to generate static web pages.')

setup(
    name='swsg',
    description=short_description,
    long_description=__doc__,
    version=__version__,
    author='Simon Liedtke',
    author_email='liedtke.simon@googlemail.com',
    url='http://github.com/derdon/swsg',
    license='WTFPL',
    packages=['swsg'],
    install_requires=['docutils', 'py', 'texttable'],
    extras_require={
        'markdown': ['markdown'],
        'textile': ['textile'],
        'creole': ['creole'],
        'mako': ['mako'],
        'jinja2': ['jinja2']},
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
        'Topic :: Text Processing :: Markup'],
    entry_points={
        'distutils.commands': [
            'init = __main__:LogfileCreater',
        ],
        'console_scripts': [
            'swsg-cli = swsg.cli:main',
         ],
    },
)
