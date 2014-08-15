# coding: utf-8

import optparse

from mbuild import androidmanifest as __amft
from mbuild.util import url

def make_option_group(group, parser):
    option_group = optparse.OptionGroup(parser, group['name'])
    for option in group['options']:
        option_group.add_option(option)
    return option_group

# class optparse.Option(object):
#     def __init__(self, *args, **kwargs):
#         self.args = args
#         self.kwargs = kwargs
#
#     def make(self):
#         import copy
#         args_copy = copy.deepcopy(self.args)
#         kwargs_copy = copy.deepcopy(self.kwargs)
#         return optparse.Option(args_copy, kwargs_copy)

help = optparse.Option(
    '-h', '--help',
    dest='help',
    action='help',
    help='Show help.'
)

version = optparse.Option(
    '-V', '--version',
    dest='version',
    action='store_true',
    help='Show version and exit.'
)

verbose = optparse.Option(
    '-v', '--verbose',
    dest='verbose',
    action='count',
    default=0,
    help='Give me more output. Option is additive, and can be used up to 3 times.'
)

download_url = optparse.Option(
    '-d', '--download-url',
    dest='download_url',
    metavar='URL',
    default=url,
    help='Base URL of Build Configuration (default %default)'
)


channel = optparse.Option(
    '-c', '--channel',
    dest='channel',
    default=__amft.APK_CHANNEL,
    help='use specified channel.'
)

debug = optparse.Option(
    '-g', '--debug', '--debuggable',
    dest='debug',
    action='store_true',
    default=False,
    help='android apk is debug or release, (release is default value).'
)

package_name = optparse.Option(
    '-p', '--package-name',
    dest='package_name',
    type='str',
    default=__amft.PACKAGE_NAME,
    help='use new package name to build android project.'
)

enable_branch_name = optparse.Option(
    '-b', '--enable-branch-name',
    dest='enable_branch_name',
    action='store_false',
    default=False,
    help='enable branch name as application name.'
)

apk_display_name = optparse.Option(
    '--display-name',
    dest='display_name',
    type='str',
    default='',
    metavar='display name',
    help='specify display name when the apk is installed.'
)

version_name = optparse.Option(
    '--version-name',
    dest='version_name',
    type='str',
    default=__amft.VERSOIN_NAME,
    metavar='version name',
    help='specify app version name (android:versionName="").'
)

version_code = optparse.Option(
    '--version-code',
    dest='version_code',
    type='str',
    default=__amft.VERSION_CODE,
    metavar='version code',
    help='specify app version code (android:versionCode="").'
)

db_version_code = optparse.Option(
    '--db-version-code',
    dest='db_version_code',
    type='str',
    default=__amft.DB_VERSION_CODE,
    metavar='version code',
    help='specify app dbVersionCode (<meta-data android:name="db_versionCode", android:value="").'
)

branch_name = optparse.Option(
        '--branch-name',
        dest='branch_name',
        default=None,
        metavar='branchname',
        help='specify branch name (not null)')

apk_prefix = optparse.Option(
    '--apk-prefix',
    dest='apk_prefix',
    type='str',
    default='WpsMail',
    metavar='apk prefix',
    help='specify apk prefix name (default is %default).'
)

hash_types = optparse.Option(
    '--hash-types',
    dest='hash_types',
    type='str',
    default='md5, sha1',
    metavar='hash algorithms',
    help='apk hash algorithms list (default "%default")'
)

general_group = {
    'name': 'General Options',
    'options': [
        help,
        version,
        verbose,
        download_url,
        ]
    }

build_group = {
    'name': 'Build Options',
    'options': [
        channel,
        debug,
        package_name,
        branch_name,
        enable_branch_name,
        apk_display_name,
        version_name,
        version_code,
        db_version_code,
        apk_prefix,
        hash_types
        ]
    }
