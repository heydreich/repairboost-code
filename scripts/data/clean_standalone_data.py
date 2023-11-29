# usage:
# python clean_standalone_data.py
#   1. cluster [lab]


import os
import random
import sys
import subprocess
import time

if len(sys.argv) != 4:
    exit()

CLUSTER=sys.argv[1]
NSTRIPE=int(sys.argv[2])
CODE=sys.argv[3]


# home dir
cmd = r'echo ~'
home_dir_str, stderr = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).communicate()
home_dir = home_dir_str.decode().strip()

# proj dir
proj_dir="{}/repairboost-code".format(home_dir)
# stripestore_dir = "{}/stripeStore".format(proj_dir)
stripestore_dir = "{}/meta/standalone-meta".format(proj_dir)
script_dir = "{}/scripts".format(proj_dir)
blk_dir = "{}/meta/standalone-blocks".format(proj_dir)
meta_dir = "{}/meta".format(proj_dir)

data_script_dir = "{}/data".format(script_dir)
cluster_dir = "{}/cluster/{}".format(script_dir, CLUSTER)

# read cluster structure
clusternodes=[]
controller=""
agentnodes=[]
repairnodes=[]
failnode=""

# read controller
f=open(cluster_dir+"/controller","r")
for line in f:
    controller=line[:-1]
    clusternodes.append(controller)
f.close()

# read agentnodes
f=open(cluster_dir+"/agents","r")
for line in f:
    agent=line[:-1]
    clusternodes.append(agent)
    agentnodes.append(agent)
f.close()

# read repairnodes
f=open(cluster_dir+"/newnodes","r")
for line in f:
    node=line[:-1]
    clusternodes.append(node)
    repairnodes.append(node)
f.close()

# remove stripestore
cmd="rm {}/{}:stripe*".format(stripestore_dir, CODE.lower())
print(cmd)
os.system(cmd)
cmd="rm {}/placement".format(meta_dir, CODE.lower())
print(cmd)
os.system(cmd)


# remove blk
for agent in agentnodes:
    cmd="ssh {} \"rm {}/*\"".format(agent, blk_dir)
    print(cmd)
    os.system(cmd)
    cmd="ssh {} \"rm {}/*\"".format(agent, stripestore_dir)
    print(cmd)
    os.system(cmd)