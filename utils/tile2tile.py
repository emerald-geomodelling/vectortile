#!/usr/bin/env python
"""Convert Vectortile data between formats

Usage:
  tile2tile.py [options] [SOURCE [DEST]]
  tile2tile.py [options] SOURCE [-]
  tile2tile.py [options] [-] [-]
  tile2tile.py (-h | --help)
  tile2tile.py --version

Options:
  -f FORMAT --format=FORMAT    Output format: (tile | json) [default: tile]
  --srcformat=SRC_FORMAT    Source file format: (tile | json)
  -h --help     Show this screen.
  --version     Show version.
  -q --quiet    be quiet
  -v --verbose  yak yak yak
"""

from docopt import docopt
import sys, logging, json
from vectortile import Tile


def transform(infile_name, src_format, outfile_name, dest_format):

    with sys.stdin if infile_name is None or '-' == infile_name else open(infile_name, 'rb') as file_in:
        with sys.stdout if outfile_name is None or '-' == outfile_name else open(outfile_name, 'w') as file_out:
            if src_format is None:
                # guess source format
                if '.json' == infile_name[-5:]:
                    src_format = 'json'
                else:
                    src_format = 'tile'
            if src_format == 'json':
                src_tile = json.load(file_in)
                if 'data' in src_tile:
                    dest_tile = Tile.fromdata(src_tile['data'], src_tile.get('meta'), src_tile.get('cols'))
                else:
                    # assume the the entire thing is just the data part
                    dest_tile = Tile.fromdata(src_tile)
            else:
                dest_tile = Tile(file_in.read())

            if dest_format == 'json':
                json.dump(dest_tile.asdict(), file_out, indent=4)
            else:
                file_out.write(str(dest_tile))


def main():
    arguments = docopt(__doc__, version='Tile2Tile 0.1')

    if arguments['--verbose']:
        log_level = logging.DEBUG
    elif arguments.get('--quiet'):
        log_level = logging.ERROR
    else:
        log_level = logging.INFO
    logging.basicConfig(format='%(levelname)s: %(message)s', level=log_level)

    src_name = arguments['SOURCE']
    dest_name = arguments['DEST']
    source_format = arguments['--srcformat']

    if (src_name is None or src_name == '-') and source_format is None:
        logging.error('Cannot read from stdin unless source format is specified')
        return 0

    try:
        transform(arguments['SOURCE'], arguments['--srcformat'], arguments['DEST'], arguments['--format'])
    except IOError, e:
        logging.error(e)
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())

