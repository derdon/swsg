import py.test
from swsg.templates import (BaseTemplate, SimpleTemplate,
    MakoTemplate, Jinja2Template, GenshiTemplate)

SOURCE_TEXT = u'title: source title\nsome **important** text'
SIMPLE_TEMPLATE_TEXT = u'<title>$title</title>$content'

FIRST_REAL_LINE = u'first real line of the template'


def test_template_equality():
    t1 = BaseTemplate(u'foo')
    t2 = BaseTemplate(u'foo')
    assert t1 == t2
    t3 = BaseTemplate(u'bar')
    assert t1 != t3
    assert t2 != t3


def test_simple_template():
    template = SimpleTemplate(SIMPLE_TEMPLATE_TEXT)
    title = 'test title'
    content = 'blah blah'
    namespace = {'title': title, 'content': content}
    rendered_template = template.render(namespace)
    assumed_result = SIMPLE_TEMPLATE_TEXT.replace(
        '$title', title).replace('$content', content)
    assert rendered_template == assumed_result


def test_mako_template():
    mako = py.test.importorskip('mako')
    # almost completely copied from mako's homepage
    template_text = u'''
<table>
    % for row in rows:
        ${makerow(row)}
    % endfor
</table>

<%def name="makerow(row)">
    <tr>
    % for name in row:
        <td>${name}</td>
    % endfor
    </tr>
</%def>'''.strip()
    rows = [list(range(10)) for row in range(10)]
    mako_template = MakoTemplate(template_text)
    rendered_mako_template = mako_template.render({'rows': rows})
    assumed_result = mako.template.Template(template_text).render(rows=rows)
    assert rendered_mako_template == assumed_result


def test_jinja2_template():
    jinja2 = py.test.importorskip('jinja2')
    template_text = u'''{% for item in r -%}
        {{ item }}
    {%- endfor %}'''
    jinja_template = Jinja2Template(template_text)
    rendered_jinja_template = jinja_template.render({'r': range(10)})
    assumed_result = jinja2.Template(template_text).render(r=list(range(10)))
    assert rendered_jinja_template == assumed_result


def test_genshi_template():
    py.test.importorskip('genshi')
    from genshi.template.markup import MarkupTemplate
    # the following snippet is copied from
    # http://genshi.edgewall.org/wiki/ApiDocs/genshi.template.markup
    # and extended by an assignment at the beginning
    #<ul py:with="items=range(10)">
    template_text = '''<div xmlns:py="http://genshi.edgewall.org/">
    <ul>
        <li py:for="item in items">${item}</li>
    </ul>
</div>'''
    genshi_template = GenshiTemplate(template_text)
    rendered_genshi_template = genshi_template.render({'items': range(10)})
    assumed_stream = MarkupTemplate(template_text).generate(items=range(10))
    assumed_result = assumed_stream.render()
    assert rendered_genshi_template == assumed_result
