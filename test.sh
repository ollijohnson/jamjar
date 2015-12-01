#!/bin/bash
#------------------------------------------------------------------------------
# test.sh - Run all tests
#
# November 2015, Phil Connell
#------------------------------------------------------------------------------

ROOT=$(dirname $(readlink -f $0))
export PYTHONPATH=ROOT

python3 -m pylint -E $(find jamjar -name "*.py")
python3 -m unittest $ROOT/jamjar/test/test_*.py

