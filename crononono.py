#!/usr/bin/python

import argparse
import sys
import subprocess
import time
import signal
import re
import copy as _copy

def handler(signum, frame):
    raise Exception("timeout")

parser = argparse.ArgumentParser(description='Cron Output Filter',
        prog='crononono'
        )
parser.add_argument('-r', '--regex', action='append', type=str)
parser.add_argument('-e', '--exit', action='append', type=int)
parser.add_argument('-n', '--negate', action='store_true')
parser.add_argument('-t', '--timeout', type=int)
parser.add_argument('cmd', nargs=argparse.REMAINDER)
args = parser.parse_args()

failed = False
timed_out = False

process = subprocess.Popen(" ".join(args.cmd), shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

if args.timeout:
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(args.timeout)

stdout=""
stderr=""

try:
    (stdout, stderr) = process.communicate()
except Exception, exc:
    failed = True
    timed_out = True
    process.kill()

signal.alarm(0)
rc = process.wait()

if (args.exit and rc in args.exit) or (not args.exit and rc != 0):
    failed = True

if args.regex:
    exps = [re.compile(exp) for exp in args.regex]
    if stdout and any(exp.search(stdout) for exp in exps):
        failed = True
    if stderr and any(exp.search(stderr) for exp in exps):
        failed = True

if args.negate == True:
    failed = not failed

if failed or timed_out:
    if timed_out:
        print "Command timed out: %s\nTimeout: %d" % (args.cmd, args.timeout)
    else:
        print "Command failed: %s" % args.cmd
    print "Exit status: %d\nStandard Output: %s\nStandardError: %s" % (rc, stdout, stderr)

sys.exit(0)
