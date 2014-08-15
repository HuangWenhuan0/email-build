# coding: utf-8

import os
import sys
import optparse

from mbuild import option
from mbuild.util import get_git_commit_sha1
from mbuild.util import get_prog
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


class AndBuildCommand(Command):
    name = 'ant'
    usage = """
        %prog [optoions]
    """
    summary = 'Ant Build Android Project'

    def __init__(self, *args, **kwargs):
        super(AndBuildCommand, self).__init__(*args, **kwargs)

        build_opts = option.make_option_group(option.build_group, self.parser)
        self.parser.option_groups.insert(0, build_opts)

    def run(self, options, args):
        options.commit_id = get_git_commit_sha1()
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
        gradle_build = GradleBuild(options, options.verbose)
        with gradle_build.prepare(AndroidManifest()):
            if gradle_build.build():
                gradle_build.publish()


commands = {
    AndBuildCommand.name: AndBuildCommand,
    GradleCommand.name: GradleCommand
}

commands_order = [AndBuildCommand, GradleCommand]


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