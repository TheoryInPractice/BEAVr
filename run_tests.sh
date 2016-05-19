#!/bin/sh
#
# This file is part of BEAVr, https://github.com/theoryinpractice/beavr/, and is
# Copyright (C) North Carolina State University, 2016. It is licensed under
# the three-clause BSD license; see LICENSE.
#

# run_tests.py - Run all unit tests for the visualization tool
python2.7 -m unittest discover -p '*.py' unittests
