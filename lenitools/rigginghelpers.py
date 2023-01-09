# <> with ❤ by @LeniMagEsVonHinten

import maya.cmds as cmds

__all__ = ['Leni_rigginghelpers_lock']


def Leni_rigginghelpers_lock(*args, **kwargs):
    """
    Lock or unlock transformations in a selected node

    >>> Leni_rigginghelpers_lock()
    >>> Leni_rigginghelpers_lock(lock=False)
    >>> Leni_rigginghelpers_lock('translate', 'rotate')
    >>> Leni_rigginghelpers_lock(axis=['x','y'])

    :param args: arguments
    :param kargs: keyword options
    """
    attributes = []
    args = [argument.lower() for argument in args]

    if len(args) <= 0:
        attributes = ['translate', 'rotate', 'scale']

    if 'translate' in args or 't' in args:
        attributes.append('translate')

    if 'rotate' in args or 'r' in args:
        attributes.append('rotate')

    if 'scale' in args or 's' in args:
        attributes.append('scale')

    axes = kwargs.get('axis', ['X', 'Y', 'Z'])
    axes = [axis.upper() for axis in axes]
    lock = kwargs.get('lock', True)

    selected_objects = kwargs.get('axis', cmds.ls(selection=True))
    for attribute in attributes:
        for axis in axes:
            for _object in selected_objects:
                cmds.setAttr('{}.{}{}'.format(_object, attribute, axis), lock=lock)
