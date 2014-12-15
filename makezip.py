#!/usr/bin/evn python
# coding: utf-8

import os

from zipfile import ZipFile
from zipfile import ZIP_DEFLATED

def __addToZip(zf, path, zippath):
    if os.path.isfile(path):
        if not path.endswith(".pyc"):
            zf.write(path, zippath, ZIP_DEFLATED)
    elif os.path.isdir(path):
        for nm in os.listdir(path):
            __addToZip(zf, os.path.join(path, nm), os.path.join(zippath, nm))

def zip(target, *paths):
    dir, name = os.path.dirname(target), os.path.basename(target)

    if dir and not os.path.exists(dir):
        os.makedirs(dir)

    if not target.endswith('.zip'):
        target += '.zip'

    with ZipFile(target, 'w', compression=ZIP_DEFLATED) as zipfile:
        for path in paths:
            __addToZip(zipfile, path, os.path.basename(path))

if __name__ == '__main__':
    zip('lv/mbuild', '__main__.py', 'mbuild')
