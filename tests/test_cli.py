from py.io import StdCapture
from swsg.cli import parse_args
from swsg import __version__ as swsg_version

args_without_any_options = parse_args(['list'])


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


def test_version():
    capture = StdCapture()
    try:
        parse_args(['--version'])
    except SystemExit, e:
        # exit code is 0
        assert e.code == 0
        out, err = capture.done()
        # there should be no output to STDOUT
        stdout = out.read()
        assert stdout == u''
        # version string is printed to STDERR
        stderr = err.read()
        expected_version_string = 'py.test {0}\n'.format(swsg_version)
        assert stderr == expected_version_string
    else:
        assert False
