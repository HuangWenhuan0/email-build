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
5bCkpInf0G0FVGgupRCRcZJ8ANz2pQ9Wi/M94UKQ/5heYXA95Hqji+sh0aLLp/dFndg+2QpYppdr
5EbauQFjst+LMP7TKSkdj7szUGmOk6vnq+9cv1rhnrAyJK1bk/5wljtzEy7dLwLzP833P5lfxn/x
3/+VTCPvM37/p6ykMvj+74ug1sYRIwvyxsCf9NIzz/A+OTJvZF5zfawmFG1pCB8YyMsbAcyjx5BH
ww8qXAD/HOHmmpZoQ317jG1u+Efztq1NjSF2+9GNoaKntz1zV1vJc2Wvv62yc5uLo83bjdtGHnnV
XyduOfHqoq6Rq9+Z8u/4t45/+/izxq9e8874qb3vfHO3uFfdow6jjjS+fmV8NpiZbTlipn/ZEr8j
I8jvOMnh3AyjTYZ0SvMwaRnLGesykRJ0153JyPgZB/0CinlB139F97xxNQVLXhMb710wfvIRA5PG
Tt530c+Xp//+WOjkKY+dPeuNyqW4bfzLO+/fWXSgeNwldeM+6do3e+Iz0i0v7du8+vrryz7o2xUp
Sxz4+JP9Ix46Yf/0kRPWNn37Xxvanlr0ytbjIi/euVypu3lL86Inbt91wqyj3lx57rY9+ZXz6p/W
rmtbMHX1xFl4gFu265l/j75h6qI/rGuqmHD33pPTyzfzJQMDdxVL1zRsXb/gFuZ7H4yr7X32ztAH
E2tLrqxmHkzuqnt3zE2vXbDyvCUXPoCXn3XP3g2pYz5cFH1i09evWL1yY/eT9+UveaD99oGSKx68
dMnC/LMu2XVW5GcLw6f3FxxRu/mMYzbHWs9876aftz6+qnvcqOn3jd9f8N2ZocoN0acuv3DZc/vu
f2rbplOl1sbnr7twXay+6MXZN146lnshctP2dLjpO3uKH//dwrOFqz7oHXFu+e26+tvLUXNs9Px7
5k6Ovv/VHaVXf/PSWY8Pv3NvZOkpG7eWvMDe9mbdKv4quSM5/NLvX9ly44Idv/rjkcmdD1W9WnjZ
TT85/1tNb8xbu+PDlQVzN9z45snf6O7dcmz3pgkj5qGPos8/fMez5/e9csuroWX/Kueu7fz1uZGd
P3xlxg1v3Ddq4aZbr80vW7Vl7JJHv/LJjlsvHnPtz9ZvSMhL4u9O7X01MvP1455/YvHDt9639qW7
3jp1+wubt6qN23ZMGf3Xo5ceu2rT3B8N+9PqAxO+wz930iNr1qTrOi6On37CxBVVV0/d178fj5g7
ctqy7S+uG1uy7LQVR9VOmP/kM3MmrXqvaf/UhgOJ3T+8+5fqqPOX1i24+etvvbbuwRHl5yXW75m/
/rS+o40918TOa79+09pzN33trfKXH939i71ze/Zfk/znNWj9k+x5/xjYXTGpJy/98VZu3/trdisD
Vyy+4cOLftrx7kcrL7l3z3PHTZs5peTPY4pvfUg/5Y7fDL9rxUOXnbRxyznVUx/Z0XzCE9c1RjZu
WVt82rvHP9CEL8grv+jENW88tu6O04uZFQUv/PTm0ff8eNJ7S/t/8/qk+df+auNFL99y3eqXmGXJ
k0qmT1j+aNfv3zxp4P2ZpD5X3Lbzb38BpGgYRepz2PCCPD9UDPfgjJ98qJMp6i37Ap9YVQ7MIRry
83LDg0uP2WCRW2C0T2CXFzxcoWzw4dJRwzLAxF0gEfTGjfEJlg87FHBpbTxiFOEeBX8kkIiPzAso
oIACCiiggAIKKKCAAgoooIACCiiggAIKKKCAAgoooID+L+g/hMMK9ABQAAA=
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
