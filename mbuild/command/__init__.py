# coding: utf-8

import os
import sys
import copy
import optparse

from mbuild import option
from mbuild.util import get_git_commit_sha1
from mbuild.util import get_prog
from mbuild.util import scp_send_apk, scp_send_file

from mbuild.parser import PrettyHelpFormatter
from mbuild.androidmanifest import AndroidManifest

from mbuild.build import AntBuild
from mbuild.build import GradleBuild

SUCCESS = 0
ERROR = 1
UNKNOWN_ERROR = 2

class MbuildError(Exception):
    """
    Base mbuild exception
    """


class CommandError(MbuildError):
    """
    Raised when there is an error in command-line arguments
    """


class Command(object):
    name = None
    usage = None
    hidden = False

    def __init__(self):
        parser_kw = {
            'usage': self.usage,
            'prog': '%s %s' % (get_prog(), self.name),
            'formatter': PrettyHelpFormatter(),
            'add_help_option': False,
            'description': self.__doc__
        }
        self.parser = optparse.OptionParser(**parser_kw)

        optgroup_name = '%s Options' % self.name.capitalize()
        self.cmd_opts = optparse.OptionGroup(self.parser, optgroup_name)

        gen_opts = option.make_option_group(option.general_group, self.parser)
        self.parser.add_option_group(gen_opts)

    def parse_args(self, args):
        return self.parser.parse_args(args)

    def main(self, args):
        options, args = self.parse_args(args)
        self._unicode_convert(options)
        self._filter(options)
        self._experience_filter(options)

        exit = SUCCESS
        try:
            status = self.run(options, args)

            # transfer apk to wlan
            self._scp_send_apk(options)
            self._scp_experience_apk(options)

            if isinstance(status, int):
                exit = status
        except CommandError:
            e = sys.exc_info()[1]
            exit = ERROR
        return exit

    def _unicode_convert(self, options):
        for key, value in options.__dict__.items():
            if type(value) is str and not isinstance(value, unicode):
                try:
                    setattr(options, key, unicode(value, 'gb2312'))
                except UnicodeDecodeError as e:
                    print '%-20s = %-10s, %s' % (key, value, type(value))

    def _filter(self, options):
        from mbuild import androidmanifest as __amft
        if (options.version_code == AndroidManifest.DEFAULT):
            options.version_code = __amft.VERSION_CODE
        if (options.version_name == AndroidManifest.DEFAULT):
            options.version_name = __amft.VERSOIN_NAME
        return options

    def _experience_filter(self, options):
        try:
            if options.__dict__.get('experience', False):
                def version_code(year, month, day, code=500528):
                    import datetime
                    base = datetime.datetime(year, month, day)
                    now  = datetime.datetime.now()
                    vc = (now - base).days + code
                    return str(vc)

                from time import strftime, localtime

                options.channel = 'exp'
                options.version_name = '%s_%s_%s' % (
                'WpsMail_Exp', strftime('%Y%m%d', localtime()), os.getenv('BUILD_NUMBER', '8888'))
                options.version_code = version_code(2015, 3, 10)
        except:
            pass

    def _scp_send_apk(self, options):
        is_transfer = os.getenv('isTransfer2Wlan', 'false')
        if is_transfer.lower() == 'true':
            publish_dir_root     = os.getenv('publishRootDir', '/data/hudson/misc/release')
            publish_build_number = os.getenv('BUILD_NUMBER', 'dev')
            publish_dir_prefix   = os.getenv('publishDirPrefix', os.path.basename(options.branch_name))
            publish_full_path    = '%s/%s-%s_%s' % (publish_dir_root, publish_dir_prefix, options.version_name, publish_build_number)

            # Linux上，最后一个包上传后格式被损坏了（文件内容没有完整）
            # pkey_filename = os.getenv('WLAN_PRIVATE_KEY')
            # scp_send_apk(options.mode, publish_full_path, '42.62.42.75', 'hudson', pkey_filename=pkey_filename)

            pkey_filename = os.getenv('WLAN_PRIVATE_KEY')
            host = 'hudson@42.62.42.75'

            ssh_cmd = 'ssh -o StrictHostKeyChecking=no -i %s %s "%s"' % (pkey_filename, host, 'rm -fr %s; mkdir -p %s' % (publish_full_path, publish_full_path))
            r = os.system(ssh_cmd)
            print ssh_cmd, r == 0

            for root, dirs, files in os.walk(options.mode):
                for file in files:
                    if file.endswith('.apk'):
                        scp_cmd = 'scp -o StrictHostKeyChecking=no -i %s %s %s:%s' % (pkey_filename, os.path.join(root, file), host, publish_full_path)
                        r = os.system(scp_cmd)
                        print scp_cmd, r == 0

    def _scp_experience_apk(selfself, options):
        if options.__dict__.get('experience', False):
            # Linux上，最后一个包上传后格式被损坏了（文件内容没有完整）
            # pkey_filename = os.getenv('EXPER_PRIVATE_KEY')
            # remotedir = '/home/wpsmail/webserver/download-server/webapps/download/experience'
            # scp_send_file(options.apk_path, remotedir, '42.62.41.207', 'wpsmail', pkey_filename=pkey_filename)

            remotedir = '/home/wpsmail/webserver/download-server/webapps/download/exp'
            apk_path = options.apk_path
            apk_name = os.path.basename(apk_path)
            pkey_filename = os.getenv('EXPER_PRIVATE_KEY')
            host = 'wpsmail@42.62.41.207'

            ssh_cmd = 'ssh -o StrictHostKeyChecking=no -i %s %s "%s"' % (pkey_filename, host, 'rm -fr %s' % os.path.join(remotedir, apk_name))
            r = os.system(ssh_cmd)
            print ssh_cmd, r == 0

            scp_cmd = 'scp -o StrictHostKeyChecking=no -i %s %s %s:%s' % (pkey_filename, apk_path, host, remotedir)
            r = os.system(scp_cmd)
            print scp_cmd, r == 0

            import httplib, urllib
            from time import strftime, localtime
            from mbuild.androidmanifest import MIN_SDK_VERSION, TARGET_SDK_VERSION

            conn = httplib.HTTPConnection('www.kmail.com')

            url    = '/wpsmail-api/upgrade/exp/replace?'
            des_packageName = (options.package_name
                                if options.package_name_for_exp is None else options.package_name_for_exp);
            print "des_packageName=%s" % des_packageName
            params = {
                'packageName': (options.package_name
                                if options.package_name_for_exp is None else options.package_name_for_exp),
                'size': '%.3f' % (os.path.getsize(options.apk_path) / (1024.0 * 1024.0)),
                'apkName': os.path.basename(options.apk_path),
                'versionCode': options.version_code,
                'versionName': options.version_name,
                'minSdkVersion': MIN_SDK_VERSION,
                'maxSdkVersion': TARGET_SDK_VERSION,
                'releaseNote': '%s-%s' % (u'Wpsmail偷跑版', strftime('%Y%m%d', localtime()))
            }
            url += urllib.urlencode(params)
            print "url=%s" % url

            try:
                conn.request('GET', url)
                response = conn.getresponse()
                print response.status, response.reason, response.read()
            except Exception, e:
                print e
            finally:
                conn.close()


class BatchCommand(Command):

    def __init__(self, *args, **kwargs):
        super(BatchCommand, self).__init__()

        build_opts = option.make_option_group(option.batch_build_group, self.parser)
        self.parser.option_groups.insert(0, build_opts)

    def run(self, options, args):
        options.commit_id = get_git_commit_sha1()
        #options.mode = 'debug' if options.debug else 'release'
        options.mode = options.debug

        batch_channel = options.batch_channel
        del options.batch_channel

        channels = batch_channel.split(',')
        c_prefix, c_len, c_range = channels[0], channels[1], channels[2]
        start, end = int(c_range.split('-')[0]), int(c_range.split('-')[1])
        for index in xrange(start, end + 1):
            tmp_options = copy.deepcopy(options)
            tmp_options.channel = (c_prefix + '%0' + c_len + 'd') % index
            self._run_single(tmp_options, args)


    def _run_single(self, options, args):
        pass


class AntCommand(Command):
    name = 'ant'
    usage = """
        %prog [optoions]
    """
    summary = 'Ant Build Android Project'

    def __init__(self, *args, **kwargs):
        super(AntCommand, self).__init__()

        build_opts = option.make_option_group(option.build_group, self.parser)
        self.parser.option_groups.insert(0, build_opts)

    def run(self, options, args):
        options.commit_id = get_git_commit_sha1()
        options.mode = 'debug' if options.debug else 'release'

        ant_build = AntBuild(options, options.verbose)
        with ant_build.prepare(AndroidManifest()):
            if ant_build.build():
                ant_build.publish()


class AntBatchCommand(BatchCommand):
    name = 'ant-batch'
    usage = """
        %prog [optoions]
    """
    summary = 'Ant Batch Build Android Project'

    def __init__(self, *args, **kwargs):
        super(AntBatchCommand, self).__init__()

    def _run_single(self, options, args):
        ant_build = AntBuild(options, options.verbose)
        with ant_build.prepare(AndroidManifest()):
            if ant_build.build():
                ant_build.publish()


class GradleCommand(Command):
    name = 'gradle'
    usage = """
        %prog [options]
    """
    summary = 'Gradle Build Android Project'

    def __init__(self):
        super(GradleCommand, self).__init__()

        build_opts = option.make_option_group(option.build_group, self.parser)
        self.parser.option_groups.insert(0, build_opts)

    def run(self, options, args):
        options.commit_id = get_git_commit_sha1()
        print 'options.debug='+options.debug
        options.mode = options.debug

        gradle_build = GradleBuild(options, options.verbose)
        with gradle_build.prepare(AndroidManifest()):
            if gradle_build.build():
                gradle_build.publish()


class GradleBatchCommand(BatchCommand):
    name = 'gradle-batch'
    usage = """
        %prog [options]
    """
    summary = 'Gradle Batch Build Android Project'

    def __init__(self):
        super(GradleBatchCommand, self).__init__()

    def _run_single(self, options, args):
        gradle_build = GradleBuild(options, options.verbose)
        with gradle_build.prepare(AndroidManifest()):
            if gradle_build.build():
                gradle_build.publish()


commands = {
    AntCommand.name: AntCommand,
    GradleCommand.name: GradleCommand,
    AntBatchCommand.name: AntBatchCommand,
    GradleBatchCommand.name: GradleBatchCommand
}

commands_order = [AntCommand, GradleCommand, AntBatchCommand, GradleBatchCommand]


def get_summaries(ignore_hidden=True, ordered=True):
    if ordered:
        cmditems = _sort_commands(commands, commands_order)
    else:
        cmditems = commands.items()

    for name, command_class in cmditems:
        if ignore_hidden and command_class.hidden:
            continue
        yield (name, command_class.summary)


def _sort_commands(cmddict, order):
    def keyfn(key):
        try:
            return order.index(key[1])
        except ValueError:
            return 0xff

    return sorted(cmddict.items(), key=keyfn)