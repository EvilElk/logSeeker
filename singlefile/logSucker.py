__author__ = 'elk'

from fabric.api import *
from fabric.operations import get
from fabric.operations import put
import os
import json

env.jSrvLog = {}


@parallel
def test():
    print(env.host_string)
    run('uname -a')


def set_env(srvString):
    env.jSrvLog = json.loads(srvString, encoding="utf-8")
    env.hosts = env.jSrvLog.keys()
    print(env.hosts)


def getLogs(start='', fin=''):
    print(env.host_string, env.hosts, env.jSrvLog)
    put('sfFilter.py', '/var/tmp/sfFilter.py')
    log = env.jSrvLog[env.host_string]
    targetFile = '{server}.filtered.{logName}'.format(server=env.host_string, logName=os.path.split(log)[1])
    run('python /var/tmp/sfFilter.py \'{start}\' \'{fin}\' {logfile} >/var/tmp/{tLog}'.format(start=start, fin=fin, logfile=log, tLog=targetFile))
    get('/var/tmp/' + targetFile, targetFile)
    run('rm /var/tmp/' + targetFile)
    run('rm /var/tmp/sfFilter.py')
    pass
#parallel execution, pool_size limits Fabric to a specific number of concurrently active processes
#@parallel(pool_size=5)
#def heavy_task():
#     pass