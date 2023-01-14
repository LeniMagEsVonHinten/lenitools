# <> with ❤ by @LeniMagEsVonHinten

""" Install python wheels """

from pathlib import Path

import tarfile
import tempfile
import functools

from .filter.tararchive import Leni_filter_tarmembersuffix

__all__ = ['Leni_install_wheel', 'Leni_list_archive', 'Leni_extract_archive']


def Leni_install_wheel(*args, **kwargs) -> bool:
    """
    Install a python wheel

    :param wheel: filepath to wheel, Defaults to ''
    """
    if len(args) < 1 and 'path' not in kwargs.keys():
        return False
    if 'path' in kwargs.keys():
        success = True
        for wheel_file in Path(kwargs.keys('path')).iterdir():
            ret = Leni_install_wheel(str(wheel_file))
            if not ret:
                success = False
        return success

    suffices: list[str] = ['.whl']
    for file in args:
        print('Install', file)
    return True


def Leni_list_archive(*args, **kwargs) -> dict[str, list[str]]:
    """
    List content of archive

    Currently, only tar-archives are supported.

    :param archive: filepath to archive, Defaults to ''
    """
    if len(args) < 1:
        raise RuntimeError('*** Wrong parameters: Expecting more than 1 argument, got 0')
    elif not functools.reduce(lambda x, y: x and y, [Path(f).is_file() for f in args]):
        raise RuntimeError('*** Wrong parameter: One or more file paths given are no files!')
    archive_items = {}

    archives = filter(lambda f: tarfile.is_tarfile(f), args)

    for filepath in archives:
        archive = tarfile.open(filepath)
        archive_items[filepath] = archive.getnames()
        archive.close()
    return archive_items


def Leni_extract_archive(*args, **kwargs) -> str:
    """
    Extract archive and install all contained python wheels

    Currently, only tar-archives are supported.
    """
    if 'selection' in kwargs.keys():
        selection = kwargs.get('selection')
        archives = selection.keys()
    elif len(args) < 1:
        raise RuntimeError('*** Wrong parameters: Expecting more than 1 argument, got 0')
    else:
        selection = 'all'
        archives = filter(lambda f: tarfile.is_tarfile(f), args)

    tmp_directory = kwargs.get('path', tempfile.mkdtemp())

    # extract archive
    for filepath in archives:
        with tarfile.open(filepath) as archive:
            if selection == 'all':
                archive.extractall(
                    path=tmp_directory,
                    members=Leni_filter_tarmembersuffix(archive, '.whl')
                )
            else:
                for member in selection[filepath]:
                    archive.extract(member=member, path=tmp_directory)
    return tmp_directory


