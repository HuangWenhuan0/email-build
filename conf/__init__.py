# coding: utf-8

import sys
import os
import tarfile
import base64

def make_ant_tar_gz():
    paths = ('com.android.email', 'com.kingsoft.email', 'build.xml', 'mo-ant-tasks.jar')
    tar = tarfile.open('ant.tar.gz', mode='w|gz')
    try:
        for path in paths:
            tar.add(path)
    finally:
        tar.close()


def make_base64():
    input  = open('ant.tar.gz', mode='rb')
    output = open('ant.tar.gz.base64', 'wb')

    try:
        base64.encode(input, output)
    finally:
        input.close()
        output.close()

if __name__ == '__main__':
    make_ant_tar_gz()
    make_base64()