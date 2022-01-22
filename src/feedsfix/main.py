#!/usr/bin/env python3
#
# MIT License
#
# Copyright (c) 2020 Arkadiusz Netczuk <dev.arnet@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#

import sys

import argparse
import logging


logging.basicConfig(stream = sys.stdout, 
                    level = logging.DEBUG)

_LOGGER = logging.getLogger(__name__)


def main( args=None ):
#     if args is None:
#         parser = create_parser()
#         args = parser.parse_args()

    _LOGGER.debug( "Starting the application" )
#     _LOGGER.debug( "Logger log file: %s", logger.log_file )

    exitCode = 1

#     try:
#         exitCode = run_app( args )
#
#     except BaseException:
#         _LOGGER.exception("Exception occurred")
#         raise

    return exitCode


if __name__ == '__main__':
    ret_code = main()
    sys.exit( ret_code )
