# <> with ❤ by @LeniMagEsVonHinten

""" Collection of some basic samples for python scripts """

__all__ = ['hello_world']


def hello_world(name='World'):
    """Greet <name>.

    :param name: recipient. Defaults to 'World'.
    """
    print("Hello, {}!".format(name))


if __name__ == '__main__':
    hello_world()
