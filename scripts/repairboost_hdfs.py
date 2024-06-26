

import os
import sys
import subprocess
import time

def usage():
    print("""
        #usage:
        #   python fullnode.py
        #       1.  cluster [lab]
        #       2.  CODE [RS|LRC|BUTTERFLY]
        #       3.  ECN [4]
        #       4.  ECK [3]
        #       5.  ECW [0] The number of groups, only valid in LRC. Default is 0.
        #       6.  method [cr|ppr|path]
        #       7.  blkMiB [1|256] MB
        #       8.  pktKiB [1|64] the size of packet, input 64 means 64K ,blkMiB need to be divided by PKTSIZE
        #       9.  num stripes [20]
        #       10. gendata [true|false]: gen meta from hdfs
        #       11. cleandata [true|false]
        #       12. setbandwidth []
        """)

if len(sys.argv) < 11:
    usage()
    exit()

CLUSTER=sys.argv[1]
CODE=sys.argv[2]
ECN=int(sys.argv[3])
ECK=int(sys.argv[4])
ECW=int(sys.argv[5])
METHOD=sys.argv[6]
BLKMB=int(sys.argv[7])
PKTKB=int(sys.argv[8])
NSTRIPE=int(sys.argv[9])
GENDATASTR=sys.argv[10]
CLEANDATA = sys.argv[11]
BANDWIDTH = int(sys.argv[12])
# NTEST=int(sys.argv[13]) #?
NTEST=1


PKTSIZE = PKTKB * 1024

pktcount = BLKMB * 1048576 / PKTSIZE


gendata=False
if GENDATASTR == "true":
    gendata = True
# print(gen)

cleandata = False
if CLEANDATA == "true":
    cleandata = True

# sizes
filesize_MB = int(BLKMB * ECK)
filesize_bytes = int(filesize_MB * 1048576)
block_bytes = int(BLKMB * 1048576)
packet_bytes = int(PKTKB * 1024)

print("filesize_bytes: "+str(filesize_bytes))
print("block_bytes: "+str(block_bytes))
print("packet_bytes: "+str(packet_bytes))

# BLOCKSOURCE="standalone"
BLOCKSOURCE="HDFS3"
FAILNODEID=0

# home dir
cmd = r'echo ~'
home_dir_str, stderr = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).communicate()
home_dir = home_dir_str.decode().strip()

# proj dir
proj_dir="{}/repairboost-code".format(home_dir)
script_dir="{}/scripts".format(proj_dir)
data_dir="{}/data".format(script_dir)
conf_dir="{}/conf".format(script_dir)
cache_dir="{}/cache".format(script_dir)
exe="{}/build/ParaCoordinator".format(proj_dir)
cluster_dir = "{}/cluster/{}".format(script_dir, CLUSTER)

blk_dir = "{}/meta/standalone-blocks/{}_{}_{}_{}_{}".format(proj_dir, CODE, ECN, ECK, ECW, BLKMB)

network_dir="{}/network".format(script_dir)


# 0. stop parafullnode
cmd="cd {}; python stop.py".format(script_dir)
os.system(cmd)

# 1. gen data
if cleandata:
    cmd="cd {}; python clean_standalone_data.py {} {} {} {} {} {} {}".format(data_dir, CLUSTER, NSTRIPE, CODE, ECN, ECK, ECW, BLKMB)
    # print(cmd)
    os.system(cmd)

# gendate = true
if gendata:
    for i in range(NSTRIPE):
        cmd="cd {}; python3 genmeta_from_hdfs_fullnode_repairboost.py -code {} -n {} -k {} -w {} -bs {} -ps 1 -filename /{}_{}_{}_{} -stripename {}_{}{}{}_{}".format(
            data_dir, CODE, ECN, ECK, ECW,
            str(block_bytes),
            CODE, ECN, ECK, i,
            CODE, ECN, ECK, ECW, i,)
        print(cmd)
        os.system(cmd)

# 2. create configuration file for parafullnode
cmd="cd {}; python createconf.py {} {} {} {} {} {} {} {} {} {}".format(conf_dir, CLUSTER, BLOCKSOURCE, BLKMB, pktcount, CODE, ECN, ECK, METHOD, PKTSIZE, ECW)
os.system(cmd)

# 3. clear cache
cmd="cd {}; python clearcache.py {}".format(cache_dir, CLUSTER)
os.system(cmd)

# 4. set bdwt
cmd="cd {}; python setbdwt.py {} {}".format(network_dir, CLUSTER, BANDWIDTH)
os.system(cmd)

time.sleep(2)

# 5. start
cmd="cd {}; python start.py".format(script_dir)
os.system(cmd)

# 6. run
for i in range(NTEST):
    agentnodes=[]
    f=open(cluster_dir+"/agents","r")
    for line in f:
        agent=line[:-1]
        agentnodes.append(agent)
    f.close()

    agent = agentnodes[FAILNODEID]
    # cmd="ssh {} \"rm {}/*\"".format(agent, blk_dir)
    # os.system(cmd)

    # cmd="ssh {} \"cd {}; ./ECClient &> client_output \"".format(agent, proj_dir)
    # print(cmd)
    # res=subprocess.Popen(['/bin/bash','-c',cmd], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # out, err = res.communicate()

    # print(out)

    cmd="ssh {} \"cd {}; ./ECClient \"".format(agent, proj_dir)
    print(cmd)
    os.system(cmd)


#out = out.split("\n")
#for line in out:
#    if line.find("repairtime") != -1:
#        print(line)

# 7. unset bdwt
cmd="cd {}; python clearbdwt.py {}".format(network_dir, CLUSTER)
os.system(cmd)

# 8. stop parafullnode
cmd="cd {}; python stop.py".format(script_dir)
os.system(cmd)
