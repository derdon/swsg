from functools import partial

import py.test
from swsg.sources import (UnsupportedMarkup, BaseSource, ReSTSource,
    CreoleSource, TextileSource, MarkdownSource, get_source_class_by_markup)


def test_base_source():
    Source = partial(BaseSource, '', 'default.html')
    source = Source('')
    assert source.title == 'unknown'
    assert source.template_path == 'default.html'
    assert source.text == ''
    source = Source('title: foo\nsome text')
    assert source.title == 'foo'
    assert source.template_path == 'default.html'
    assert source.text == 'some text'
    source = Source('some text')
    assert source.title == 'unknown'
    assert source.template_path == 'default.html'
    assert source.text == 'some text'
    source = Source('template: bar.html\nsome text')
    assert source.title == 'unknown'
    assert source.template_path == 'bar.html'
    assert source.text == 'some text'
    source = Source('title: foo\ntemplate: bar.html\nsome text')
    assert source.title == 'foo'
    assert source.template_path == 'bar.html'
    assert source.text == 'some text'
    # make sure that the order of assignments does not matter
    source = Source('template: bar.html\ntitle: foo\nsome text')
    assert source.title == 'foo'
    assert source.template_path == 'bar.html'
    assert source.text == 'some text'


def test_render_rest():
    r'''
>>> ReSTSource(u'simple test').render_templateless()
u'<p>simple test</p>\n'
>>> ReSTSource(u'**simple test**').render_templateless()
u'<p><strong>simple test</strong></p>\n'
>>> ReSTSource(u'`simple test`').render_templateless()
u'<p><cite>simple test</cite></p>\n'
>>> ReSTSource(u'``test``').render_templateless()
u'<p><tt class="docutils literal">test</tt></p>\n'
>>> ReSTSource(u'`example`_\n\n.. _example: http://example.com').render_templateless()
u'<p><a class="reference external" href="http://example.com">example</a></p>\n'
>>> ReSTSource(u'`example <http://example.com>`_').render_templateless()
u'<p><a class="reference external" href="http://example.com">example</a></p>\n'
    '''
    py.test.importorskip('docutils')


def test_render_creole():
    r'''
>>> CreoleSource(u'test').render_templateless()
u'<p>test</p>\n'
>>> CreoleSource(u'test\ntest').render_templateless()
u'<p>test test</p>\n'
    '''
    py.test.importorskip('creole')


def test_render_textile():
    r'''
>>> TextileSource('_This_ is a *test.*').render_templateless()
'<p><em>This</em> is a <strong>test.</strong></p>'
>>> TextileSource('* One\n* Two\n* Three').render_templateless()
'<ul>\n\t\t<li>One</li>\n\t\t<li>Two</li>\n\t\t<li>Three</li>\n\t</ul>'
>>> TextileSource('Link to "Slashdot":http://slashdot.org/').render_templateless()
'<p>Link to <a href="http://slashdot.org/">Slashdot</a></p>'
    '''
    py.test.importorskip('textile')


def test_render_markdown():
    r'''
>>> MarkdownSource('[Slashdot](http://slashdot.org/ "Slashdot - News for nerds, stuff that matters")').render_templateless()
u'<p><a href="http://slashdot.org/" title="Slashdot - News for nerds, stuff that matters">Slashdot</a></p>'
>>> MarkdownSource('---------------------------------------').render_templateless()
u'<hr />'
>>> MarkdownSource('![Python](http://python.org/community/logos/python-logo.png "The Python Logo")').render_templateless()
u'<p><img alt="Python" src="http://python.org/community/logos/python-logo.png" title="The Python Logo" /></p>'
    '''
    py.test.importorskip('markdown')


def test_get_source_class_by_markup():
    f = get_source_class_by_markup
    assert f('rest') == ReSTSource
    assert f('rst') == ReSTSource
    assert f('creole') == CreoleSource
    assert f('textile') == TextileSource
    assert f('tt') == TextileSource
    assert f('markdown') == MarkdownSource
    assert f('md') == MarkdownSource
    py.test.raises(UnsupportedMarkup, "f('does_not_exist')")
