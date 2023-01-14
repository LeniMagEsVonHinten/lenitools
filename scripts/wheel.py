#!/usr/bin/env mayapy
# <> with ❤ by @LeniMagEsVonHinten

""" Install python wheels """

import os
import sys
import tarfile
import tempfile
import subprocess
import platform

from argparse import ArgumentParser
from pathlib import Path

try:
    import maya.cmds as cmds

    is_maya = True
except (ModuleNotFoundError, ImportError):
    is_maya = False

try:
    import pymel.core as pm

    pymel_supported = True
except (ModuleNotFoundError, ImportError):
    pymel_supported = False

DEFAULT_VERBOSE_LEVEL = 2


def extract_filelist_by_suffix(filelist, filter_func=lambda f: Path(f).suffix == '.txt', results=None, **kwargs):
    results = results or []
    for file in filelist:
        if Path(file).is_file() and filter_func(Path(file).suffix):
            filename = file.resolve().absolute()
            results.append(filename)
            # T: #CMD
            print_verbose(_('Add {file}').format(file=filename), min_level=2, verbose=kwargs.get('verbosity', 0))
        if tarfile.is_tarfile(file):
            # T: #CMD
            print_verbose(_('Analyse {file}').format(file=file), min_level=3, verbose=kwargs.get('verbosity', 0))
            target_directory = tempfile.mkdtemp()

            with tarfile.open(file) as archive:
                members = [m for m in filter(lambda x: filter_func(x.name), archive.getmembers())]
                archive.extractall(path=target_directory, members=[m for m in filter_member_by_suffix(members, '.whl')])
            results.extend(extract_filelist_by_suffix([x for x in Path(target_directory).iterdir()], filter_func, results, **kwargs))
    return results


def filter_member_by_suffix(members: list[tarfile.TarInfo], suffix: str = '.txt') -> tarfile.TarInfo:
    """
    Generator to filter members of a Tarfile by file suffix

    :param members: list of TarInfo objects
    :param suffix: suffix to look for

    :return: next TarInfo object with suffix
    """
    for tarinfo in members:
        if os.path.splitext(tarinfo.name)[1] == suffix:
            yield tarinfo


def get_maya_install_dir(version: str) -> str:
    """
    return Maya Installation Directory

    Currently, only works in Maya itself

    :param version: Return installation of specific Maya Version. Currently unused. Required.

    :return: installation directory of Maya
    """
    if is_maya:
        return os.environ['MAYA_LOCATION'].rstrip(os.path.sep).rstrip('/')
    return ''


def info_string() -> str:
    """
    Returns a string with some information about the Maya installation

    Includes:
    * Maya Version
    * Python Version
    * System (Windows, Linux or macOS)
    * whether PyMEL is installed
    * Maya installation path

    :return: system information as string
    """
    maya_version = cmds.about(version=True) if is_maya else ''
    # T: #CMD Results in sth. like:
    # T: #CMD    Maya 2023, Python 2.9 on Windows <with PyMEL>
    # T: #CMD    Installed in C:\Program Files\Autodesk\Maya2023
    return _("{maya_version}, {python_version} on {system} {pymel}{install_path}").format(
        # T: #CMD "Maya" is the name of a software application by Autodesk (https://www.autodesk.de/products/maya/overview)
        maya_version=_("Maya {version}").format(version=maya_version),
        # T: #CMD "Python" is the name of a programming language (https://www.python.org/)
        python_version=_("Python {version}").format(version=platform.python_version()),
        system=platform.system(),
        # T: #CMD "PyMEL" is the name of a Python Module (https://pypi.org/project/pymel/)
        pymel=_('<with PyMEL>') if not pymel_supported else '',
        # T: #CMD
        install_path='{}{}{}'.format('\n', '', _('Installed in {directory}').format(get_maya_install_dir(version=maya_version)))
    )


def install_module(*args, **kwargs) -> int:
    """
    Install a python module or wheel

    :param args: list of modules or wheel files to install
    :param kwargs: keyword arguments
    
    keyword arguments:
        path: directory containing wheel files to install
        verbosity: verbosity level
    """
    if len(args) < 1 and 'path' not in kwargs.keys():
        return False

    # get wheels in <path> and install them
    if 'path' in kwargs.keys():
        return len([x for x in filter(lambda y: y, [install_module(str(wheel)) for wheel in Path(kwargs.get('path')).iterdir()])])

    python_interpreter = '{}/bin/mayapy'.format(os.environ['MAYA_LOCATION']) if is_maya else 'python3'
    pip_options = kwargs.get('pip_options', ['user'])
    commands = []

    for filepath in args:
        # T: #CMD
        print_verbose(_('Install {module}').format(module=filepath), min_level=2, verbose=kwargs.get('verbosity', 0))
        commands.append('"{interpreter}" -m pip install {options} {module}'.format(
            interpreter=python_interpreter, module=filepath,
            options=' '.join(['--{}'.format(opt) for opt in pip_options]))
        )

    for status, output, command in run_commands(commands):
        print_verbose(command, min_level=1, verbose=kwargs.get('verbosity', 0), prefix='🖥️ ')
        print_verbose(output, min_level=2, verbose=kwargs.get('verbosity', 0))
        # T: #CMD
        print_verbose(_('✅') if status == 0 else _('❌'), min_level=1, verbose=kwargs.get('verbosity', 0))

    return 0


def list_archive(*args, **kwargs) -> dict[str, list[str]]:
    """
    List content of archive

    Currently, only tar-archives are supported.

    :param args: list of archive files to scan
    :param kwargs: keyword arguments, currently not supported
    
    :return: dict, grouped by archive file with a list of wheel-files in each archive file.
    
    The result looks similar to this:

    ```python
        {
            "/file/path/to/archive1": 
            [
                'python_module_1.whl',
                'python_module_2.whl'
            ],
            "/path/to/archive2": 
            [
                'module_A.whl'
            ],
            
        }
    ```
    
    """
    archive_items = {}
    archives = filter(lambda f: Path(f).is_file() and tarfile.is_tarfile(f), args)

    for filepath in archives:
        with tarfile.open(filepath) as archive:
            archive_items[filepath] = archive.getnames()
    return archive_items


def print_verbose(*args, **kwargs):
    """ print depending on the verbosity level """
    verbosity = kwargs.pop('verbose', 0)
    if verbosity >= kwargs.pop('min_level', DEFAULT_VERBOSE_LEVEL):
        print(*args, **kwargs)


def prompt(msg, actions, options=None, settings=None, **kwargs):
    is_valid_input = False
    user_input = ''
    settings = settings or {}
    options = options or {}
    verbosity = kwargs.get('verbose', 0)
    msg += options.get('verbosity_map', ['', '', ''])[verbosity]

    for i in range(settings.get('loop', 3)):
        # prompt user
        print_verbose(min_level=-1, verbose=verbosity)
        option = input(msg)
        print_verbose(min_level=-1, verbose=verbosity)
        if settings.get('ignore_case', True):
            user_input = option.lower()
        if settings.get('ignore_trail', True):
            user_input = option[0]

        # handle user input
        if actions.get(user_input, '') == 'OK':
            is_valid_input = True
            break
        if actions.get(user_input, '') == 'Cancel':
            # T: #CMD
            print_verbose(_('Aborted by user.'), min_level=-1, verbose=verbosity, file=sys.stderr)
            return 1
    if not is_valid_input:
        # T: #CMD
        print_verbose(_('Invalid input: "{}"').format(user_input), min_level=-1, verbose=verbosity, file=sys.stderr)
        return -1
    return 0


def run_commands(commands: list[str]) -> tuple[int, str, str]:
    """
    Generator to run commands in shell

    Returns a tuple that contains the status code (0 for success),
    the output of the command and the command itself.
    
    :param commands: list of shell commands to run
    :return: tuple with (status code, output, command)
    """
    for command in commands:
        # ignore empty lines
        if not command.strip():
            continue

        # run command
        process = subprocess.Popen(
            command,
            shell=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            close_fds=True
        )
        try:
            std_output, std_error = process.communicate(timeout=60)
            process.terminate()
        except subprocess.TimeoutExpired:
            process.kill()
            std_output, std_error = process.communicate()

        # decode output
        std_output = std_output.decode()
        std_error = std_error.decode()

        if std_error:
            yield 1, std_error.strip(), command.strip()

        std_output = '\n' + std_output.rstrip() if len(std_output.splitlines()) > 1 else std_output.rstrip()
        yield 0, std_output, command.strip()


def run():
    """
    main entry point for non-graphical interface inside of Maya
    """
    # ###################################################################################### #
    #                                                                                        #
    # CONFIGURATION FOR MAYA SETUP                                                           #
    #                                                                                        #
    # Please use these constants to change any settings you like.                            #
    #                                                                                        #
    # WARNING:                                                                               #
    # These constants are used, if and only if you use this application without GUI.         #
    # If you want to use the UI, just ignore these constants and use the configuration files #
    # instead!                                                                               #
    #                                                                                        #
    # ###################################################################################### #

    # search path for python modules. Defaults to ~/Downloads
    MAYA_SEARCH_PATH_FOR_MODULES = r'C:\Users\Micha\Projects\lenitools\dist'

    # if True, search recursively through the search path. Defaults to True
    MAYA_RECURSIVE = True

    # if True, ignore archive files and only use wheel files (.whl). Defaults to False
    MAYA_STRICT = False

    # verbosity (1-3, Defaults to 1), controls the amount of output into the script editor
    # set to 0 to get no output at all, or up to 3 to get more detailed output
    MAYA_VERBOSE = 0

    # ###################################################################################### #
    #                                                                                        #
    #  Please don't change anything below this block                                         #
    #                                                                                        #
    # ###################################################################################### #

    # run inside of Maya, from Script Editor or similar
    search_path = str(Path(MAYA_SEARCH_PATH_FOR_MODULES).expanduser().absolute().resolve())
    maya_default_arguments = [search_path]
    if MAYA_RECURSIVE:
        maya_default_arguments.append('-r')
    if MAYA_STRICT:
        maya_default_arguments.append('-s')
    if MAYA_VERBOSE:
        verbose = '-'
        verbose += 'v' * MAYA_VERBOSE
        maya_default_arguments.append(verbose)
    main(maya_default_arguments)


def main(arguments) -> int:
    """ Main entry point for the application """
    # Command Line Arguments
    parser = ArgumentParser(add_help=False)
    # T: #CMD Headline in usage/help information
    cli_arg_grp = parser.add_argument_group(_('Command line arguments'))
    cli_arg_grp.add_argument(
        'path', type=str, nargs='+',
        # T: #CMD Help text
        help=_('Path to look for files to install.')
    )
    cli_arg_grp.add_argument(
        '-l', '--list', action='store_true',
        # T: #CMD Help text
        help=_('Look for files and list them. Do not install anything.')
    )
    cli_arg_grp.add_argument(
        '-r', '--recursive', action='store_true',
        # T: #CMD Help text
        help=_('Look recursively for files.')
    )
    cli_arg_grp.add_argument(
        '-v', '--verbose', action='count',
        # T: #CMD Help text
        help=_('Level of verbosity.')
    )
    cli_arg_grp.add_argument(
        '--dry-run', action='store_true',
        # T: #CMD Help text
        help=_('Run script without actually installing anything.')
    )
    cli_arg_grp.add_argument(
        '--system-wide', action='store_true',
        # T: #CMD Help text
        help=_('Install modules system-wide, not in user space.')
    )
    cli_arg_grp.add_argument(
        '-y', '--yes', action='store_true',
        # T: #CMD Help text
        help=_('Assume yes for any interactive question.')
    )
    cli_arg_grp.add_argument(
        '-s', '--strict', action='store_true',
        # T: #CMD Help text
        help=_('Strict mode: Only look for .whl wheel files, ignore archives.')
    )
    cli_arg_grp.add_argument(
        '-h', '--help', action='help',
        # T: #CMD Help text
        help='Show help and exit.'
    )

    args = parser.parse_args(arguments)

    pip_options=[]
    if not args.system_wide:
        pip_options.append('user')
    if args.dry_run:
        pip_options.append('dry-run')

    # gather some arguments
    verbosity = args.verbose or 0
    ignore_archives = args.strict
    if not is_maya and Path(__file__).absolute().resolve() == Path(sys.argv[0]).absolute().resolve():
        args.path = args.path[1:]
    search_path = ''.join(args.path)

    # Collect module files
    files = [
        # get all wheel files
        file for file in Path(search_path).glob('**/*.whl' if args.recursive else '*.whl')
    ] if ignore_archives else [
        # get all wheel files plus any file archive
        file for file in filter(
            lambda f: f.is_file() and tarfile.is_tarfile(f) or f.suffix == '.whl',
            [file for file in Path(search_path).glob('**/*.*' if args.recursive else '*.*')]
        )
    ]
    # T: #CMD
    print_verbose(_('Files in "{directory}":').format(directory=search_path), min_level=-1 if args.list else 1, verbose=verbosity)
    for file in files:
        print_verbose(file, min_level=-1 if args.list else 1, verbose=verbosity)
    print_verbose(
        # T: #CMD
        _('Found no files.') if len(files) <= 0 else \
        # T: #CMD
        _('{amount} files found.').format(amount=len(files)),

        min_level=-1 if args.list else 0, verbose=verbosity, file=sys.stderr if len(files) <= 0 else sys.stdout)

    if len(files) <= 0:
        return 1

    if args.list:
        return 0

    # prompt user whether to continue with installation or not
    if not args.yes:
        # T: #CMD
        message = _('Do you want to continue with installation?  (Y/n) ')
        actions = {
            'y': 'OK',
            'n': 'Cancel'
        }
        settings = {
            'verbosity_map': [
                # T: #CMD
                '{}{}'.format('\n', _('(Archives, that do not contain python wheels will be ignored automatically)')),
                # T: #CMD
                '{}{}'.format('\n', _('(Archives, that do not contain python wheels will be ignored automatically)')),
                # T: #CMD
                '{}{}'.format('\n', _('(Archives, that do not contain python wheels will be ignored automatically)'))
            ]
        }
        prompt(message, actions, settings=settings)

    # T: #CMD
    print_verbose(_('Prepare installation'), min_level=1, verbose=verbosity)
    # T: #CMD
    print_verbose(_('Extract archives and collect wheels'), min_level=1, verbose=verbosity)
    extracted_files = extract_filelist_by_suffix(files, filter_func=lambda f: Path(f).suffix == '.whl')

    # T: #CMD
    print_verbose(_('Install wheels'), min_level=1, verbose=verbosity)
    install_module(extracted_files, pip_options=pip_options)

    # T: #CMD
    print_verbose(_('Finished.'), min_level=3, verbose=verbosity)
    return 0


if __name__ == '__main__':
    if not is_maya:
        # run as command line application, without Maya
        arguments = sys.argv if len(sys.argv) > 1 else ['-h']
        main(arguments)
    else:
        run()
