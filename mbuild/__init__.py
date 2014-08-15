# coding: utf-8

import os
import sys
import optparse

from mbuild import option
from mbuild.command import commands
from mbuild.command import get_summaries
from mbuild.command import MbuildError
from mbuild.command import CommandError

from mbuild.util import get_prog
from mbuild.util import get_terminal_size

from mbuild.parser import PrettyHelpFormatter


ANTFILE = b"""
QlpoOTFBWSZTWfqNnFsACgb//////////////////////////////////v///////f/vYBAfBeNm
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
utcFX/F3JFOFCQ+o2cWw

"""

__version__ = '2.1'

__all__ = ['main']


def create_main_parser():
    parser_kw = {
        'usage' : '\n%prog <command> [options]',
        'add_help_option' : False,
        'formatter': PrettyHelpFormatter(),
        'prog' : get_prog()
    }

    parser = optparse.OptionParser(**parser_kw)
    parser.disable_interspersed_args()

    mbuild_pkg_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    parser.version = 'mbuild %s from %s (python %s)' % (
        __version__, mbuild_pkg_dir, sys.version[:3])

    gen_opts = option.make_option_group(option.general_group, parser)
    parser.add_option_group(gen_opts)

    parser.main = True

    command_summaries = get_summaries()
    description = [''] + ['%-27s %s' % (name, summary) for name, summary in command_summaries]
    parser.description = '\n'.join(description)

    return parser

def parseopts(args):
    parser = create_main_parser()
    general_options, args_else = parser.parse_args(args)

    # --version
    if general_options.version:
        sys.stdout.write(parser.version)
        sys.stdout.write(os.linesep)
        sys.exit()

    if not args_else or (args_else[0] == 'help' and len(args_else) == 1):
        parser.print_help()
        sys.exit()

    # subcommand name
    cmd_name = args_else[0].lower()

    cmd_args = args[:]
    cmd_args.remove(args_else[0].lower())

    if cmd_name not in commands:
        msg = ['unkown command "%s"' % cmd_name]
        raise CommandError(' - '.join(msg))

    return cmd_name, cmd_args

def main(initial_args=None):
    if initial_args is None:
        initial_args = sys.argv[1:]

    try:
        cmd_name, cmd_args = parseopts(initial_args)
    except MbuildError:
        e = sys.exc_info()[1]
        sys.stderr.write('Error %s' % e)
        sys.stderr.write(os.linesep)
        sys.exit(1)

    command = commands[cmd_name]()
    return command.main(cmd_args)
