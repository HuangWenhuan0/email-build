#!/usr/bin/env python

import mbuild

def run():
    mbuild.main()

if __name__ == '__main__':
    # from mbuild.util import cd_path_context
    # with cd_path_context(r'E:\Program Files (x86)\Sources\Email\AndroidMail'):
    #     run()

    import os
    print os.getcwd()
    run()