# <> with ❤ by @LeniMagEsVonHinten
# Toggle Shelf Height between 1 or 2 rows

from typing import Any

import maya.cmds as cmds
import maya.mel as mel

__all__ = [
    'Leni_shelftools_get_shelf',
    'Leni_shelftools_toggle_height',
    'Leni_shelftools_height_in_pixel',
    'Leni_shelftools_set_height'
]

SHELF_HEIGHT = 35


def Leni_shelftools_get_shelf() -> Any:
    """
    return current shelf

    :return: current shelf
    """
    current_shelf = mel.eval("global string $gShelfTopLevel; $temp = $gShelfTopLevel;")
    return cmds.tabLayout(current_shelf, q=True, st=True)


def Leni_shelftools_toggle_height() -> None:
    """ toggle shelf height between one and three rows """
    current_shelf = Leni_shelftools_get_shelf()
    current_height = cmds.layout(current_shelf, q=True, height=True)

    current_rows = 1
    if current_height < 75:
        current_rows = 1
    elif current_height < 100:
        current_rows = 2
    else:
        current_rows = 0

    target_height = Leni_shelftools_height_in_pixel(current_rows + 1)
    Leni_shelftools_set_height(target_height)


def Leni_shelftools_height_in_pixel(rows: int = 1) -> int:
    """
    calculate shelf height from number of rows

    >>> Leni_shelftools_height_in_pixel()
    35

    :param rows: number of rows in shelf
    :return: shelf height in pixel
    """
    height = rows * SHELF_HEIGHT
    if rows > 1:
        height += rows * 2
    return height


def Leni_shelftools_set_height(height:int = SHELF_HEIGHT) -> None:
    """
    set shelf height

    :param height: height in pixel
    """
    current_shelf = Leni_shelftools_get_shelf()
    cmds.layout(current_shelf, edit=True, height=height)
