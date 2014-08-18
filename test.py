#!/usr/bin/env python
# coding: utf-8

import os
import mbuild
from mbuild.util import cd_path_context

def run():
    mbuild.main()

if __name__ == '__main__':
    with cd_path_context('F:\soft\Mail-Source\Email\AndroidMail'):
        print os.getcwd()
        run()

