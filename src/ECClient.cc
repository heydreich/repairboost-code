#include <string>
#include <iostream>

#include "Config.hh"
#include "LinesDefine.hh"
#include "LinesFullNodeClientStream.hh"
using namespace std;

double duration(struct timeval t1, struct timeval t2) {
  return (t2.tv_sec-t1.tv_sec) * 1000.0 + (t2.tv_usec-t1.tv_usec) / 1000.0;
}

int main(int argc, char** argv) {
    struct timeval time1, time2;
    gettimeofday(&time1, NULL);
    Config* conf = new Config("conf/config.xml");
    LinesFullNodeClientStream lfs(conf, conf->_packetCnt, conf->_packetSize, conf->_coordinatorIP, conf->_localIP);
    gettimeofday(&time2, NULL);
    cout << "overall duration " << duration(time1, time2) << endl;
    return 0;
}
