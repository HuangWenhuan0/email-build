# coding: utf-8

import os
import sys
import contextlib
import hashlib
import shutil
import re
import subprocess

from contextlib import closing
from paramiko import SSHClient, RSAKey, AutoAddPolicy, Transport, config
from scpclient import Write
from pyjavaproperties import Properties

try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from os.path import join as _join
from os.path import exists as _exists


miui_res_filename = 'framework-miui-res.apk'
miui_res_dir      = 'MIUI_SDK'
project_filename  = 'project.properties'
url               = 'http://42.62.42.75:51866/build-conf2/'

if os.getenv('GIT_COMMIT ') is None:
    def get_git_commit_sha1():
        output = None
        try:
            cmd = ['git', 'log', '-1']
            commit = subprocess.check_output(cmd)
            output = StringIO(commit)
            return output.readline()[len('commit '):-1]
        finally:
            if output:
                output.close()
else:
    def get_git_commit_sha1():
        return os.environ['GIT_COMMIT']

def log(options, stdout=sys.stdout):
    format = '%-20s = %s'
    stdout.write('\n'.join([format % (key, value) for key, value in options.__dict__.items()]))
    stdout.write('\n')

@contextlib.contextmanager
def cd_path_context(_path):
    if _path:
        old_wd = os.getcwd()
        try:
            os.chdir(_path)
            yield
        finally:
            os.chdir(old_wd)

def is_mi_branch(branch_name):
    if not branch_name:
        raise ValueError('please specify current git branch name')

    keys = ('v5', 'v6')
    for key in keys:
        if key in branch_name:
            return True
    return False

def is_mi_v5(branch_name):
    return 'v5' in branch_name

def is_mi_v6(branch_name):
    return 'v6' in branch_name

def get_dependency_projects():
    if os.path.exists(project_filename):
        with open(project_filename) as fsock:
            properties = Properties()
            properties.load(fsock)

            project  = re.compile(r'android.library.reference.\d+')
            return (value for key, value in properties.items() if project.match(key))
    else:
        return []

def hash(_file, algorithms='md5'):
    try:
        func = getattr(hashlib, algorithms)()
    except AttributeError:
        return algorithms, None

    with open(_file, 'rb') as fsock:
        for line in fsock:
            func.update(line)

    return func.name.lower(), func.hexdigest()

def batch_hash(_file, *algorithms_list):
    for algorithms in algorithms_list:
        yield hash(_file, algorithms)

def rename(rootpath, **kwargs):
    for root, dirs, files in os.walk(rootpath):
        for sf, df in kwargs.items():
            if sf in files:
                src = os.path.join(root, sf)
                dst = os.path.join(root, df)
                print '[%-10s] %s -> %s' % (root, src, dst)
                shutil.move(src, dst)


def download_file_insecure(url, target):
    """
    Use Python to download the file, even though it cannot authenticate the
    connection.
    """
    src = urlopen(url)
    try:
        with open(target, 'wb') as dst:
            for line in src:
                dst.write(line)
    finally:
        src.close()

def cp_miui_res(_url=url):
    apk_path = os.path.join('../miui', miui_res_filename)
    if not _exists(apk_path):
        os.mkdir(os.path.dirname(apk_path))
        download_file_insecure(_url + miui_res_filename, apk_path)

     # current directory: copy miui-res.apk
    if not _exists(miui_res_dir):
        os.mkdir(miui_res_dir)

    shutil.copy2(apk_path, miui_res_dir)

    for dir in get_dependency_projects():
        dst_dir = os.path.join(dir, miui_res_dir)

        if not _exists(dst_dir):
            os.mkdir(dst_dir)

        if not _exists(_join(dst_dir, miui_res_filename)):
            shutil.copy2(apk_path, dst_dir)

def rm_miui_res():
    if _exists(miui_res_dir):
        shutil.rmtree(miui_res_dir)

    for dir in get_dependency_projects():
        dst_dir = _join(dir, miui_res_dir)
        if _exists(dst_dir):
            shutil.rmtree(dst_dir)

def get_prog():
    try:
        if os.path.basename(sys.argv[0]) in ('__main__.py', '-c'):
            return '%s -m mbuild' % sys.executable
    except:
        pass
    return 'mbuild'

def get_terminal_size():
    """Returns a tuple (x, y) representing the width(x) and the height(x)
    in characters of the terminal window."""
    def ioctl_GWINSZ(fd):
        try:
            import fcntl
            import termios
            import struct
            cr = struct.unpack(
                'hh',
                fcntl.ioctl(fd, termios.TIOCGWINSZ, '1234')
            )
        except:
            return None
        if cr == (0, 0):
            return None
        return cr
    cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
    if not cr:
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            cr = ioctl_GWINSZ(fd)
            os.close(fd)
        except:
            pass
    if not cr:
        cr = (os.environ.get('LINES', 25), os.environ.get('COLUMNS', 80))
    return int(cr[1]), int(cr[0])

def get_ssh_client(hostname, username, port=config.SSH_PORT,
                   password=None, pkey_filename=None, pkey=None):
    ssh = SSHClient()
    ssh.set_missing_host_key_policy(AutoAddPolicy())
    ssh.connect(hostname, port, username, password=password,
                key_filename=pkey_filename,
                pkey=pkey)
    return ssh

def scp_send_apk(localdir, remotedir,
             hostname, username, port=config.SSH_PORT,
             password=None, pkey_filename=None, pkey=None):
    def progress(remote_filename, size, file_pos):
        if file_pos == size:
            print '[%s:%s] Upload %s to %s complete' % (hostname, port, remote_filename, remotedir)

    ssh = get_ssh_client(hostname, username, port, password, pkey_filename, pkey)
    try:
        ssh.exec_command('rm -fr %s' % remotedir)
        ssh.exec_command('mkdir -p %s' % remotedir)

        with closing(Write(ssh.get_transport(), remotedir)) as scp:
            for root, dirs, files in os.walk(localdir):
                for file in files:
                    if file.endswith('.apk'):
                        scp.send_file(os.path.join(root, file), progress=progress)
    finally:
        ssh.close()