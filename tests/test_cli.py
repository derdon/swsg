import py
from swsg.cli import parse_args, validate_change_config
from swsg import __version__ as swsg_version
from swsg.sources import SUPPORTED_MARKUP_LANGUAGES
from swsg.templates import SUPPORTED_TEMPLATE_ENGINES

args_without_any_options = parse_args(['list'])


def pytest_generate_tests(metafunc):
    if 'markup' in metafunc.funcargnames:
        for m in SUPPORTED_MARKUP_LANGUAGES:
            metafunc.addcall(funcargs=dict(markup=m))
    elif 'template' in metafunc.funcargnames:
        for t in SUPPORTED_TEMPLATE_ENGINES:
            metafunc.addcall(funcargs=dict(template=t))


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


def test_logfile():
    assert not args_without_any_options.logfile
    logfile_name = 'file.log'
    args_with_logfile_long = parse_args(['--logfile', logfile_name, 'list'])
    assert args_with_logfile_long.logfile == logfile_name
    args_with_logfile_short = parse_args(['-l', logfile_name, 'list'])
    assert args_with_logfile_short.logfile == logfile_name


def test_init():
    # the name of the project is required, so
    # omitting it will finally raise a SystemExit
    py.test.raises(SystemExit, "parse_args(['init'])")
    project_name = 'test project'
    args_with_default_project_directory = parse_args(['init', project_name])
    assert args_with_default_project_directory.name == project_name
    assert args_with_default_project_directory.project_directory == '.'
    proj_dir = '/my/test/dir'
    args_with_explicit_project_directory = parse_args(
        ['init', project_name, '-p', proj_dir])
    assert args_with_explicit_project_directory.project_directory == proj_dir
    args_with_explicit_project_directory = parse_args(
        ['init', project_name, '--project-directory', proj_dir])
    assert args_with_explicit_project_directory.project_directory == proj_dir


def test_change_config(capsys):
    args = parse_args(['change-config'])
    try:
        validate_change_config(args)
    except SystemExit, e:
        # exit code is 2 because it is a CLI error
        assert e.code == 2
        out, err = capsys.readouterr()
        # there should be no output to STDOUT
        assert out == u''
        expected_error_message = (
            'Error: Neither a markup language '
            'nor a template language was given.\n')
        assert err == expected_error_message
    else:
        assert False
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
