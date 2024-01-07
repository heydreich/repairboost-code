# usage
#   python createconf.py
#       1. cluster [lab]
#       2. block_source [standalone|hdfs]
#       3. blockMiB [1]
#       4. pktcount [64]
#       5. code [Clay]
#       6. ecn [4]
#       7. eck [3]
#       8. method [cr]
#       9. PKTSIZE [1048576]

import os
import sys
import subprocess

def usage():
    print("python createconf.py cluster[lab] block_source[standalone|hdfs]")


if len(sys.argv) < 10:
    usage()
    exit()

CLUSTER=sys.argv[1]
block_source=sys.argv[2]
BLKMB=int(sys.argv[3])
pktcount=int(sys.argv[4])
CODE=sys.argv[5]
ECN=int(sys.argv[6])
ECK=int(sys.argv[7])
METHOD=sys.argv[8]   
PKTSIZE=int(sys.argv[9]) 
ECW = int(sys.argv[10])

RECVGROUP=10
SENDGROUP=10
COMPUTEGROUP=10

BLKBYTES=BLKMB*1048576
PKTBYTES=PKTSIZE

ECCSIZE="10"
RPTHREADS="4"

# home dir
cmd = r'echo ~'
home_dir_str, stderr = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).communicate()
home_dir = home_dir_str.decode().strip()

# proj dir
proj_dir="{}/repairboost-code".format(home_dir)
script_dir = "{}/scripts".format(proj_dir)
config_dir = "{}/conf".format(proj_dir)

gen_conf_dir = "{}/conf".format(script_dir)
cluster_dir = "{}/cluster/{}".format(script_dir, CLUSTER)

config_filename = "config.xml"
stripeStore_dir = "{}/meta/standalone-meta".format(proj_dir)
tradeoffPoint_dir = "{}/offline".format(proj_dir)
# blk_dir = "{}/meta/standalone-blocks".format(proj_dir) #
blk_dir = "{}/meta/standalone-blocks/{}_{}_{}_{}_{}".format(proj_dir, CODE, ECN, ECK, ECW, BLKMB)
meta_dir = "{}/meta".format(proj_dir)

if block_source == "hdfs":
   cmd = r'echo $HADOOP_HOME'
   hadoop_home_dir_str, stderr = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).communicate()
   hadoop_home_dir = hadoop_home_dir_str.decode().strip()
   blk_dir = "{}/dfs/data/current".format(hadoop_home_dir)

clusternodes=[]
controller=""
datanodes=[]
repairnodes=[]

# get controller
f=open(cluster_dir+"/controller","r")
for line in f:
    controller=line[:-1]
    clusternodes.append(controller)
f.close()

# get datanodes
f=open(cluster_dir+"/agents","r")
for line in f:
    agent=line[:-1]
    clusternodes.append(agent)
    datanodes.append(agent)
f.close()

# get clients
f=open(cluster_dir+"/newnodes","r")
for line in f:
    node=line[:-1]
    clusternodes.append(node)
    repairnodes.append(node)
f.close()

print(controller)
print(datanodes)
print(repairnodes)
print(clusternodes)

# threads
controller_threads = 4
agent_threads = 4
cmddist_threads = 4
if CLUSTER == "aliyunhdd" or CLUSTER == "lab":
    controller_threads = 20
    agent_threads = 20
    cmddist_threads = 10

for node in clusternodes:

    content=[]

    line="<setting>\n"
    content.append(line)

    line="<attribute><name>erasure.code.type</name><value>"+CODE+"</value></attribute>\n"
    content.append(line)

    line="<attribute><name>erasure.code.k</name><value>"+str(ECK)+"</value></attribute>\n"
    content.append(line)

    line="<attribute><name>erasure.code.n</name><value>"+str(ECN)+"</value></attribute>\n"
    content.append(line)

    line="<attribute><name>lrc.code.l</name><value>"+"0"+"</value></attribute>\n"
    content.append(line)

    line="<attribute><name>encode.matrix.file</name><value>"+ config_dir + "/" + CODE.lower() + "EncMat_" + str(ECK) + "_" + str(ECN) +"</value></attribute>\n"
    content.append(line)

    line="<attribute><name>packet.size</name><value>"+str(PKTBYTES)+"</value></attribute>\n"
    content.append(line)

    line="<attribute><name>packet.count</name><value>"+str(pktcount)+"</value></attribute>\n"
    content.append(line)





    line="<attribute><name>repair.method</name><value>"+METHOD+"</value></attribute>\n"
    content.append(line)

    line="<attribute><name>coordinator.address</name><value>"+controller+"</value></attribute>\n"
    content.append(line)

    line="<attribute><name>file.system.type</name><value>"+block_source+"</value></attribute>\n"
    content.append(line)

    line="<attribute><name>meta.stripe.dir</name><value>"+stripeStore_dir+"</value></attribute>\n"
    content.append(line)

    line="<attribute><name>block.directory</name><value>"+blk_dir+"</value></attribute>\n"
    content.append(line)

    line="<attribute><name>helpers.address</name>\n"
    content.append(line)
    

    for agent in datanodes:
        line="<value>default/"+agent+"</value>\n"
        content.append(line)

    line="</attribute>\n"
    content.append(line)

    # line="<attribute><name>repairnodes.addr</name>\n"
    # content.append(line)

    # for client in repairnodes:
    #     line="<value>"+client+"</value>\n"
    #     content.append(line)

    # line="</attribute>\n"
    # content.append(line)

    # line="<attribute><name>block.bytes</name><value>"+str(BLKBYTES)+"</value></attribute>\n"
    # content.append(line)

    # line="<attribute><name>packet.bytes</name><value>"+str(PKTBYTES)+"</value></attribute>\n"
    # content.append(line)

    # line="<attribute><name>code.name</name><value>"+CODE+"</value></attribute>\n"
    # content.append(line)

    # line="<attribute><name>code.ecn</name><value>"+str(ECN)+"</value></attribute>\n"
    # content.append(line)

    # line="<attribute><name>code.eck</name><value>"+str(ECK)+"</value></attribute>\n"
    # content.append(line)

    # line="<attribute><name>code.ecw</name><value>"+str(ECW)+"</value></attribute>\n"
    # content.append(line)

    # line="<attribute><name>batch.size</name><value>"+str(PKTSIZE)+"</value></attribute>\n"
    # content.append(line)

    # line="<attribute><name>recvgroup.size</name><value>"+str(RECVGROUP)+"</value></attribute>\n"
    # content.append(line)

    # line="<attribute><name>sendgroup.size</name><value>"+str(SENDGROUP)+"</value></attribute>\n"
    # content.append(line)

    # line="<attribute><name>computegroup.size</name><value>"+str(COMPUTEGROUP)+"</value></attribute>\n"
    # content.append(line)

    # line="<attribute><name>controller.thread.num</name><value>"+str(controller_threads)+"</value></attribute>\n"
    # content.append(line)

    # line="<attribute><name>agent.thread.num</name><value>"+str(agent_threads)+"</value></attribute>\n"
    # content.append(line)

    # line="<attribute><name>cmddist.thread.num</name><value>"+str(cmddist_threads)+"</value></attribute>\n"
    # content.append(line)

    line="<attribute><name>local.ip.address</name><value>"+node+"</value></attribute>\n"
    content.append(line)

    # line="<attribute><name>block.directory</name><value>"+blk_dir+"</value></attribute>\n"
    # content.append(line)

    # line="<attribute><name>stripestore.directory</name><value>"+stripeStore_dir+"</value></attribute>\n"
    # content.append(line)

    # line="<attribute><name>tradeoffpoint.directory</name><value>"+tradeoffPoint_dir+"</value></attribute>\n"
    # content.append(line)

    #line="<attribute><name>eccluster.size</name><value>"+ECCSIZE+"</value></attribute>\n"
    #content.append(line)

    #line="<attribute><name>repair.thread.num</name><value>"+RPTHREADS+"</value></attribute>\n"
    #content.append(line)

    line="</setting>\n"
    content.append(line)

    f=open("config.xml","w")
    for line in content:
        f.write(line)
    f.close()

    cmd="scp config.xml {}:{}".format(node, config_dir)
    print(cmd)
    os.system(cmd)

    cmd="rm config.xml"
    print(cmd)
    os.system(cmd)

    print("finished create conf on node", node)