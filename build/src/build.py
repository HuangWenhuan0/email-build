# coding: utf-8

import sys
import os
import hashlib
import optparse
import subprocess
import contextlib
import shutil

import platform
import re

from lxml import etree
from pyjavaproperties import Properties

from os.path import exists as _exists
from os.path import join as _join

try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

reload(sys).setdefaultencoding('utf-8')

sdk_cfg            = 'sdk.cfg'
sdk_props_filename = 'sdk.properties'
res_filename       = 'framework-miui-res.apk'
res_dir            = 'MIUI_SDK'
res_relative_path  = os.path.join(os.path.curdir, res_dir, res_filename)
project_filename   = 'project.properties'

ANDROID_MANIFEST_XML = 'AndroidManifest.xml'
NAMESPACES           = {'android' : 'http://schemas.android.com/apk/res/android'}

def _python_cmd(*args):
    """
    Return True if the command succeeded
    """
    args = (sys.executable, ) + args
    return subprocess.call(args) == 0

def _clean_check(cmd, target):
    """
    Run the command to download target. If the command fails, clean up before
    re-raising the error.
    """
    try:
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError:
        if os.access(target, os.F_OK):
            os.unlink(target)

def _check_output(cmd):
    """
    Run the command. If the command fails, None is returned
    """
    try:
        return subprocess.check_output(cmd)
    except subprocess.CalledProcessError:
        pass

def download_file_axel(url, target):
    from multiprocessing import cpu_count
    cmd = ['axel', url, '--quiet', '--num-connections', str(cpu_count()), '--output', target]
    _clean_check(cmd, target)

def has_axel():
    cmd = ['axel', '--version']
    with open(os.path.devnull, 'wb') as devnull:
        try:
            subprocess.check_call(cmd, stdout=devnull, stderr=devnull)
        except Exception:
            return False
    return True

download_file_axel.viable = has_axel

def download_file_curl(url, target):
    cmd = ['curl', url, '--silent', '--output', target]
    _clean_check(cmd, target)

def has_curl():
    cmd = ['curl', '--version']
    with open(os.path.devnull, 'wb') as devnull:
        try:
            subprocess.check_call(cmd, stdout=devnull, stderr=devnull)
        except Exception:
            return False
    return True

download_file_curl.viable = has_curl

def download_file_wget(url, target):
    cmd = ['wget', url, '--quiet', '--output-document', target]
    _clean_check(cmd, target)

def has_wget():
    cmd = ['wget', '--version']
    with open(os.path.devnull, 'wb') as devnull:
        try:
            subprocess.check_call(cmd, stdout=devnull, stderr=devnull)
        except Exception:
            return False
    return True

download_file_wget.viable = has_wget

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

download_file_insecure.viable = lambda: True

def get_best_downloader():
    downloaders = (
        download_file_axel,
        download_file_curl,
        download_file_wget,
        download_file_insecure,
    )
    viable_downloaders = (dl for dl in downloaders if dl.viable())
    return next(viable_downloaders, None)


@contextlib.contextmanager
def print_context(prompt=None, out=None):
    def _():
        if out is None:
            print
        else:
            print out

    try:
        if prompt is not None:
            print '%s' % (prompt)
        _()
        yield
    finally:
        _()

@contextlib.contextmanager
def cd_path_context(_path):
    if _path is not None and _path != '':
        old_wd = os.getcwd()
        try:
            os.chdir(_path)
            yield
        finally:
            os.chdir(old_wd)


def hash(_file, _type='md5'):
    try:
        f = getattr(hashlib, _type)()
    except AttributeError:
        return _type, None

    with open(_file, 'rb') as fsock:
        for line in fsock:
            f.update(line)

    return f.name.lower(), f.hexdigest()

def get_git_commit_sha1():
    try:
        cmd = ['git', 'log', '-1']
        commit = subprocess.check_output(cmd)
        output = StringIO(commit)
        return output.readline()[len('commit '):-1]
    finally:
        output.close()

def rename(rootpath, **kwargs):
    with print_context():
        for root, dirs, files in os.walk(rootpath):
            for sf, df in kwargs.items():
                if sf in files:
                    src = os.path.join(root, sf)
                    dst = os.path.join(root, df)
                    print '[%-10s] %s -> %s' % (root, src, dst)
                    shutil.move(src, dst)

def ant(mode):
    ant_cmd = 'ant clean %s | tee -a ant-build.log'
    rv = os.system(ant_cmd % mode)
    return rv == 0

def publish(options):
    publish_dir = '%s/%s/%s' % (options.mode, options.channel, options.commit_id)
    if not os.path.exists(publish_dir):
        os.makedirs(publish_dir)

    apk_name = '%s_%s_%s.apk' % (options.apk_prefix, options.channel, options.commit_id[:7])
    src_apk = 'bin/AndroidMail-%s.apk' % options.mode
    dst_apk = '%s/%s' % (publish_dir, apk_name)

    shutil.copy2(src_apk, dst_apk)
    shutil.copy2('ant-build.log', publish_dir)
    shutil.copy2(ANDROID_MANIFEST_XML, publish_dir)

    # make md5 sum file
    with cd_path_context(publish_dir):
        type, md5_value = hash(apk_name)
        setattr(options, type, md5_value)

        with open('%s.%s' % (apk_name, type), 'w+') as fmd5:
            fmd5.write(md5_value)

        with open('build.log', 'w+') as build_log:
            log(options, build_log)

    os.system('rm -fr bin/classes bin/*_ bin/*.d bin/*.apk')
    os.system('tar zcf %s/src.tar.gz src gen bin/*' % publish_dir)

def log(options, stdout=sys.stdout):
    format = '%-20s = %s'
    stdout.write('\n'.join([format % (key, value) for key, value in options.__dict__.items()]))
    stdout.write('\n')

def cleanup(all=False):
    tmp_files = ['ant-build.log', 'build.log', 'build.zip']
    for file in tmp_files:
        if os.path.exists(file): os.remove(file)

    if all:
        tmp_dirs = ['build', 'MIUI_SDK']
        for dir in tmp_dirs:
            if _exists(dir): shutil.rmtree(dir)

def backup(options):
    if not os.path.exists(options.commit_id):
        os.mkdir(options.commit_id)

    tar_cmd = 'tar zcf %s/backup.tar.gz assets res src *.xml *.properties'
    os.system(tar_cmd % options.commit_id)

def restore(options):
    os.system('rm -fr assets res src *.xml *.properties *.md5 *.cfg')
    os.system('tar zxf %s/backup.tar.gz' % options.commit_id)

    shutil.rmtree(options.commit_id)
    SdkSetup.rm_miui_res()

@contextlib.contextmanager
def build_context(options):
    def modify_project_code():
        manifest = AndroidManifest()
        manifest.set_package_name(options.package_name)
        manifest.set_version_code(options.version_code)
        manifest.set_version_name(options.version_name)
        manifest.set_channel(options.channel)
        manifest.set_commit_id(options.commit_id)
        manifest.set_debuggable(options.debuggable)
        manifest.set_db_version_code(options.db_version_code)
        manifest.save()

        files = {'ksMailTemplate_mixed.html': 'ksMailTemplate.html',
                 'ksMailView_mixed.js': 'ksMailView.js'}
        rename('assets', **files);

    def mk_sdk():
        ismi = SdkSetup.is_mi_branch(options.branch_name)
        SdkSetup.mk_sdk(ismi, conf=options.build_conf, overwrite=options.overwrite, verbose=options.verbose)

    try:
        cleanup()
        backup(options)

        mk_sdk()
        modify_project_code()

        yield
    finally:
        cleanup(all=True)
        restore(options)


class SdkSetup(object):

    # @staticmethod
    # def mk_sdk(ismi=False, overwrite=False, verbose=False):
    #     with open(sdk_cfg) as cfg:
    #         props = Properties()
    #         props.load(cfg)
    #
    #     with open(sdk_props_filename, 'w+') as fsock:
    #         osname = platform.system()
    #
    #         if ismi:
    #             key = '%s_mi' % osname
    #         else:
    #             key = osname
    #
    #         value = props[key]
    #
    #         if ismi and value is not '':
    #             SdkSetup.cp_miui_res(overwrite, verbose)
    #
    #         if value is not '':
    #             fsock.write('sdk.dir=%s' % value)
    #             return 0
    #         else:
    #             print "# current platform %s doesn't supported!" % platform.system()
    #             return 1

    LAN_CONF = {'Windows': 'E:/android/sdk/android-sdk_r22.6.2-windows',
                'Windows_mi': 'E:/android/sdk/android-miui-sdk_r22.6.2-windows',
                'Linux': '/opt/android-sdk_r22.6.2-linux',
                'Linux_mi': '/opt/android-miui-sdk_r16-linux'}

    WAN_CONF = {'Windows': 'E:/android/sdk/android-sdk_r22.6.2-windows',
                'Windows_mi': 'E:/android/sdk/android-miui-sdk_r22.6.2-windows',
                'Linux': '/data/hudson/android-sdk_r22.6.2-linux',
                'Linux_mi': '/data/hudson/android-miui-sdk_r16-linux'}

    URL = 'http://42.62.42.75:51866/build-conf2/'

    @staticmethod
    def mk_sdk(ismi=False, conf=LAN_CONF, overwrite=False, verbose=False):
        with open(sdk_props_filename, 'w+') as fsock:
            osname = platform.system()
            key = ismi and ('%s_mi' % osname) or (osname)
            SdkSetup.cp_miui_res(overwrite, verbose)
            fsock.write('sdk.dir=%s' % conf[key])

    @staticmethod
    def get_dependency_projects():
        if os.path.exists(project_filename):
            with open(project_filename) as fsock:
                properties = Properties()
                properties.load(fsock)

                project  = re.compile(r'android.library.reference.\d+')
                return (value for key, value in properties.items() if project.match(key))
        else:
            return []

    @staticmethod
    @contextlib.contextmanager
    def mi_res_context(overwrite=False, verbose=False):
        def __mi_res_file_exists():
            return _exists(_join(os.getcwd(), res_relative_path))

        def __mi_res_dir_exists():
            return _exists(res_dir)

        def __is_android_project():
            return os.path.exists(project_filename)

        try:
            # delete 'framework-miui-res.apk''s parent directory
            if __mi_res_file_exists() and overwrite:
                if verbose: print "# delete framework-miui-res.apk file's parent directory %s" % _join(os.getcwd(), res_dir)
                shutil.rmtree(res_dir)

            if not __mi_res_dir_exists():
                if verbose: print '# mkdir %s directory in %s' % (res_dir, os.getcwd())
                os.mkdir(res_dir)

            # if 'framework-miui-res.apk' file doesn't exists, download it
            if not __mi_res_file_exists():
                if __is_android_project():
                    if verbose: print '# download %s to %s' % (res_filename, _join(os.getcwd(), res_dir))
                    from build import get_best_downloader as _down
                    _down()(SdkSetup.URL + res_filename, res_relative_path)
                else:
                    print '# current directory is not android project'
                    sys.exit(2)

            for dir in SdkSetup.get_dependency_projects():
                dst_dir = _join(dir, res_dir)
                if _exists(dst_dir) and overwrite:
                    if verbose: print '# delete %s directory' % dst_dir
                    shutil.rmtree(dst_dir)
            yield
        finally:
            pass

    @staticmethod
    def cp_miui_res(overwrite=False, verbose=False):
        with SdkSetup.mi_res_context(overwrite, verbose):
            project_dirs = SdkSetup.get_dependency_projects()

            for dir in project_dirs:
                dst_dir = os.path.join(dir, res_dir)

                if not _exists(dst_dir):
                    if verbose: print '# make %s directory' % dst_dir
                    os.mkdir(dst_dir)

                if not _exists(_join(dst_dir, res_filename)):
                    if verbose: print '# copy %s file to %s' % (res_relative_path, dst_dir)
                    shutil.copy2(res_relative_path, dst_dir)

    @staticmethod
    def rm_miui_res():
        for dir in SdkSetup.get_dependency_projects():
            dst_dir = _join(dir, res_dir)
            if _exists(dst_dir):
                shutil.rmtree(dst_dir)

    @staticmethod
    def _parse_args():
        parser = optparse.OptionParser()
        parser.add_option(
            '-b', '--branch-name', dest='branch_name', default=None,
            metavar='BRANCH-NAME',
            help='specify branch name (not null)')
        parser.add_option(
            '-q', '--quiet', dest='verbose', action='store_false', default=True,
            help="slient mode, don't print debug info")
        parser.add_option(
            '-o', '--overwrite', dest='overwrite', action='store_true', default=False,
            help='overwrite mi_res_apk')

        options, args = parser.parse_args()
        return options

    @staticmethod
    def is_mi_branch(branch_name):
        keys = ('mi', 'miui')
        for key in keys:
            if key in branch_name:
                return True
        return False

class AndroidManifest(object):

    xpath_package_name       = '/manifest[@package]'
    xpath_version_code       = '/manifest[@android:versionCode]'
    xpath_version_name       = '/manifest[@android:versionName]'
    xpath_debuggable         = '/manifest/application[@android:debuggable]'

    _xpath_meta_data_node    = '/manifest/application/meta-data[@android:name="%s"]'
    xpath_db_version_code    = _xpath_meta_data_node % 'db_versionCode'
    xpath_channel            = _xpath_meta_data_node % 'channel'
    xpath_default_searchable = _xpath_meta_data_node % 'android.app.default_searchable'
    xpath_commit_id          = _xpath_meta_data_node % 'commit_id'

    attr_name_package     = 'package'
    attr_name_versionCode = 'android:versionCode'
    attr_name_versionName = 'android:versionName'
    attr_name_debuggable  = 'android:debuggable'
    attr_name_value       = 'android:value'

    def __init__(self, manifest=ANDROID_MANIFEST_XML):
        self.doc = etree.parse(manifest)
        self.def_package_name    = self._get(self.xpath_package_name, self.attr_name_package)
        self.def_version_code    = self._get(self.xpath_version_code, self.attr_name_versionCode)
        self.def_version_name    = self._get(self.xpath_version_name, self.attr_name_versionName)
        self.def_debuggable      = self._get(self.xpath_debuggable, self.attr_name_debuggable)

        self.def_db_version_code = self._get(self.xpath_db_version_code, self.attr_name_value)
        self.def_channel         = self._get(self.xpath_channel, self.attr_name_value)
        self.def_searchable      = self._get(self.xpath_default_searchable, self.attr_name_value)
        self.commit_id           = self._get(self.xpath_commit_id, self.attr_name_value)

        self.dirty = False

    @staticmethod
    def _convert_attr_name(attr_name):
        if 'android:' in attr_name:
            return attr_name.replace('android:', '{%s}' % NAMESPACES['android'])
        else:
            return attr_name

    def _get(self, xpath, _attr_name):
        _attr_name = AndroidManifest._convert_attr_name(_attr_name)
        nodes = self.doc.xpath(xpath, namespaces=NAMESPACES)

        assert len(nodes) == 1

        for node in nodes:
            for attr_name, attr_value in node.items():
                if attr_name == _attr_name:
                    return attr_value

    def set(self, xpath, _attr_name, _attr_value):
        _attr_name = self._convert_attr_name(_attr_name)
        nodes = self.doc.xpath(xpath, namespaces=NAMESPACES)
        for node in nodes:
            for attr_name, attr_value in node.items():
                if attr_name == _attr_name and attr_value != _attr_value:
                    node.set(_attr_name, _attr_value)

                    if not self.dirty:
                        self.dirty = True

    def set_package_name(self, package_name):
        if package_name is not None and package_name != self.def_package_name:
            self.set(self.xpath_package_name, 'package', package_name)

            # res/xml directory
            scmd_email_np = "sed -i 's#xmlns:email=\"http://schemas.android.com/apk/res/%s\"#xmlns:email=\"http://schemas.android.com/apk/res/%s\"#' res/xml/%s"
            files = ['email_server_list.xml', 'services.xml']
            for file in files:
                os.system(scmd_email_np % (self.def_package_name, package_name, file))

            # res/drawable directory
            scmd_app_np = "sed -i 's#xmlns:app=\"http://schemas.android.com/apk/res/%s\"#xmlns:app=\"http://schemas.android.com/apk/res/%s\"#' res/drawable/%s"
            files = ['ic_folder_drafts.xml',    'ic_folder_inbox.xml',
                     'ic_folder_outbox.xml',    'ic_folder_sent.xml',
                     'ic_folder_star.xml',      'ic_folder_trash.xml',
                     'ic_folder_unkown.xml',    'ic_folder_unread.xml']
            for file in files:
                os.system(scmd_app_np % (self.def_package_name, package_name, file))

            # res/layout directory
            scmd_app_np = "sed -i 's#xmlns:app=\"http://schemas.android.com/apk/res/%s\"#xmlns:app=\"http://schemas.android.com/apk/res/%s\"#' res/layout/%s"
            files = ['cc_bcc_view.xml', 'compose_recipients.xml']
            for file in files:
                os.system(scmd_app_np % (self.def_package_name, package_name, file))

    def set_version_code(self, version_code):
        if version_code is not None and version_code != self.def_version_code:
            self.set(self.xpath_version_code, self.attr_name_versionCode, version_code)

    def set_version_name(self, version_name):
        if version_name is not None and version_name != self.def_version_name:
            self.set(self.xpath_version_name, self.attr_name_versionName, version_name)

    def set_debuggable(self, debuggable):
        if debuggable is not None and debuggable != self.def_debuggable:
            self.set(self.xpath_debuggable, self.attr_name_debuggable, str(debuggable).lower())

    def set_db_version_code(self, db_version_code):
        if db_version_code is not None and db_version_code != self.def_db_version_code:
            import types
            if type(db_version_code) is types.IntType:
                db_version_code = str(db_version_code)
            self.set(self.xpath_db_version_code, self.attr_name_value, db_version_code)

    def set_channel(self, channel):
        if channel is not None and channel != self.def_channel:
            self.set(self.xpath_channel, self.attr_name_value, channel)

    def set_commit_id(self, commit_id):
        if commit_id is not None and commit_id != self.commit_id:
            self.set(self.xpath_commit_id, self.attr_name_value, commit_id)

    def set_searchable(self, searchable):
        if searchable is not None and searchable != self.def_searchable:
            self.set(self.xpath_default_searchable, self.attr_name_value, searchable)

    def tostring(self, format=None):
        if format is None:  format = '%-20s = %s'
        props = [format % ('package', self._get(self.xpath_package_name, self.attr_name_package)),
                 format % ('android:versionCode', self._get(self.xpath_version_code, self.attr_name_versionCode)),
                 format % ('android:versionName', self._get(self.xpath_version_name, self.attr_name_versionName)),
                 format % ('debuggable', self._get(self.xpath_debuggable, self.attr_name_debuggable)),
                 format % ('db_versionCode', self._get(self.xpath_db_version_code, self.attr_name_value)),
                 format % ('channel', self._get(self.xpath_channel, self.attr_name_value)),
                 format % ('commit_id', self._get(self.xpath_commit_id, self.attr_name_value)),
                 format % ('def_searchable', self._get(self.xpath_default_searchable, self.attr_name_value))]
        return '\n'.join(props)

    def save(self):
        if self.dirty:
            self.doc.write(ANDROID_MANIFEST_XML, xml_declaration=True, encoding='utf-8')

    def __str__(self):
        return self.tostring()


def _parse_args(androidmanifest):
    """
    Parse command line for option
    """
    parser = optparse.OptionParser()
    parser.add_option(
        '-c', '--channel', dest='channel', default='dev',
        metavar='CHANNEL',
        help='use specified channel')
    parser.add_option(
        '-g', '--debuggable', dest='debuggable', action='store_true', default=False,
        help='debug or release, (release is default value)')
    parser.add_option(
        '-p', '--package-name', dest='package_name', default=androidmanifest.def_package_name,
        metavar='PACKAGE-NAME',
        help='use specified package name to make apk')
    parser.add_option(
        '-b', '--enable-branch-name', dest='enable_branch_name', action='store_false', default=False,
        help='enable branch name as application name')
    parser.add_option(
        '--display-name', dest='display_name', default=None,
        metavar='DISPLAY-NAME',
        help='specify display name when the apk is installed')
    parser.add_option(
        '--version-name', dest='version_name', default=androidmanifest.def_version_name,
        metavar='VERSION-NAME',
        help='specify app version name (android:versionName="")')
    parser.add_option(
        '--version-code', dest='version_code', default=androidmanifest.def_version_code,
        metavar='VERSION-CODE',
        help='specify app version code (android:versionCode=""')
    parser.add_option(
        '--db-version-code', dest='db_version_code', default=androidmanifest.def_db_version_code,
        metavar='DB-VERSION-CODE',
        help='specify app dbVersionCode (<meta-data android:name="db_versionCode", android:value="")')
    parser.add_option(
        '--apk-prefix', dest='apk_prefix', default='WpsMail',
        metavar='APK-PREFIX',
        help='specify apk prefix name (default is WpsMail)')
    parser.add_option(
        '--branch-name', dest='branch_name', default=None,
        metavar='BRANCH-NAME',
        help='specify branch name (not null)')
    parser.add_option(
        '--wan', dest='iswan', action='store_true', default=False,
        help='download build configuration form wan, else form lan')
    parser.add_option(
        '-q', '--quiet', dest='verbose', action='store_false', default=True,
        help="don't print log information")
    parser.add_option(
        '-o', '--overwrite', dest='overwrite', action='store_true', default=False,
        help='overwrite mi_res_apk')

    options, args = parser.parse_args()

    options.mode = options.debuggable and 'debug' or 'release'
    options.build_conf = options.iswan and SdkSetup.WAN_CONF or SdkSetup.LAN_CONF
    options.commit_id = get_git_commit_sha1()
    options.is_mi_branch = SdkSetup.is_mi_branch(options.branch_name)

    for key, value in options.__dict__.items():
        if type(value) is str and not isinstance(value, unicode):
            try:
                setattr(options, key, unicode(value, 'gb2312'))
            except UnicodeDecodeError as e:
                print '%-20s = %-10s, %s' % (key, value, type(value))

    return options

def _download_build_conf(options):
    down = get_best_downloader()
    overwrite = options.overwrite

    def get(url, target):
        if url is not None and url != '':
            if not _exists(target):
                down(url, target)
            else:
                if overwrite:
                    os.remove(target)
                    down(url, target)

    def build_common_xml_path():
        if options.is_mi_branch:
            return 'ant/%s/build.zip' % 'com.android.email'
        else:
            return 'ant/%s/build.zip' % 'com.kingsoft.email'

    url = SdkSetup.URL
    files = {url + 'build.xml': 'build.xml',
             url + build_common_xml_path() : 'build.zip'}

    for url, target in files.items():
        get(url, target)

    os.system('unzip -o -q build.zip')

def main():
    manifest = AndroidManifest()
    options = _parse_args(manifest)

    _download_build_conf(options)

    with print_context('[Original AndroidManifest Property]'):
        print manifest

    with build_context(options):
        if ant(options.mode):
            publish(options)

            with print_context('[Final AndroidManifest Property]'):
                print AndroidManifest()

            with print_context('[Final Options]'):
                log(options)

if __name__ == '__main__':
    main()