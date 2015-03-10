# coding: utf-8

import optparse

from mbuild import androidmanifest as __amft
from mbuild.util import url

def make_option_group(group, parser):
    option_group = optparse.OptionGroup(parser, group['name'])
    for option in group['options']:
        option_group.add_option(option)
    return option_group


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

experience = optparse.Option(
    '-e', '--experience',
    dest='experience',
    action='store_true',
    default=False,
    help='Build experience version apk.'
)

debug = optparse.Option(
    '--mode',
    dest='debug',
    type='str',
    default='release',
    help='android apk is debug, release, or unsigned (release is default value).'
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

apk_name_format = optparse.Option(
    '--apk-name-format',
    dest='apk_name_format',
    type='str',
    default='%prefix_%channel_%versionName_%commitId',
    metavar='apk name format',
    help="""specify apk prefix name (default is %default)
            --apk-name-format option controls the apk name.

            The only valid option is:

                %prefix         apk-prefix
                %channel        app channel
                %versionName    app version name
                %versionCode    app version code
                %commitId       git commit sha1
                %dbVersoinCode  app dbversionCode
                %packageName    app package name
    """
)

batch_channel = optparse.Option(
    '-C', '--batch-channel',
    dest='batch_channel',
    default='c,3,1-70',
    help='use specified channel (default is %default).'
)

hash_types = optparse.Option(
    '--hash-types',
    dest='hash_types',
    type='str',
    default='md5,sha1',
    metavar='hash algorithms',
    help='apk hash algorithms list (default "%default")'
)

test_flag = optparse.Option(
    '-t', '--test',
    dest='test_flag',
    action='store_true',
    default=False,
    help='publish apk and build info (False is default value).'
)

test_apk_publish_dir = optparse.Option(
    '--test-apk-publish-dir',
    dest='test_apk_publish_dir',
    type='str',
    default='/tmp',
    metavar='automate apk and other info directory',
    help='automate apk and other info directory (default "%default")'
)

test_info_publish_dir = optparse.Option(
    '--test-info-publish-dir',
    dest='test_info_publish_dir',
    type='str',
    default='/tmp',
    metavar='automate build info directory',
    help='automate build info directory (default "%default")'
)
flavor_name = optparse.Option(
    '--flavor-name',
    dest='flavor_name',
    type='str',
    default='',
    metavar='specify which flavor to build',
    help='specify which flavor to build (such as : kingsoft/oppo).'
)

package_name_for_exp = optparse.Option(
    '--package-name-for-exp',
    dest='package_name_for_exp',
    type='str',
    default=None,
    metavar='specify which package to upgrade',
    help='Take effect only when the parameters with -e'
         '(value default as : content in AndroidManifest.xml).'
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
        experience,
        channel,
        debug,
        package_name,
        branch_name,
        enable_branch_name,
        apk_display_name,
        version_name,
        version_code,
        apk_prefix,
        hash_types,
        apk_name_format,
        test_flag,
        test_apk_publish_dir,
        test_info_publish_dir,
        flavor_name,
        package_name_for_exp
        ]
    }

batch_build_group = {
    'name': 'Batch Build Options',
    'options': [
        debug,
        batch_channel,
        package_name,
        branch_name,
        enable_branch_name,
        apk_display_name,
        version_name,
        version_code,
        apk_prefix,
        hash_types,
        apk_name_format,
        flavor_name,
        package_name_for_exp
        ]
}
