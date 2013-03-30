#!/bin/bash -x
# vim: ts=8 sw=2 smarttab
#
# $0.sh - run tests on the monitor's 'config-key' api

bin_test='test_mon_config_key.py'

args=""

[ ! -z $DURATION ] && args="$args -d $DURATION"
[ ! -z $SEED ] && args="$args -s $SEED"
[ ! -z $DEBUG ] && args="$args -v"
[ ! -z $TEST_LOC ] && bin_test="$TEST_LOC/$bin_test"

$bin_test $args
