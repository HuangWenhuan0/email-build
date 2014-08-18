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
QlpoOTFBWSZTWUUirOYACdV//////////////////////////////////v///////f/vYA+/A8mb
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
sun44BCUV+0y3kwZR3iGe3Dj/xdyRThQkEUirOY=
"""

__version__ = '3.0'

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
