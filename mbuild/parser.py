# coding: utf-8

import optparse
import textwrap

from mbuild.util import get_terminal_size

class PrettyHelpFormatter(optparse.IndentedHelpFormatter):
    """A prettier/less verbose help formatter for optparse."""

    def __init__(self, *args, **kwargs):
        # help position must be aligned with __init__.parseopts.description
        kwargs['max_help_position'] = 30
        kwargs['indent_increment'] = 1
        kwargs['width'] = get_terminal_size()[0] - 2
        optparse.IndentedHelpFormatter.__init__(self, *args, **kwargs)

    def format_option_strings(self, option):
        return self._format_option_strings(option, ' <%s>', ', ')

    def _format_option_strings(self, option, mvarfmt=' <%s>', optsep=', '):
        """
        Return a comma-separated list of option strings and metavars.

        :param option:  tuple of (short opt, long opt), e.g: ('-f', '--format')
        :param mvarfmt: metavar format string - evaluated as mvarfmt % metavar
        :param optsep:  separator
        """
        opts = []

        if option._short_opts:
            opts.append(option._short_opts[0])
        if option._long_opts:
            opts.append(option._long_opts[0])
        if len(opts) > 1:
            opts.insert(1, optsep)

        if option.takes_value():
            metavar = option.metavar or option.dest.lower()
            opts.append(mvarfmt % metavar.lower())

        return ''.join(opts)

    def format_heading(self, heading):
        if heading == 'Options':
            return ''
        return heading + ':\n'

    def format_usage(self, usage):
        """
        Ensure there is only one newline between usage and the first heading
        if there is no description.
        """
        msg = '\nUsage: %s\n' % self.indent_lines(textwrap.dedent(usage), "  ")
        return msg

    def format_description(self, description):
        # leave full control over description to us
        if description:
            if hasattr(self.parser, 'main'):
                label = 'Commands'
            else:
                label = 'Description'
            # some doc strings have initial newlines, some don't
            description = description.lstrip('\n')
            # some doc strings have final newlines and spaces, some don't
            description = description.rstrip()
            # dedent, then reindent
            description = self.indent_lines(textwrap.dedent(description), "  ")
            description = '%s:\n%s\n' % (label, description)
            return description
        else:
            return ''

    def format_epilog(self, epilog):
        # leave full control over epilog to us
        if epilog:
            return epilog
        else:
            return ''

    def indent_lines(self, text, indent):
        new_lines = [indent + line for line in text.split('\n')]
        return "\n".join(new_lines)
