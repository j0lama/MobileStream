# Setup Radio Access Network (RAN) components
## 1. MobileStream with emulated eNBs from OpenEPC 
`Note : To use emulated eNBS from OpenEPC, you need to submit OpenEPC sub-lisense agreement.`   
Please refer to [OpenEPC Sublicese](https://wiki.emulab.net/wiki/phantomnet/openepc-sublicense).   
You can test initial attachment, detach, service request and s1 intra handover mobile events with eNB emulator(s) from OpenEPC.

### Access to `enb1` node.
* Attach to a console of eNB emulator   
$ /opt/OpenEPC/bin/enodeb.attach.sh

* Trigger mobile events from a console of eNB emulator
1. initial attachment <imsi> <apn> <start> <max>   
enodeb> enodeb.attach 998981000000000 default 1 1

2. service request <imsi> <apn> <start> <max>   
enodeb> enodeb.attach 998981000000000 default 1 1

3. S1 release <imsi> <apn> <start> <max>   
enodeb> enodeb.detach 998981000000000 default 1 1

4. intra s1 handover <imsi> <tac> <target cell id> <start> <max>   
eNodeB > enodeb.intra_lte_handover 998981000000000 01 4568 1 1



### Start/Kill eNB emulator  
* Start eNB emulator    
$ sudo /opt/OpenEPC/bin/enodeb.start.sh   

* Kill eNB emulator    
$ sudo /opt/OpenEPC/bin/enodeb.kill.sh   


## 2. MobileStream with srsUE and srseNB from srsLTE 
###  Access to `srseNB` node.
* Run srseNB   
$ cd /local/repository/config/srsLTE/srsenb    
$ sudo ./run_enb.sh


### Access to `srsUE` node.  
* Run srsLTE UE  
$ cd /local/repository/config/srsLTE/srsue   
$ sudo ./run_ue.sh

If you see `Network attach successful. IP: 172.16.0.6` (note that you may get different IP address) output after running srsue, ue is correctly connected and this is ip address assigned for the ue.  
* Note : Default configurations of UE subscription and Radio to use SDR-version UE.
1. User subscription info  
imsi : 998981234560308  
algo : milenage  
op   : 01020304050607080910111213141516  
k    : 00112233445566778899aabbccddeeff  
amf  : 8000  

2. LTE band : 4  