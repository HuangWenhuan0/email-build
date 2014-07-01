# -*- coding: utf-8 -*-

"""Usage: python build.py [options]

Parameters:
    -c xxx,    --channel=xxx             use specified channel
    -C xxx,    --config=xxx              debug or release(default)
    -p xxx,    --package-name=xxx        use specified package name
    -b,        --enable-branch-name      enable branch name as application name
    -d xxx,    --display-name=xxx        specify display name
    -v xxx,    --version-name=xxx        specify app version name (android:versionName="")
               --apk-prefix=xxx          specify apk prefix name (default is WpsMail)
               --branch-name=xxx         specify branch name (not null)
    -h,        --help
    -i,        --verbose-info
"""

import os, sys, subprocess
import platform
import getopt
import shutil
import time

from StringIO import StringIO
from subprocess import check_output

__PYTHON_VER__ = '2.7.6'

SHOT_OPTS = 'bhc:C:p:d:v:i'
LONG_OPTS = ['enable-branch-name', 'help', 'channel=', 'config=', 'package-name=', 
             'display-name=', 'version-name=','verbose-info', 'apk-prefix=',
             'branch-type=', 'branch-name=']

SDK_PATHS = {
        'Windows_miui'  : 'sdk.dir=E:/android/sdk/android-miui-sdk_r22.6.2-windows',
        'Windows_wps'   : 'sdk.dir=E:/android/sdk/android-sdk_r22.6.2-windows',
        'Linux_miui'    : 'sdk.dir=/opt/android-miui-sdk_r16-linux',
        'Linux_wps'     : 'sdk.dir=/opt/android-sdk_r22.6.2-linux'
    }

CHANNEL = 'channel'
CONFIG = 'config'
PACKAGE_NAME = 'package-name'
DISPLAY_NAME = 'display-name'
ENABLE_BRANCH_NAME ='enable-branch-name'
VERSION_NAME ='version-name'
APK_PREFIX ='apk-prefix'
BRANCH_NAME = 'branch-name'
IS_MIUI_BRANCH = 'is-miui-branch'

DEF_CHANNEL = 'dev'
DEF_CONFIG  = 'debug'
DEF_ENABLE_BRANCH_NAME = False
DEF_APK_PREFIX = 'WpsMail'
DEF_IS_MIUI_BRANCH = False

OPTIONS = {
       CHANNEL            : DEF_CHANNEL, 
       CONFIG             : DEF_CONFIG,
       PACKAGE_NAME       : None,
       DISPLAY_NAME       : None,
       ENABLE_BRANCH_NAME : DEF_ENABLE_BRANCH_NAME,
       VERSION_NAME       : None,
       APK_PREFIX         : DEF_APK_PREFIX,
       BRANCH_NAME        : None,
       IS_MIUI_BRANCH     : DEF_IS_MIUI_BRANCH
    }

FORMATTER = '%-20s = %s'


class Parameters(object):
    def __init__(self):
        self.option = dict(OPTIONS)
    
    def __getitem__(self, key):
        return self.option[key]
    
    def __setitem__(self, key, value):
        self.option[key] = value
        
    def items(self):
        return self.option.items()
        
    @staticmethod
    def _grep(pattern, search_key, file):
        cmd = ['grep', pattern, file]
        out = subprocess.check_output(cmd).split('"')
        out = [v.strip() for v in out]
        
        idx = out.index(search_key)
        return out[idx + 1]
        
    @staticmethod
    def get_git_commit_sha1():
        try:
            cmd = ['git', 'log', '-1']
            commit = subprocess.check_output(cmd)
            output = StringIO(commit)
            return output.readline()[len('commit '):-1]
        finally:
            output.close()

    @staticmethod
    def get_def_pn():
        key = 'package='
        if sys.platform.startswith('win32'):
            return Parameters._grep('\'%s".*"\'' % key, key, 'AndroidManifest.xml')
        elif sys.platform.startswith('linux'):
            return Parameters._grep('%s".*"' % key, key, 'AndroidManifest.xml')
    
    @staticmethod
    def get_def_version_name():
        key = 'android:versionName='
        if sys.platform.startswith('win32'):
            return Parameters._grep('\'%s".*"\'' % key, key, 'AndroidManifest.xml')
        elif sys.platform.startswith('linux'):
            return Parameters._grep('%s".*"' % key, key, 'AndroidManifest.xml')
        
    @staticmethod
    def log_build_config(params, fsock=sys.stdout):
        options = [FORMATTER % (k, v) for k, v in params.items()]
        try:
            for option in options:
                fsock.write("%s\n" % option)
            fsock.write(FORMATTER % ('commit-sha1', '%s\n' % GIT_COMMIT_SHA1))
        finally:
            fsock.close()

    @staticmethod
    def load_def_config(params):
        for key, value in params.items():
            if value == None:
                if key == CHANNEL:
                    params[CHANNEL] = DEF_CHANNEL
                elif key == CONFIG:
                    params[CONFIG] = DEF_CONFIG
                elif key == PACKAGE_NAME:
                    params[PACKAGE_NAME] = DEF_PACKAGE_NAME
                elif key == DISPLAY_NAME:
                    pass
                elif key == ENABLE_BRANCH_NAME:
                    params[ENABLE_BRANCH_NAME] = DEF_ENABLE_BRANCH_NAME
                elif key == VERSION_NAME:
                    params[VERSION_NAME] = DEF_VERSION_NAME
                elif key == APK_PREFIX:
                    params[APK_PREFIX] = DEF_APK_PREFIX
                elif key == BRANCH_NAME:
                    print('build.py: "branch-name" option must be specified!')
                    print("build.py: 'try python build.py --help' for more information")
                    return False
        return True
    

def usage():
    print __doc__
    
def __log(level, out):
    print '%s - [%s] : %s' % (level, time.ctime()[4:-5], out)

def rename(rootpath, **kwargs):
    for root, dirs, files in os.walk(rootpath):
        print root, dirs, files

        for sf, df in kwargs.items():
            if sf in files:
                src = os.path.join(root, sf)
                dst = os.path.join(root, df)
                shutil.move(src, dst)

def prepare(params):
    # config sdk directory
    filename = 'sdk.properties'
    fsock = open(filename, 'w+')
    params[IS_MIUI_BRANCH] = 'mi' in params[BRANCH_NAME] or 'miui' in params[BRANCH_NAME]
    is_miui_branch = params[IS_MIUI_BRANCH]
    
    try:
        if is_miui_branch:
            if platform.system() == 'Windows':
                fsock.write(SDK_PATHS['Windows_miui'])            
            elif platform.system() == 'Linux':
                # path = SDK_PATHS['Linux_miui'] % os.environ['HOME']
                # fsock.write(path)
                fsock.write(SDK_PATHS['Linux_miui'])
            else:
                __log("DEBUG", "doesn't support this %s platform" % platform.system())
                sys.exit(2)
        else:
            if platform.system() == 'Windows':
                fsock.write(SDK_PATHS['Windows_wps'])
            elif platform.system() == 'Linux':
                # path = SDK_PATHS['Linux_wps'] % os.environ['HOME']
                # fsock.write(path)
                fsock.write(SDK_PATHS['Linux_wps'])
            else:
                __log("DEBUG", "doesn't support this %s platform" % platform.system())
                sys.exit(2)
    finally:
        fsock.close()
        
    # config miui res apk
    if is_miui_branch:
        dsts = ['./MIUI_SDK', '../appcompat/MIUI_SDK', '../gridlayout/MIUI_SDK']
        apk_name = 'framework-miui-res.apk'
        for dst in dsts:
            if not os.path.exists(dst):
                os.makedirs(dst)
            if not os.path.exists(os.path.join(dst, apk_name)):
                # shutil.copy2('../miui_libs/%s' % apk_name, dst)
                shutil.copy2('./%s' % apk_name, dst)

    files = {'ksMailTemplate_mixed.html' : 'ksMailTemplate.html',
             'ksMailView_mixed.js'       : 'ksMailView.js'}
    rename('assets', **files);
    
def backup():
    if not os.path.exists(GIT_COMMIT_SHA1):
        os.mkdir(GIT_COMMIT_SHA1)
    
    tcmd = 'tar zcf %s/backup.tar.gz assets res src *.xml *.properties'
    os.system(tcmd % GIT_COMMIT_SHA1)

def cleanup():
    try:
        os.remove('ant-build.log')
        os.remove('build.log')
    except:
        pass

def restore(params):
    os.system('rm -fr assets res src *.xml *.properties')
    os.system('tar zxf %s/backup.tar.gz' % GIT_COMMIT_SHA1)
    
    shutil.rmtree(GIT_COMMIT_SHA1)
    
    # delete miui res apk
    if params[IS_MIUI_BRANCH]:
        dsts = ['./MIUI_SDK', '../appcompat/MIUI_SDK', '../gridlayout/MIUI_SDK']
        for dst in dsts:
            if os.path.exists(dst):
                shutil.rmtree(dst)
    
def distribute(params):
    config = params[CONFIG]

    # _time = time.strftime('%Y%m%d-%H%M%S', time.localtime())
    path = '%s/%s/%s' % (config, params[CHANNEL], GIT_COMMIT_SHA1)
    if not os.path.exists(path):
        os.makedirs(path)
    
    src_file = 'bin/AndroidMail-%s.apk' % config
    dst_file = '%s/%s_%s_%s.apk' % (path, params[APK_PREFIX], params[CHANNEL], GIT_COMMIT_SHA1[:7])
    shutil.copy2(src_file, dst_file)
    shutil.copy2('ant-build.log', path)
    shutil.copy2('build.log', path)
    
    os.system('rm -fr bin/classes bin/*_ bin/*.d bin/*.apk')
    os.system('tar zcf %s/src.tar.gz src gen bin/*' % path)
    
    
def change_displayname(params):
    pass
    
def change_packagename(params):
    package_name = params[PACKAGE_NAME]
    if params[ENABLE_BRANCH_NAME]:
        package_name += "_" + BRANCH_NAME
    
    if package_name != DEF_PACKAGE_NAME:
        scmd = "sed -i 's#package=\"%s\"#package=\"%s\"#' AndroidManifest.xml"
        os.system(scmd % (DEF_PACKAGE_NAME, package_name))
        
        # res/xml directory
        scmd_email_np = "sed -i 's#xmlns:email=\"http://schemas.android.com/apk/res/%s\"#xmlns:email=\"http://schemas.android.com/apk/res/%s\"#' res/xml/%s"
        files = ['email_server_list.xml', 'services.xml']
        for file in files:
            os.system(scmd_email_np % (DEF_PACKAGE_NAME, package_name, file))
        
        # res/drawable directory
        scmd_app_np = "sed -i 's#xmlns:app=\"http://schemas.android.com/apk/res/%s\"#xmlns:app=\"http://schemas.android.com/apk/res/%s\"#' res/drawable/%s"
        files = ['ic_folder_drafts.xml',    'ic_folder_inbox.xml',
                 'ic_folder_outbox.xml',    'ic_folder_sent.xml',
                 'ic_folder_star.xml',      'ic_folder_trash.xml',
                 'ic_folder_unkown.xml',    'ic_folder_unread.xml']
        for file in files:
            os.system(scmd_app_np % (DEF_PACKAGE_NAME, package_name, file))
        
def change_appdebugable(params):
    config  = params[CONFIG]
    scmd = "sed -i 's#android:debuggable=\"%s\"#android:debuggable=\"%s\"#' AndroidManifest.xml"
    
    if config == 'release':
        os.system(scmd % ("true", "false"))
    elif config == 'debug':
        os.system(scmd % ("false", "true"))
        
def change_version_name(params):
    ver_name = params[VERSION_NAME]
    if ver_name != DEF_VERSION_NAME:
        scmd = "sed -i 's#android:versionName=\".*\"#android:versionName=\"%s\"#' AndroidManifest.xml"
        os.system(scmd % ver_name)

def change_appchannel(params):
    channel = params[CHANNEL]
    scmd = "sed -i 'N;s#android:name=\"channel\"\s\+android:value=\"%s\"#android:name=\"channel\"\\r\\n\\t\\t\\tandroid:value=\"%s\"#' AndroidManifest.xml"
    default_channels = ['DEBUG', 'miui', 'wps']
    for d_channel in default_channels:
        os.system(scmd % (d_channel, channel))
		
def change_commit_sha1():
    scmd = "sed -i 'N;s#android:name=\"commit_id\"\s\+android:value=\"%s\"#android:name=\"commit_id\"\\r\\n\\t\\t\\tandroid:value=\"%s\"#' AndroidManifest.xml"
    default_channels = ['DEBUG']
    for d_channel in default_channels:
        os.system(scmd % (d_channel, GIT_COMMIT_SHA1))
        
def start_ant(params):
    ant_cmd = 'ant clean %s | tee -a ant-build.log'
    if os.system(ant_cmd % params[CONFIG]):
        print 'ant error'
    
def cmp_ver(actual, suggest, index):
    """
    1  - current version < suggest version
    -1 - current versoin > sugesst version
    0  - current version = suggest version
    """
    if actual[index] > suggest[index]:
        return -1
    elif actual[index] < suggest[index]:
        return 1
    else:
        index += 1
        if index == len(suggest) or index == len(actual):
            return 0
        return cmp_ver(actual, suggest, index)
    
    
def set_global_info():
    global GIT_COMMIT_SHA1
    global DEF_PACKAGE_NAME
    global DEF_VERSION_NAME
    
    GIT_COMMIT_SHA1 = Parameters.get_git_commit_sha1()
    DEF_PACKAGE_NAME = Parameters.get_def_pn()
    DEF_VERSION_NAME = Parameters.get_def_version_name()

def main():
    argv = sys.argv[1:]
    if len(argv) == 0:
#         print 'load default config and build project...'
#         argv = ['--channel=%s'      % DEF_CHANNEL,
#                 '--config=%s'       % DEF_CONFIG,
#                 '--package-name=%s' % DEF_PACKAGE_NAME,
#                 '--apk-prefix=%s'   % DEF_APK_PREFIX,
#                 '--version-name=%s' % DEF_VERSION_NAME,
#                 '--verbose-info']
        pass
    
    try:
        opts, args = getopt.getopt(argv, SHOT_OPTS, LONG_OPTS)  # @UnusedVariable
    except getopt.GetoptError as err:
        print str(err)
        usage()
        sys.exit(2)
        
    global verbose
    verbose = False
    
    if ('-i', '') in opts:
        verbose = True
        opts.remove(('-i', ''))
    if ('--verbose-info', '') in opts:
        verbose = True
        opts.remove(('--verbose-info', ''))
        
    set_global_info()
    params = Parameters()        
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            usage()
            sys.exit(2)
        elif opt in ('--apk-prefix'):
            params[APK_PREFIX] = arg
        elif opt in ('--branch-name'):
            params[BRANCH_NAME] = arg
        elif opt in ('-v', '--version-name'):
            params[VERSION_NAME] = arg
        elif opt in ('-d', '--display-name'):
            params[DISPLAY_NAME] = arg
        elif opt in ('-b', '--enable-branch-name'):
            params[ENABLE_BRANCH_NAME] = True
        elif opt in ('-p', '--package-name'):
            params[PACKAGE_NAME] = arg
        elif opt in ('-C', '--config'):
            params[CONFIG] = arg
        elif opt in ('-c', "--channel"):
            params[CHANNEL] = arg
            
    if not Parameters.load_def_config(params):
        sys.exit(2)
    
    cleanup()
    backup()
    
    change_version_name(params)
    change_displayname(params)
    change_packagename(params)
    change_appdebugable(params)
    change_appchannel(params)
	change_commit_sha1()
    
    prepare(params)
    
    try:
        Parameters.log_build_config(params, open('build.log', 'w+'))
        start_ant(params)
        Parameters.log_build_config(params)
        distribute(params)
    finally:
        cleanup()
        restore(params)
            
if __name__ == '__main__':
    main()
