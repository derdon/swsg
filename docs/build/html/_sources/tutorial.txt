.. highlight:: bash

Tutorial
========

Hello, new SWSG user!  In this tutorial you will learn how to work with SWSG
projects. To be more detailed, you will learn how to …

#. create a new project
#. get a list of all projects
#. add and modify sources and templates
#. render a project
#. remove a project

Preparation
-----------

Before you can start, you need to have SWSG installed (see
:ref:`first-steps` for more information). Additionally, you have to know
how to navigate through your filesystem via a terminal.

Creating a new project
----------------------

Open a new terminal window and create an empty directory for all your SWSG
projects (this step is optional). ::

    mkdir swsg-projects
    cd swsg-projects

Initialize a new project by invoking the following command ::

    swsg-cli init example-project

Let's see what happened. The first action which was performed is the
initialization of the filesystem structure. ::

    tree -F 
    .
    └── example-project/
        ├── config.ini
        ├── output/
        ├── sources/
        └── templates/

    4 directories, 1 file
        
As you can see, three empty directories and one default configuration file
have been created (We will take a look at the configuration file in
:ref:`configuration`). After that, SWSG writes some useful information in
a file which saves all SWSG projects with their corresponding properties.
These properties are:

- the *name* of the project
- the *path* which shows where the project directory is located
- the date and time when the project was *created*
- the date and time when the project was *modified the last time*

The command ``list-projects`` lists all projects in an ASCII
table, including their discussed properties::

    swsg-cli list-projects
    +-----------------+----------------------------+--------------------------+--------------------------+
    |      Name       |            Path            |         Created          |      Last modified       |
    +=================+============================+==========================+==========================+
    | example-project | /Users/simon/swsg-projects | Tue Nov  9 20:58:05 2010 | Tue Nov  9 20:58:05 2010 |
    +-----------------+----------------------------+--------------------------+--------------------------+

To find out the path of the file which saves these projects, copy & paste
the following command into your shell::

    [[ $XDG_DATA_HOME != '' ]] && echo -n $XDG_DATA_HOME || echo -n '~/.local/share/'; echo 'swsg/projects.shelve'

Add content
-----------

Let's add some text files to make the use of SWSG senseful :-)

Create a file with the following content and save it in
:file:`~/swsg-projects/example-project/sources/index.rst`

.. code-block:: rest

    A heading
    =========

    This is my *first* document to test the usage of `SWSG`_. Cool, it seems to
    work :-)

    .. _SWSG: http://pypi.python.org/pypi/swsg/

Render the project
------------------

To convert all files in your source directory (currently there is only one
file, but you can add as many as you want), there is the command
``render``::

    swsg-cli render

.. TODO:
   - call ``tree`` again to see that the file output/index.html was
   created.
   - use ``cat`` to print its output
   - change the title and render again -> subsection
   - change the template file and render again -> subsection
   - enter ``ls -l output/index.html`` to show the output's timestamp and
   call ``render`` again to prove that this command is smart enough to
   detect if re-rendering is necessary or not
   "To experience more about the caching algorithm SWSG uses to detect
   whether a source file should be rendered again or not, see ..."

Remove the project
------------------

TODO: call ``swsg-cli remove-project example-project``; ``swsg-cli
list-projects`` to verify that the project has really been removed.

.. warning::
   It is important that you do not remove the project directory manually,
   e.g. with the ``rm`` command. Because if you do so, the project will
   still be in the list of projects you get via the ``list-projects``
   command.
