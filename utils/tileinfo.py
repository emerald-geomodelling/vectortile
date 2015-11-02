#!/usr/bin/env python

"""Print out a report about whats in a vectortile

Usage:
  tileinfo.py [options] [SOURCE]

Options:
  --srcformat=SRC_FORMAT    Source file format: (tile | json)
  --indent=INT|None         JSON indentation level.  Defaults to 4.  Use 'None' to disable.
  -h --help     Show this screen.
  --version     Show version.
  -q --quiet    be quiet
"""


import json
import sys

from docopt import docopt

from vectortile import Tile


def info(data, cols):

    """
    Compute min/max for all registered columns.

    Parameters
    ----------
    data : list
        List of points from tile.
    cols : list
        List of columns from tile header.

    Returns
    -------
    dict
        {
            column: {
                min: value,
                max: value
            }
        }
    """

    stats = {c['name']: [] for c in cols}
    for point in data:
        for c, v in point.items():
            stats[c].append(v)
    return {n: {'min': min(v), 'max': max(v)} for n, v in stats.items()}


def main():

    """
    Get an info report for a tile.  Format is same as input tile but with
    min/max values for values under 'data'.
    """

    arguments = docopt(__doc__, version='tileinfo 0.1')

    src_name = arguments['SOURCE']
    src_format = arguments['--srcformat']
    indent = arguments['--indent']
    if isinstance(indent, str) and indent.lower() == 'none':
        indent = None
    elif isinstance(indent, str):
        indent = int(indent)
    else:
        indent = 4

    with sys.stdin if src_name in ('-', None) else open(src_name, 'rb') as f:

        # Guess input format if not given
        if src_format is None:
            if '.json' == f.name[-5:]:
                src_format = 'json'
            else:
                src_format = 'tile'

        if src_format == 'tile':
            header, data = Tile(f.read()).unpack()
        else:
            header = json.loads(f.read())
            data = header.pop('data')

        # Generate the info report
        report = info(data, header['cols'])

        # Merge report with other tile attributes
        out = {k: v for k, v in header.items() if k != 'data'}
        out['data'] = {}
        for field, vals in report.items():
            out['data'][field + '_min'] = vals['min']
            out['data'][field + '_max'] = vals['max']

        print(json.dumps(out, indent=indent, sort_keys=True))


if __name__ == '__main__':
    sys.exit(main())
