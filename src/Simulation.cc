#include "LinesDefine.hh"
#include "LinesCoordinator.hh"
#include "LinesDealScheduling.hh"
#include <sstream>

LinesDealScheduling lds111;



using namespace std;

void usage() {
    cout << "Usage: ./Simulation " << endl;
    cout << "   1. agent num" << endl;
    cout << "   2. strips num" << endl;
    cout << "   3. fail node id" << endl;
    
}

//split method
std::vector<std::string> stringSplit(const std::string& str, char delim) {
    std::stringstream ss(str);
    std::string item;
    std::vector<std::string> elems;
    while (std::getline(ss, item, delim)) {
        if (!item.empty()) {
            elems.push_back(item);
        }
    }
    return elems;
}


int main(int argc, char** argv) {
    Config* _conf = new Config("simulation/config.xml");

    if (argc < 4) {
        usage();
        return 0;
    }

    int agent_num = atoi(argv[1]);
    int num_stripes = atoi(argv[2]);
    int fail_node = atoi(argv[3]);
    int _ecN = _conf -> _ecN ;
    int _ecK = _conf -> _ecK;
    string proj_dir = "./simulation/";
    lds111.initConf2(_conf, agent_num);


    // 读入placement文件, 生成如下所需信息
    ifstream ifs;
    string filename = proj_dir + "simulation_" + to_string(agent_num)
        + "_" + to_string(num_stripes) + "_" +
        to_string(_ecN) + "_" + to_string(_ecK);
    ifs.open(filename, ios::in);

    if (!ifs.is_open()) {
        cout << "read file failed!" << endl;
        return 0;
    }

    int lostBlkCnt = 0;

    string buf;
    vector<string> strlist;
    vector<int> loststripe;
    int i = 0;
    while (getline(ifs, buf)) {
        strlist = stringSplit(buf, ' ');
        for (string nodes : strlist) {
            if (stoi(nodes) == fail_node) {
                lostBlkCnt++;
                loststripe.push_back(i);
                break;
            }
        }
        i++;
    }
    cout << "lostBlkCnt = " << lostBlkCnt << " should = " << loststripe.size() << endl;

    int* idxs = (int*)malloc(lostBlkCnt * sizeof(int));
    int* placement = (int*)malloc(_ecN * lostBlkCnt * sizeof(int));
    int* isSoureCandidate = (int*)malloc(_ecN * lostBlkCnt * sizeof(int));

    i = 0;
    int num = 0;
    ifs.close();
    ifs.open(filename, ios::in);
    while (getline(ifs, buf)) {
        strlist = stringSplit(buf, ' ');
        if (loststripe[num] != i++) break;
        int j = 0;
        for (string nodes : strlist) {
            if (stoi(nodes) == fail_node) idxs[num] = j;
            placement[num * _ecN + j] = stoi(nodes);
            isSoureCandidate[num * _ecN + j] = 1;
            j++;
        }
        num++;
        // cout << "num:" << num << endl;
    }
    int repairMethod = _conf -> _chunkRepairMethod;



    clock_t start,end;
    start = clock();
    vector<Stripe> stripes = lds111.repairboost(fail_node, repairMethod, lostBlkCnt, idxs, placement, isSoureCandidate);
    end = clock();
    cout << " time = " << double(end - start) / CLOCKS_PER_SEC << "s" << endl;
    
    
    
    
    
    cout << "simulaiton success" << endl;
    int MaxRepairTime = 0;
    ofstream ofs;
    ofs.open(proj_dir + "output", ios::out);
    for(int i = 0; i < stripes.size(); i++) {
        Stripe stripe = stripes[i];
        int temp = stripe.dump2(&ofs);
        if (MaxRepairTime < temp) MaxRepairTime = temp;
    }

    // ofs << "placement = " << endl;
    // for(int i =0; i < lostBlkCnt; ++i) {
    //     for(int j = 0; j < _ecN; j++) {
    //         ofs << placement[i*_ecN+j] << " ";
    //     }
    //     ofs << endl;
    // }

    cout << "MaxRepairTime: " << MaxRepairTime << endl;

    ifs.close();
    ofs.close();
    return 0;
}
