# coding: utf-8
#
# author:
#   HuangWenhuan    <huangwenhuan1125@gmail.com>
#

import os
import sys
import contextlib
import shutil
import tarfile
import logging
import re
import base64
import hashlib

from mbuild.util import is_mi_branch
from mbuild.util import rename
from mbuild.util import cp_miui_res
from mbuild.util import rm_miui_res
from mbuild.util import cd_path_context
from mbuild.util import batch_hash
from mbuild.util import is_mi_v5
from mbuild.util import is_mi_v6

from mbuild.androidmanifest import ANDROID_MANIFEST_XML
from mbuild.androidmanifest import AndroidManifest

from os.path import exists as _exists

reload(sys).setdefaultencoding('utf-8')

class Build(object):

    BUILD_CONF = None
    TEMP_FILES = None
    TEMP_DIRS  = None

    _BACKUP_DIRS  = ('assets', 'res', 'src')
    _BACKUP_FILES = ('.xml', '.properties', '.md5', '.cfg')

    # *.apk *.d *_ classes
    SRC_PATTERN = re.compile(r'(^(bin)+[^\/:*?"<>|]+((\.apk$)|(\.d$)|(_$)))|(.*classes$)')
    SRC_DIRS = ('src', 'gen', 'bin')

    WPS_PACKAGE_NAME = 'com.kingsoft.email'
    MI_PACKAGE_NAME  = 'com.android.email'

    APK_NAME_FORMAT = {
        '%prefix':          'apk_prefix',
        '%channel':         'channel',
        '%versionName':     'version_name',
        '%versionCode':     'version_code',
        '%commitId':        'commit_id',
        '%dbVersoinCode':   'db_version_code',
        '%packageName':     'package_name'
        }

    def __init__(self, options, verbose=False, ismi=is_mi_branch):
        self.backup_file = None
        self.cmd_line_build_file = None
        self.build_temp_files = []

        self.options = options
        self.verbose = verbose

        self.commit_id = options.commit_id
        self.channel = options.channel
        self.download_url = options.download_url
        self.mode = 'debug' if options.debug else 'release'
        self.hash_algorithms = ['md5', 'sha1']

        self.__process_branch_name(ismi)
        self.__process_hash_types()

    def __process_branch_name(self, ismi=is_mi_branch):
        branch_name = os.getenv('GIT_BRANCH')
        if branch_name:
            self.ismi = ismi(branch_name)
            self.branch_name = branch_name
        else:
            if self.options.branch_name:
                self.ismi = ismi(self.options.branch_name)
                self.branch_name = self.options.branch_name
            else:
                logging.error('please specify current git branch name')
                sys.exit(1)

    def __process_hash_types(self):
        try:
            algorithms = [t.strip() for t in self.options.hash_types.split(',')]
            del self.hash_algorithms[:]

            for algorithm in algorithms:
                if algorithm in hashlib.algorithms:
                    self.hash_algorithms.append(algorithm)
                else:
                    print '%s is supported algorithms' % algorithm
        except:
            pass

    def build(self):
        pass

    def publish(self):
        options = self.options

        publish_dir = '%s/%s/%s' % (options.mode, options.channel, options.commit_id)
        if not os.path.exists(publish_dir):
            os.makedirs(publish_dir)


        apk_name = self._expand_apk_name(options.apk_name_format)
        src_apk = self._get_original_apk_path()
        dst_apk = '%s/%s' % (publish_dir, apk_name)

        shutil.copy2(src_apk, dst_apk)
        if self.cmd_line_build_file is not None:
            shutil.copy2(self.cmd_line_build_file, publish_dir)
        shutil.copy2(ANDROID_MANIFEST_XML, publish_dir)

        with cd_path_context(publish_dir):
            # make hash algorithms for apk
            checksum_name = '%s.%s' % (apk_name, 'checksum')
            with open(checksum_name, 'w+') as checksum_fobj:
                # algorithms_list = ('md5', 'sha1')
                for type, value in batch_hash(apk_name, *self.hash_algorithms):
                    setattr(self.options, type, value)
                    checksum_fobj.writelines('*%-7s %s\n' % (type, value))

            # write options to file
            with open('build.log', 'w') as build_log_fobj:
                from mbuild.util import log
                log(self.options, build_log_fobj)

        # make src compress file
        if os.getenv('publish_src'):
            archive_name = '%s/src.tar.gz' % os.path.curdir
            exclude = lambda name: self.SRC_PATTERN.match(name)
            with tarfile.open(archive_name, mode='w|gz') as tar:
                for dir in self.SRC_DIRS:
                    tar.add(dir, exclude=exclude)

        options.apk_path = os.path.join(os.getcwd(), dst_apk)


    def _get_original_apk_path(self):
        pass

    def clean(self, all=False):
        for file in self.TEMP_FILES:
            if _exists(file):
                os.remove(file)

        if all:
            for dir in self.TEMP_DIRS:
                if _exists(dir):
                    shutil.rmtree(dir)

    def backup(self):
        """
        backup project file
        """
        if not _exists(self.commit_id):
            os.mkdir(self.commit_id)

        dirs = self._BACKUP_DIRS
        files_suffix = self._BACKUP_FILES

        tar = tarfile.open('%s/backup.tar.gz' % self.commit_id, mode='w|gz')
        try:
            for name in os.listdir(os.path.curdir):
                if os.path.isdir(name):
                    if name in dirs:
                        if self.verbose:
                            print '\tAdd %s directory' % name
                        tar.add(name)

                if os.path.isfile(name):
                    for suffix in files_suffix:
                        if name.endswith(suffix):
                            if self.verbose:
                                print '\tAdd %s file' % name
                            tar.add(name)
        finally:
            tar.close()

        self.backup_file = os.path.abspath('%s/backup.tar.gz' % self.commit_id)

    def restore(self):
        """
        restore project file
        """
        if self.backup_file is None:
            return

        dirs = self._BACKUP_DIRS
        files_suffix = self._BACKUP_FILES

        # delete
        for name in os.listdir(os.path.curdir):
            if os.path.isdir(name):
                if name in dirs:
                    shutil.rmtree(name)

            if os.path.isfile(name):
                for suffix in files_suffix:
                    if name.endswith(suffix):
                        os.remove(name)

        #restore
        tar = tarfile.open(self.backup_file, mode='r|gz')
        try:
            tar.extractall(os.path.curdir)
        finally:
            tar.close()

        shutil.rmtree(self.commit_id)

        if is_mi_v5(self.branch_name):
            rm_miui_res()

    def revise_file(self, manifest):
        self._revise_android_manifest(manifest)
        self._revise_build_conf()
        self._revise_other_file()

    def _revise_android_manifest(self,manifest):
        if not isinstance(manifest, AndroidManifest):
            raise TypeError, 'not an AndroidManifest instance: %r' % manifest

        def _filter(options):
            from mbuild import androidmanifest as __amft
            if (options.version_code == AndroidManifest.DEFAULT):
                options.version_code = __amft.VERSION_CODE
            if (options.version_name == AndroidManifest.DEFAULT):
                options.version_name = __amft.VERSOIN_NAME
            return options

        options = _filter(self.options)

        manifest.set_package_name(options.package_name)
        manifest.set_version_code(options.version_code)
        manifest.set_version_name(options.version_name)
        manifest.set_channel(options.channel)
        manifest.set_commit_id(options.commit_id)
        manifest.set_debuggable(options.debug)
        manifest.save()

    def _revise_other_file(self):
        # rename files
        files = {
            'ksMailTemplate_mixed.html': 'ksMailTemplate.html',
            'ksMailView_mixed.js': 'ksMailView.js'
        }
        rename('assets', **files)

    def _revise_build_conf(self):
        pass

    def _setup_sdk(self, sdk_environ_key='ANDROID_HOME'):
        # configure sdk directory
        key = None
        try:
            # remove 'sdk.properties' file
            sdk_prop_file = 'sdk.properties'
            if os.path.exists(sdk_prop_file):
                os.remove(sdk_prop_file)

            # set 'ANDROID_HOME' environment variable
            if is_mi_v5(self.branch_name):
                key = 'MI_V5_SDK'
            elif is_mi_v6(self.branch_name):
                key = 'MI_V6_SDK'
            else:
                key = 'ANDROID_SDK'
            os.environ[sdk_environ_key] = os.environ[key]
        except KeyError as e:
            print '%s, please set %s environment variable' % (e, key)
            sys.exit(1)

        # configure miui resource apk
        if is_mi_v5(self.branch_name):
            cp_miui_res(self.download_url)

    def _expand_apk_name(self, format):
        import copy
        apk_name = copy.deepcopy(format)

        for format, attr_name in self.APK_NAME_FORMAT.items():
            value = None
            try:
                value = getattr(self.options, attr_name)
                if format.lower() == '%commitId'.lower():
                    value = value[:7]
            except:
                value = format

            if value is not None:
                apk_name = apk_name.replace(format, value)

        return apk_name if apk_name.endswith('.apk') else apk_name + '.apk'

    def _log_time(self, prompt):
        import time
        print '%s - %s' % (prompt, time.ctime()[4:])

    @contextlib.contextmanager
    def prepare(self, manifest, sdk_environ_key='ANDROID_HOME'):
        try:
            self._log_time('Build start at')
            self.clean()
            self.backup()

            # configure android sdk
            self._setup_sdk(sdk_environ_key)

            # modify android manifest file, build configuration file and other file
            self.revise_file(manifest)

            yield
        finally:
            self.clean(True)
            self.restore()
            self._log_time('Build end at')


class AntBuild(Build):

    BUILD_CONF = 'build.xml'
    TEMP_FILES = ('ant-build.log', 'build.log', 'build.zip')
    TEMP_DIRS  = ('build', 'MIUI_SDK')
    ANT_FILE_NAME = 'ant.tar.gz'

    def __init__(self, options, verbose=False, ismi=is_mi_branch):
        super(AntBuild, self).__init__(options, verbose, ismi)
        self.task = 'debug' if options.debug else 'release'

    def _revise_build_conf(self):
        super(AntBuild, self)._revise_build_conf()

        # make build.xml
        with open(self.ANT_FILE_NAME, 'wb') as fp:
            from mbuild import ANTFILE
            fp.write(base64.decodestring(ANTFILE))

        self.build_temp_files.append(self.ANT_FILE_NAME)

        with tarfile.open(self.ANT_FILE_NAME, mode='r:gz') as tar:
            for member in tar.getmembers():
                if member.isfile():
                    path, name = os.path.dirname(member.name), os.path.basename(member.name)

                    if self.ismi and path ==self.WPS_PACKAGE_NAME: continue
                    if not self.ismi and path == self.MI_PACKAGE_NAME: continue

                    tar.makefile(member, targetpath=name)

                    self.build_temp_files.append(name)

    def clean(self, all=False):
        super(AntBuild, self).clean(all)

        if all:
            for build_file in self.build_temp_files:
                if _exists(build_file):
                    os.remove(build_file)

    def build(self):
        self.cmd_line_build_file = 'ant-build.log'
        ant_cmd = 'ant clean %s | tee -a %s'
        return os.system(ant_cmd % (self.task, self.cmd_line_build_file)) == 0

    def _get_original_apk_path(self):
        return 'bin/AndroidMail-%s.apk' % self.mode


class GradleBuild(Build):

    BUILD_CONF = 'build.gradle'
    TEMP_FILES = ('gradle-build.log', 'build.log', 'build.zip')
    TEMP_DIRS  = ('MIUI_SDK')

    def __init__(self, options, verbose=False, ismi=is_mi_branch):
        super(GradleBuild, self).__init__(options, verbose, ismi)
        self.task = 'assembleDebug' if options.debug else 'assembleRelease'

    def build(self):
        self.cmd_line_build_file = 'gradle-build.log'
        gradle_cmd = 'gradle clean %s | tee -a %s'
        return os.system(gradle_cmd % (self.task, self.cmd_line_build_file)) == 0

    def _get_original_apk_path(self):
        src_apk_name = 'AndroidMail-%s.apk' % self.mode
        for root, dirs, files in os.walk('build'):
            if src_apk_name in files:
                return os.path.join(root, src_apk_name)