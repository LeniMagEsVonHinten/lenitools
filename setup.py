#!/usr/bin/env python3
from setuptools import setup

try:
    from babel.messages import frontend as babel
except (ModuleNotFoundError, ImportError):
    pass

setup(
    name='leni-tools',
    version='1.0',
    packages=['lenitools'],
    url='https://github.com/lenimagesvonhinten/leni-tools',
    license='Apache 2.0 License',
    author='Leni mag es von Hinten',
    author_email='leni.mag.es.von.hinten@googlemail.com',
    description='',
    cmdclass={
        'compile_catalog': babel.compile_catalog,
        'extract_messages': babel.extract_messages,
        'init_catalog': babel.init_catalog,
        'update_catalog': babel.update_catalog
    }
)
