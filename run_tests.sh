#!/bin/sh
# run_tests.py - Run all unit tests for the visualization tool
python2.7 -m unittest discover -p '*.py' unittests
