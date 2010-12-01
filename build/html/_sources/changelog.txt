Changelog
=========

0.3
---
- use the variable ``content`` instead of ``get_content`` for accessing rendered
  sources within templates 
- added CleverCSS support
- fixed some bugs in the command ``quickstart`` and improved the prompts
- implemented a caching algorithm to save unnecessary rendering processes
- do not only pay attention to the Genshi settings, but also to the Jinja
  settings for the rendering process
- removed the progressbar which used to appear during the rendering process
  &rarr; removed the dependeny "progressbar"
- assign one template to each source file instead of assigning a list of
  source files to each templaze

  - use a default template, whose file name is given in the config file, if no
    template is assigned in a source file

    - the content of this template depends on the value of ``template language``
      in the config file

0.2.5
-----
- use more verbose logging messages
- fix removing projects

0.2.4
-----
- use an absolute path to create an empty logfile
- make installation possible, even if distribute / setuptools is not installed

0.2.3
-----
- make sure that the directories exist where the logfile is located

0.2.2
-----
- fix install for easy_install and pip users

0.2.1
-----
- add the python package "argparse" to the list of requirements if it is not
  installed yet

0.2
---
- use a global configuration file if it can be found as the default
  configuration for new projects
- added the subcommand "quickstart"
- print more useful error messages, e.g. if a source file mentioned in a
  template cannot be found
- added support for the template engines Mako, Jinja2 and Genshi:

  - Genshi:

    - added the configuration options ``method`` (can be either "html" or
      "xhtml") and ``doctype`` to specify the behaviour of rendering

  - Jinja2

    - added the following configuration options (see `the Jinja
      documentation about Jinja2.Environment
      <http://jinja.pocoo.org/api/#jinja2.Environment>`_ for their meanings and
      default values):

      - block_start_string
      - block_end_string
      - variable_start_string
      - variable_end_string
      - comment_start_string
      - comment_end_string
      - trim_blocks
- renamed the section "local configuration" in the project-dependent
  config.ini to "general"
- interpret also short filename extensions of sources (new filename
  extensions: ``*.rst`` for ReST, ``*.md`` for Markdown, and ``*.tt`` for
  Textile)

0.1
---
- fixed many bugs
- added many tests and improved the existing ones
- source files can have titles now (it is highly recommended that you set a
  title for each source file; the fallback for titleless source files will
  generate a rather useless title (it simply takes the first five words of the
  source file's first line))
- print a progressbar during the rednering process
- create required directories and an empty logfile directly after the
  installation process
- the encoding UTF-8 for reading template files and source files is used
- additional packages from PyPi are required: texttable, py and logbook
- added logging features:

  - new global CLI option :option:`-l --logfile` determines the location of the
    logfile
    (default is $XDG_DATA_HOME/swsg/swsg.log if this environment variable is
    set; otherwise it is ~/.local/share/swsg/swsg.log
  - new global CLI options :option:`-v --verbose` and :option:`-d --debug` set
    the logging levels where the debug option will overwrite the verbose option
    in the case where both are set

- general changes to the command line interface (swsg-cli):

  - added many help messages to arguments and options
  - new CLI argument "list-projects" lists all created projects in a pretty
    ASCII table
  - added an argument for removing projects: remove-project path/to/the/project
  - added a function to validate the use of the argument change-config: an error
    message is written to STDERR and the script will be quit if neither a markup
    language nor a template language was given
  - restricted the set of possible values for the options
    :option:`--markup-language`
    and :option:`--template-language` for the argument ``change-config``

0.1a
----
- initial release
