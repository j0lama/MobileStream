**NOTE**: This repository has been cloned from https://gitlab.flux.utah.edu/junguk/mobilestream-profile

# MobileStream
This is a repository for mobilestream.

## Requirements
1. Currently, MCC and MNC are configured `998` and `98` and ip addr of mme is `192.168.4.80`. So, enb uses the same numbers.
* MCC : 998
* MNC : 98

2. Disk images in testbed
* Since MobileStream requires a lot of setup, it is easy to use testbed image in your experiment.
- `urn:publicid:IDN+emulab.net+image+PhantomNet:mobilestream-v1`

## MobileStream Setup
1. Set up redis, storm, and ZooKeeper.
```shell
# It runs redis, storm and all.
cd /opt/mobilestream-conext/mobilestreamconext/testbed/storm
bash setup_mobilestream.sh
```

2. Check storm UI with <node ip>:8080 


3. Run EPC example on mobileStream
```shell
cd /opt/mobilestream-conext/mobilestreamconext/MobileStream-Java
bash run-stateless-control-plane.sh 1 2
```

4. Advance
* Configure `run-stateless-control-plane` script
* You can adjust the number of worker except for sctp to use high computation parallelism for s1ap, nas, and security. The sum of all components is the number for `workers` variable in `run-stateless-control-plane` script.
```shell
sctp=1
s1ap=1
nas=1
security=1
auc=1
signal=0
workers=5
```

5. storm multi-cluster
* You need to configure `/opt/mobilestream-conext/storm/apache-storm-2.0.0/conf/storm.yaml`
* [Setting up a Storm Cluster](http://storm.apache.org/releases/current/Setting-up-a-Storm-cluster.html) 

## User information
1. Set up user information
* Currently, MobileStream uses `LTE_fdd_enodeb.user_db` file to store user information.
* The file is located in `/tmp` and read in HSS block.
* Example in `/opt/mobilestream-conext/mobilestreamconext/testbed/hss/LTE_fdd_enodeb.user_db` 
'''
* We are not sure where `Auc` is run, so putting `LTE_fdd_enodeb.user_db` file on all nodes is safe if you use multi storm cluster

## Compile MobileStream codes
```shell
# JNI
cd /opt/mobilestream-conext/mobilestreamconext/MobileStream-Java/src/jvm/
bash JNIHeader.sh

# C++
cd /opt/mobilestream-conext/mobilestreamconext/MobileStream-C++
mkdir build
cd build
cmake ../
make -j4

# Install storm apps
cd /opt/mobilestream-conext/mobilestreamconext/MobileStream-Java
bash compile-app.sh
```
## Tools
1. Check Redis DB
```shell
cd /opt/mobilestream-conext/mobilestreamconext/Tools/RedisClient
mvn install
./redis-client-in-phantomnet.sh 192.168.4.80 6379
```

2. Clean up Redis DB
```shell
cd /opt/mobilestream-conext/mobilestreamconext/Tools/RedisClient
./cleanup-local-redis.sh 192.168.4.80
```

3. Shutdown Redis DB
```shell
redis-cli -h 192.168.4.80
> shutdown
```

## Storm Tips
1. Location of log files for the storm application
```shell
cd /opt/mobilestream-conext/storm/apache-storm-2.0.0/logs/workers-artifacts/
```

2. [Storm command line](https://storm.apache.org/releases/current/Command-line-client.html)
```shell
/opt/mobilestream-conext/storm/apache-storm-2.0.0/bin/storm list
/opt/mobilestream-conext/storm/apache-storm-2.0.0/bin/storm kill <app name>
```

3. Storm location in testbed image
* storm binary `/opt/mobilestream-conext/storm/apache-storm-2.0.0/bin/storm`
* storm cluster configuration file : `/opt/mobilestream-conext/storm/apache-storm-2.0.0/conf/storm.yaml`
* More about configuration, refer to [Setting up a Storm Cluster](http://storm.apache.org/releases/current/Setting-up-a-Storm-cluster.html)


## TroubleShooting
1. Error after submitting storm app
```shell
Start uploading file './target/mobilestream-2.0.0.jar' to '/opt/mobilestream-conext/storm/storage/nimbus/inbox/stormjar-d20ad415-fac7-4e3e-8b3e-7a7a6ed46c71.jar' (165598267 bytes)
[==================================================] 165598267 / 165598267
File './target/mobilestream-2.0.0.jar' uploaded to '/opt/mobilestream-conext/storm/storage/nimbus/inbox/stormjar-d20ad415-fac7-4e3e-8b3e-7a7a6ed46c71.jar' (165598267 bytes)
14:04:04.825 [main] INFO  o.a.s.StormSubmitter - Successfully uploaded topology jar to assigned location: /opt/mobilestream-conext/storm/storage/nimbus/inbox/stormjar-d20ad415-fac7-4e3e-8b3e-7a7a6ed46c71.jar
14:04:04.826 [main] INFO  o.a.s.StormSubmitter - Submitting topology LegacyEpcTopologyWithShuffling in distributed mode with conf {"redisHost":"192.168.4.80","storm.zookeeper.topology.auth.scheme":"digest","storm.zookeeper.topology.auth.payload":"-7053767142693196806:-4811162087935435866","nimbus.host":"localhost","topology.workers":5,"topology.debug":false}
Exception in thread "main" java.lang.RuntimeException: org.apache.storm.thrift.TApplicationException: Internal error processing submitTopology
        at org.apache.storm.StormSubmitter.submitTopologyAs(StormSubmitter.java:274)
        at org.apache.storm.StormSubmitter.submitTopology(StormSubmitter.java:387)
        at org.apache.storm.StormSubmitter.submitTopologyWithProgressBar(StormSubmitter.java:422)
        at org.apache.storm.StormSubmitter.submitTopologyWithProgressBar(StormSubmitter.java:403)
        at mobilestream.topology.legacyEPCWithShuffleRouting.LegacyEpcTopologyWithShuffling.main(LegacyEpcTopologyWithShuffling.java:82)
Caused by: org.apache.storm.thrift.TApplicationException: Internal error processing submitTopology
        at org.apache.storm.thrift.TServiceClient.receiveBase(TServiceClient.java:79)
        at org.apache.storm.generated.Nimbus$Client.recv_submitTopology(Nimbus.java:319)
        at org.apache.storm.generated.Nimbus$Client.submitTopology(Nimbus.java:303)
        at org.apache.storm.StormSubmitter.submitTopologyInDistributeMode(StormSubmitter.java:327)
        at org.apache.storm.StormSubmitter.submitTopologyAs(StormSubmitter.java:262)
```
* Solution
```shell
cd /opt/mobilestream-conext/mobilestreamconext/MobileStream-Java
bash clean.sh

# if it keeps showing the error, restart storms
cd /opt/mobilestream-conext/mobilestreamconext/testbed/storm
bash kill_storm.sh
bash start_storm.sh
```
