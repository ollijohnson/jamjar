#------------------------------------------------------------------------------
# __init__.py - Parsers package root
#
# December 2015, Antony Wallace
#------------------------------------------------------------------------------

"""Parsers for Jam debug output."""

__all__ = (
    "parse",
)


from ._dd import DDParser
from ._dm import DMParser
from ._dc import DCParser


def parse(db, logfile):
    """
    Parse as much information as possible from the given log file into a DB.

    :param db:
        Target database to populate.
    :param logfile:
        Source jam log file containing debug output.

    """
    parser_clses = [
        DDParser,
        DMParser,
        DCParser,
    ]
    for parser_cls in parser_clses:
        parser_cls(db).parse_logfile(logfile)

