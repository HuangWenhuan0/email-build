# coding:utf-8

import os
import platform
import sys
import build

if __name__ == '__main__':
    osname = platform.system()
    if osname == 'Windows':
        os.chdir('F:\soft\Mail-Source\Email\AndroidMail')
    elif osname == 'Linux':
        os.chdir('/home/huangwenhuan/git/Email/AndroidMail')
    else:
        sys.exit(1)

    build.main()