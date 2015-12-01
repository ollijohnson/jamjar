#------------------------------------------------------------------------------
# test.sh - Run all tests
#
# November 2015, Phil Connell
#------------------------------------------------------------------------------

python3 -m pylint -E $(find jamjar -name "*.py")
python3 -m unittest jamjar/test/test_*.py

