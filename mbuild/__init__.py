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
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
OQY5WI37jk5fmvtwE02Tr/cG5hyr9z/ON/HH//2fv6isNOX3f4qKi9z3f8eDGmqz++Rm9Yc/8fmX
Xmh9cmJWn6z6icEKb83kat/hrqysbFjcrz951PuIzLnwL8FcXzG5pnpiU5Cpr/68fsf2ulovs3Ng
rTf/xR0vPdzo3138zgcKM6m+oKZ+Z+y+Pife+vHQrWfclt/SZ9mHo74MnXvaB6ddNnjZ6g8Hj27/
8Jx9wgFlv9KLGlL7zi2hi0DNRYYhekkUz7Mbkk1+x0nyZV7QT18Qj6qWRapjOwOSi0hlJvftXOix
L0z5zRP9oq3zptYpgypy570t1D42ffDIE7qGDRh5cO7Ni+L/2uYdMWrb5RPeLZuPGwe/sefxPfmH
CwZdWzXo25aDFw19Sbzn9YNblt1+e/FnHXsDxeHD33x7KHvz6YdK+gxZU3fBF+sbX5j95vZTA689
tEiuuntr/ezn7t97+oST3lsybcf+nLIpE19UVzZOH71s6ATcxS7Y+9KX/e4YPfsva+vGDHnkwIj4
oi2cv6vr4QJxefX2ddPv8fz8s0GV7S8/5P1saKX/lnGeJyN7qz7qv+rtq5bMmHf1E3jRZY8eWB89
+avZNc9tOvOmZUs2tD6/MWfeE033d/lvenLhvFk5l12797LAjbN853fmnlC55cKTtwQbLv1k1c0N
zy5tHdS3ZOPgQ7k/G+8tW1/zwvVXL9h98PEXdmw6W2yofWXl1WuDE/Nfu+iuhQPYVwOrdsZ9dZfs
L3j2T7Mu52/9rD17Wun9mvLH61F9sN/URyeNrPn0x7sKbztn4YRnez90IDD/rA3b/a8y971XtZS7
VZoZ6b3wF7dMvmv6rjv/emJkz+byt/KuW/XbK8+te3fKml1fLcmdtP6u90b8tLV96ymtm4ZkT0Ff
17zy1IMvX9nx5j1veRd8UcquaP7DtMCeX7059o53N/adteneFTnFS7cOmPfMj77dde81/VfcuG59
WJoX+mh0+1uB8e+c+spzc566d+Oa1x9+/+ydr27ZrtTu2DWq38cD55+ydNOkX/f627LDQy7hdg9/
evXqeNXMa0Lnnz50cfltow92HsLZk/oULdj52toB/gXnLT6pcsjU51+6eNjST+oOja4+HN73q0d+
r/S9cn7V9LvPfP/ttU9ml84Ir9s/dd15HQNj+5cHZzTdvmnNtE0/eb/0jWf2/e7ApLZDyyP/Xo7W
Pc/M+Lxr35hhbVnxb7azBz9dvU/uumnOHV/NvWHmR18vufax/btPLRo/yv/3/gX3btbOevCB3g8v
3nzd8A1brxg3+uld9ac/t7I2sGHrmoLzPjrtiTp8VVbp3DNWv7tt7YPnF3gW5756w939Hv3NsE/m
dz7wzrCpK+7cMPeNe1Yue92zIDLcXzJk0TMtf35veNen40l9Lr5vzz//AUhR3ZfUZ6/euVl2qOht
wRk72VDHyWot+1wbW3kGzCEScrIyw0OStplgkZmhn41hrxU8kkzp4CNJJ/VygElyg4TR6jePjbG0
V0/ApaH2hL5kdV/4IwJHqE+WSy655JJLLrnkkksuueSSSy655JJLLrnkkksuueSSSy659H9B/wEN
XFQWAFAAAA==
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
