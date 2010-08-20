from tempfile import NamedTemporaryFile

import py.test
from swsg.sources import (Source, render_rest, render_creole, render_textile,
        render_markdown)

from temp_utils import TemporaryProject


def test_source_render():
    project = TemporaryProject()
    with project as p:
        p.init()
        source = p.add_source('**text**')
        assert source.render() == u'<p><strong>text</strong></p>\n'


def test_source_init():
    # trying to give a non-exeisting file should raise an IOError
    py.test.raises(IOError, 's = Source("doesnotexist.rest")')
    # trying to use a markup language which does not exist should raise a
    # ValueError
    with NamedTemporaryFile() as temp_fp:
        py.test.raises(
            ValueError,
            's = Source(temp_fp.name + "invalid markup language")')


def test_render_rest():
    r'''
>>> render_rest(u'simple test')
u'<p>simple test</p>\n'
>>> render_rest(u'**simple test**')
u'<p><strong>simple test</strong></p>\n'
>>> render_rest(u'`simple test`')
u'<p><cite>simple test</cite></p>\n'
>>> render_rest(u'``test``')
u'<p><tt class="docutils literal">test</tt></p>\n'
>>> render_rest(u'`example`_\n\n.. _example: http://example.com')
u'<p><a class="reference external" href="http://example.com">example</a></p>\n'
>>> render_rest(u'`example <http://example.com>`_')
u'<p><a class="reference external" href="http://example.com">example</a></p>\n'
    '''
    py.test.importorskip('docutils')


def test_render_creole():
    r'''
>>> render_creole(u'test')
u'<p>test</p>\n'
>>> render_creole(u'test\ntest')
u'<p>test test</p>\n'
    '''
    py.test.importorskip('creole')


def test_render_textile():
    r'''
>>> render_textile('_This_ is a *test.*')
'<p><em>This</em> is a <strong>test.</strong></p>'
>>> render_textile('* One\n* Two\n* Three')
'<ul>\n\t\t<li>One</li>\n\t\t<li>Two</li>\n\t\t<li>Three</li>\n\t</ul>'
>>> render_textile('Link to "Slashdot":http://slashdot.org/')
'<p>Link to <a href="http://slashdot.org/">Slashdot</a></p>'
    '''
    py.test.importorskip('textile')


def test_render_markdown():
    r'''
>>> render_markdown('[Slashdot](http://slashdot.org/ "Slashdot - News for nerds, stuff that matters")')
u'<p><a href="http://slashdot.org/" title="Slashdot - News for nerds, stuff that matters">Slashdot</a></p>'
>>> render_markdown('---------------------------------------')
u'<hr />'
>>> render_markdown('![Python](http://python.org/community/logos/python-logo.png "The Python Logo")')
u'<p><img alt="Python" src="http://python.org/community/logos/python-logo.png" title="The Python Logo" /></p>'
    '''
    py.test.importorskip('markdown')
