#!/usr/bin/env python

import subprocess as sub
import os
import sys

import cephfs as cephfs

prefix='testrestart'

def get_name(b, i, j):
    c = '{pre}.{pid}.{i}.{j}'.format(pre=prefix, pid=os.getpid(), i=i, j=j)
    return c, b + '/' + c

def mkdir(ceph, d):
    print >>sys.stderr, "mkdir {d}".format(d=d)
    ceph.mkdir(d, 0755)
    return ceph.stat(d)['st_ino']

def create(ceph, f):
    print >>sys.stderr, "creating {f}".format(f=f)
    fd = ceph.open(f, os.O_CREAT|os.O_RDWR, 0644)
    ceph.close(fd)
    return ceph.stat(f)['st_ino']

def set_mds_config_param(ceph, param):
    with file('/dev/null', 'rb') as devnull:
        confarg = ''
        if conf != '':
            confarg = '-c {c}'.format(c=conf)
        r = sub.call("ceph {ca} mds tell a injectargs '{p}'".format(ca=confarg, p=param), shell=True, stdout=devnull)
        if (r != 0):
            raise

def conf_set_kill_mds(location, killnum):
    print >>sys.stderr, 'setting mds kill config option for {l}.{k}'.format(l=location, k=killnum)
    print "restart mds a mds_kill_{l}_at {k}".format(l=location, k=killnum)
    sys.stdout.flush()

def wait_for_restart():
    for l in sys.stdin.readline():
        if l == 'restarted':
            break

def kill_mds(ceph, location, killnum):
    print >>sys.stderr, 'killing mds: {l}.{k}'.format(l=location, k=killnum)
    set_mds_config_param(ceph, '--mds_kill_{l}_at {k}'.format(l=location, k=killnum))

conf = ''
if len(sys.argv) > 1:
    conf = sys.argv[1]

print >>sys.stderr, 'mounting ceph'
ceph = cephfs.LibCephFS(conffile=conf)
ceph.mount()

# these are reversed because we want to prepare the config
conf_set_kill_mds('journal_replay', 1)
kill_mds(ceph, 'openc', 1)
print "restart mds a"
sys.stdout.flush()
for i in range(1, 1000):
    c, f = get_name("/", i, 0)
    create(ceph, f)
wait_for_restart()
wait_for_restart()

print >>sys.stderr, 'doing shutdown'
ceph.shutdown()

print "done"
sys.stdout.flush()
