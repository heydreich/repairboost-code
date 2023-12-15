# usage:
# python gen_simulation_data.py
#   1. cluster [lab]
#   2. number of stripes [100]
#   3. code [Clay]
#   4. ecn [4]
#   5. eck [3]
#   6. ecw [4]
#   7. blkMB [1]
#   8. fail node id [0]


import os
import random
import sys
import subprocess
import time

if len(sys.argv) != 9:
    exit()

CLUSTER=sys.argv[1]
NSTRIPES=int(sys.argv[2])
CODE=sys.argv[3]
ECN=int(sys.argv[4])
ECK=int(sys.argv[5])
ECW=int(sys.argv[6])
BLKMB=int(sys.argv[7])
FAILID=int(sys.argv[8])

BLKBYTES=BLKMB * 1048576

# home dir
cmd = r'echo ~'
home_dir_str, stderr = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).communicate()
home_dir = home_dir_str.decode().strip()

# proj dir
proj_dir="{}/repairboost-code".format(home_dir)
stripestore_dir = "{}/meta/standalone-meta".format(proj_dir)
script_dir = "{}/scripts".format(proj_dir)
blk_dir1 = "{}/meta/standalone-blocks".format(proj_dir)

meta_dir = "{}/meta".format(proj_dir)
filename = "{}_{}_{}_{}_{}".format(CODE, ECN, ECK, ECW, BLKMB)
blk_dir = blk_dir1 + "/" + filename

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

failnode=agentnodes[FAILID]
print(failnode)

#print(controller)
#print(agentnodes)
#print(repairnodes)

# format of metadata file
# each line includes the placement of a stripe
# example of a line: stripe-name blk0:loc0 blk1:loc1 blk2:loc2 ...
# meaning:
#       stripe-name: the name of a stripe
#       blki: the name of the i-th block
#       loci: the ip of the physical nodes that stores the i-th block

# the goal of this script is to generate placement of NSTRIPES stripes
placement=[]

# print(filename)

for root, dirs, files in os.walk(blk_dir1):
    for name in dirs:
        # print(name)
        if name == filename :
            exit()
cmd = "mkdir -p {} {}".format(blk_dir, stripestore_dir)
print(cmd)
os.system(cmd)




for stripeid in range(NSTRIPES):
    stripename = "{}-{}{}{}-{}".format(CODE, ECN, ECK, ECW, stripeid)



    blklist=[]
    blklist_plus=[]
    loclist=[]
    line = ""
    for blkid in range(ECN):

        if blkid < ECK:
            blkname = "stripe_{}_file_k{}".format(stripeid, blkid + 1)
            blkname_plus = blkname + "_1001"
        else:
            blkname = "stripe_{}_file_m{}".format(stripeid, blkid - ECK + 1)
            blkname_plus = blkname + "_1002"

        line += blkname_plus + ":"

        blklist.append(blkname)
        blklist_plus.append(blkname_plus)

        tmpid = random.randint(0, len(agentnodes)-1)
        tmploc = agentnodes[tmpid]

        while tmploc in loclist:
            tmpid = random.randint(0, len(agentnodes)-1)
            tmploc = agentnodes[tmpid]

        loclist.append(tmploc)

    line = line[:-1]
    for blkid in range(ECN):
        filepath="{}/{}:{}".format(stripestore_dir, CODE.lower(), blklist_plus[blkid])
        f=open(filepath, "w")
        f.write(line)
        f.close()


    if agentnodes[0] not in loclist:
        idx = random.randint(0, ECN-1)
        loclist[idx] = failnode

    #print(blklist)
    #print(loclist)

    line = stripename + " "
    for i in range(ECN):
        line += blklist[i] + ":" + loclist[i] + " "
    line += "\n"
    placement.append(line)

    # ssh to loclist[i] and generate a blklist[i]
    for i in range(len(blklist)):
        cmd = "ssh {} \"mkdir -p {}; mkdir -p {}; dd if=/dev/urandom of={}/{} bs={} count=1 iflag=fullblock\"".format(loclist[i], blk_dir, stripestore_dir, blk_dir, blklist[i], BLKBYTES)
        print(cmd)
        os.system(cmd)

# now we write placement into a file in stripestore
ssfilename="placement"
filepath="{}/{}".format(meta_dir, ssfilename)







f=open(filepath, "w")
for line in placement:
    f.write(line)
f.close()

