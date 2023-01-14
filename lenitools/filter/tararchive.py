# <> with ❤ by @LeniMagEsVonHinten

import os

__all__ = ['Leni_filter_tarmembersuffix']


def Leni_filter_tarmembersuffix(members, suffix: str = '.txt'):
    for tarinfo in members:
        if os.path.splitext(tarinfo.name)[1] == suffix:
            yield tarinfo
