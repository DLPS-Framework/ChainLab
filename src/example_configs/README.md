# How to create configs

1. How to fill the config

* every attribute must have either length 1 or length n where n = number_of_setups
* in the first case, all tests are conducted with the given specification
* in the second case, the ith test is conducted with specifications[i-1] and so on
* several example configs are given in this directory
* for every specification of (blockchain_formation_config + client_formation_config), all specifications of experiment_config will be performed

2. Directory Structure 
* one for BlockchainFormation
* one for client setup
* one for actual experiment (also with data/time nomenclature, and containing a subfolder for every experiment, which in turn has on the highest level a config file specifying the blockchain and client setup and on the next level (names again datetime) the experiment settings)


