# coding: utf-8

import os
import sys
import copy
import optparse

from mbuild import option
from mbuild.util import get_git_commit_sha1
from mbuild.util import get_prog
from mbuild.util import scp_send_apk

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
        self.__convert(options)

        exit = SUCCESS
        try:
            status = self.run(options, args)

            # transfer apk to wlan
            self._scp_send_apk(options)

            if isinstance(status, int):
                exit = status
        except CommandError:
            e = sys.exc_info()[1]
            exit = ERROR
        return exit

    def __convert(self, options):
        for key, value in options.__dict__.items():
            if type(value) is str and not isinstance(value, unicode):
                try:
                    setattr(options, key, unicode(value, 'gb2312'))
                except UnicodeDecodeError as e:
                    print '%-20s = %-10s, %s' % (key, value, type(value))

    def _scp_send_apk(self, options):
        is_transfer = os.getenv('isTransfer2Wlan', 'false')
        if is_transfer.lower() == 'true':
            publish_dir_root     = os.getenv('publishRootDir', '/data/hudson/misc/release')
            publish_build_number = os.getenv('BUILD_NUMBER', 'dev')
            publish_dir_prefix   = os.getenv('publishDirPrefix', os.path.basename(options.branch_name))
            publish_full_path    = '%s/%s-%s_%s' % (publish_dir_root, publish_dir_prefix, options.version_name, publish_build_number)

            pkey_filename = os.getenv('WLAN_PRIVATE_KEY')
            scp_send_apk(options.mode, publish_full_path, '42.62.42.75', 'hudson', pkey_filename=pkey_filename)

class BatchCommand(Command):

    def __init__(self, *args, **kwargs):
        super(BatchCommand, self).__init__()

        build_opts = option.make_option_group(option.batch_build_group, self.parser)
        self.parser.option_groups.insert(0, build_opts)

    def run(self, options, args):
        options.commit_id = get_git_commit_sha1()
        options.mode = 'debug' if options.debug else 'release'

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
        options.mode = 'debug' if options.debug else 'release'

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

        build_opts = option.make_option_group(option.batch_build_group, self.parser)
        self.parser.option_groups.insert(0, build_opts)

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