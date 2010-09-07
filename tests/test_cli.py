import py
from swsg.cli import parse_args
from swsg import __version__ as swsg_version
from swsg.sources import SUPPORTED_MARKUP_LANGUAGES
from swsg.templates import SUPPORTED_TEMPLATE_ENGINES

args_without_any_options = parse_args(['list'])


def pytest_generate_tests(metafunc):
    funcargnames = set(metafunc.funcargnames)
    supported_stuff = (SUPPORTED_MARKUP_LANGUAGES, SUPPORTED_TEMPLATE_ENGINES)
    funcarg_is_template = 'template' in funcargnames
    key = 'template' if funcarg_is_template else 'markup'
    if set(('markup', 'template')) & funcargnames:
        for x in supported_stuff[funcarg_is_template]:
            metafunc.addcall(funcargs={key: x})


def test_verbose():
    assert not args_without_any_options.verbose
    args_with_verbose_short = parse_args(['-v', 'list'])
    assert args_with_verbose_short.verbose
    args_with_verbose_long = parse_args(['--verbose', 'list'])
    assert args_with_verbose_long.verbose


def test_debug():
    assert not args_without_any_options.debug
    args_with_debug_short = parse_args(['-d', 'list'])
    assert args_with_debug_short.debug
    args_with_debug_long = parse_args(['--debug', 'list'])
    assert args_with_debug_long.debug


def test_version(capsys):
    try:
        parse_args(['--version'])
    except SystemExit, e:
        # exit code is 0
        assert e.code == 0
        out, err = capsys.readouterr()
        # there should be no output to STDOUT
        assert out == u''
        # version string is printed to STDERR
        expected_version_string = 'py.test {0}\n'.format(swsg_version)
        assert err == expected_version_string
    else:
        assert False


def test_change_config():
    args = parse_args(['change-config'])
    assert args.markup_language is None
    assert args.template_language is None
    py.test.raises(
        SystemExit,
        "parse_args(['change-config', '-t', 'non_existing_template_engine'])")
    py.test.raises(
        SystemExit,
        "parse_args(['change-config', '-m', 'non_existing_markup_language'])")


def test_markup_config(markup):
    args = parse_args(['change-config', '-m', markup])
    assert args.markup_language == markup
    assert args.template_language is None


def test_template_config(template):
    args = parse_args(['change-config', '-t', template])
    assert args.template_language == template
    assert args.markup_language is None
