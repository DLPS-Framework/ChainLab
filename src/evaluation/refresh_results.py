#  Copyright 2020  ChainLab
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.


import json
import numpy as np
import os
import copy
import logging
from BlockchainFormation.utils.utils import datetimeconverter
from src.Experiment_Handler import Evaluation_Handler

from src.benchmarking.benchmarking import evaluate_benchmarking_test
from src.benchmarking.benchmarking import result_init
from src.benchmarking.benchmarking import result_update
from src.benchmarking.benchmarking import plot_aggregate_chart

def main():
    """
    TODO
    :return:
    """
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)

    dir_name = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    print("Loading filter config")
    try:
        json_file = open(f"{dir_name}/example_configs/evaluation/paperplots.json")
        # json_file = open(f"{dir_name}/example_configs/evaluation/presentation.json")
        filter = json.load(json_file)
    except Exception as e:
        print(e)

    # collects all the experimental results which satisfy the conditions in the filter presentation.json
    configs = []
    results = []
    count = 0

    # for rootdir in filter["directories"]:
    for rootdir in [1]:
        rootdir = os.path.join(os.path.dirname(os.path.dirname(dir_name)), f"Benchmarking-Results/{rootdir}")
        print(f"Searching for experiments in {rootdir}...")
        # find all the experiment folders
        for subdir1, dirs1, files1 in os.walk(rootdir):
            print(f"Found {len(dirs1)} potential experiments - browsing...")
            for index1, dir1 in enumerate(dirs1):
                # check whether the directory name starts with "exp"
                if dir1[0:4] != 'exp_':
                    print(f"    Omitting {dir1} because its name does not start with 'exp_'")
                    continue
                # elif int(dir1[9:11]) < 4 or (int(dir1[9:11]) == 3 and int(dir1[12:14]) < 15):
                    # print("    Checked already")
                    # continue
                else:
                    pass
                    # print(f"    Examining {dir1}")

                # look whether the experiment directory has the expected shape
                for subdir2, dirs2, files2 in os.walk(os.path.join(rootdir, dir1)):
                    # print(f"        Loading {os.path.join(os.path.join(rootdir, dir1),'config.json')}")
                    if len(files2) >= 1 and files2[0] == "config.json":

                        exp_dir = subdir2.split("/")[-1]
                        exp_dir = subdir2

                        for dir2 in dirs2:
                            for subdir3, dirs3, files3 in os.walk(os.path.join(subdir2, dir2)):

                                try:
                                    json_file = open(os.path.join(subdir3, "config.json"))
                                    config = json.load(json_file)

                                    # Modifying and saving it

                                    # os.system(f"rm {os.path.join(subdir3, 'config.json')}")

                                    config_new = {}
                                    try:
                                        config_new['blockchain_formation_settings'] = config['setup_config']['blockchain_formation_settings']
                                        config_new['client_settings'] = config['setup_config']['client_settings']
                                        config_new['experiment_settings'] = config['experiment_settings']

                                    except Exception:

                                        config_new = copy.deepcopy(config)

                                    json_file2 = open(os.path.join(subdir2, "config.json"), "w+")
                                    json.dump(config_new, json_file2, indent=4)
                                    json_file2.close()



                                    # this section reworks the config files in case there are new or renamed config keys
                                    if True:

                                        config_new = copy.deepcopy(config)

                                        if config['blockchain_formation_settings']['blockchain_type'] == 'fabric':


                                            external = 0
                                            try:
                                                external = config_new['blockchain_formation_settings']['fabric_settings']["external"]
                                                print(config_new['blockchain_formation_settings']['fabric_settings'].pop("external"))

                                            except:
                                                try:
                                                    external = config_new['blockchain_formation_settings']['fabric_settings']["external_database"]
                                                    print(config_new['blockchain_formation_settings']['fabric_settings'].pop("external_database"))
                                                except:
                                                    pass

                                            config_new['blockchain_formation_settings']['fabric_settings']['external_database'] = external

                                            internal = 0
                                            try:
                                                internal = config_new['blockchain_formation_settings']['fabric_settings']["internal"]
                                                print(config_new['blockchain_formation_settings']['fabric_settings'].pop("internal"))

                                            except:
                                                try:
                                                    internal = config_new['blockchain_formation_settings']['fabric_settings']["internal_orderer"]
                                                    print(config_new['blockchain_formation_settings']['fabric_settings'].pop("internal_orderer"))
                                                except:
                                                    pass

                                            config_new['blockchain_formation_settings']['fabric_settings']['internal_orderer'] = internal

                                        json_file = open(os.path.join(subdir3, "config.json"), "w+")
                                        json.dump(config_new, json_file, indent=4)
                                        json_file.close()


                                        json_file2 = open(os.path.join(subdir2, "config.json"))
                                        config2 = json.load(json_file2)

                                        config2["blockchain_formation_settings"] = config_new["blockchain_formation_settings"]
                                        json_file2.close()
                                        json_file2 = open(os.path.join(subdir2, "config.json"), "w+")
                                        json.dump(config2, json_file2, indent=4)

                                        try:
                                            json_file2 = open(os.path.join(subdir3, "result.json"))
                                            result = json.load(json_file2)

                                            result["blockchain_config"] = config_new["blockchain_formation_settings"]
                                            json_file2.close()
                                            json_file2 = open(os.path.join(subdir3, "result.json"), "w+")
                                            json.dump(result, json_file2, indent=4)
                                        except Exception as e:
                                            pass
                                            # logger.exception(e)

                                        # break

                                except Exception as e:
                                    print(e)
                                    print(f"        Could not open {os.path.join(subdir3, 'config.json')}")
                                    break

                                blockchain_config = config['blockchain_formation_settings']
                                client_config = config['client_settings']
                                experiment_config = config['experiment_settings']

                                for dir3 in dirs3:

                                    for subdir4, dirs4, files4 in os.walk(os.path.join(os.path.join(subdir3, dir3), "data")):

                                        freqs = []

                                        try:
                                            for file in files4:
                                                freqs.append(int(file.split('_', 1)[0].replace("freq", "")))
                                        except:
                                            for file in files4:
                                                freqs.append(round(float(file.split('_', 1)[0].replace("freq", "")), 1))

                                        temp = np.unique(freqs)


                                        freqs = []
                                        for freq in temp:
                                            freqs.append(f'{freq}')

                                        print(f"freqs: {freqs}")
                                        result = result_init(blockchain_config)

                                        evaluation_handler = Evaluation_Handler(blockchain_config, client_config, logger)

                                        for freq in freqs:

                                            test_config = {}
                                            test_config['exp_dir'] = os.path.join(os.path.join(subdir3, dir3))
                                            test_config['freq'] = freq
                                            test_config['rep'] = ""

                                            try:

                                                # raise Exception("Omit")

                                                res, r_value = evaluate_benchmarking_test(evaluation_handler, experiment_config, test_config, True, True)

                                                result = result_update(result, res, blockchain_config)

                                            except Exception as e:
                                                logger.exception(e)
                                                # logger.warning(f"exp_dir: {test_config['exp_dir']}, freq {test_config['freq']}")
                                                reps = []
                                                for file in files4:
                                                    if file.count("_") != 6 or file.split("_", 1)[0].replace("freq", "") != freq:
                                                        continue
                                                    reps.append(int(file.split('_', 6)[-2].replace('.csv', '')))

                                                reps = np.unique(reps)
                                                print(reps)

                                                for rep in reps:

                                                    second_reps = []
                                                    for file in files4:
                                                        if file.count("_") != 6 or file.split("_", 1)[0].replace("freq", "") != freq:
                                                            continue
                                                        second_reps.append(int(file.split('_', 6)[-1].replace('.csv', '')))

                                                    second_reps = np.unique(second_reps)
                                                    print(second_reps)

                                                    for second_rep in second_reps:
                                                        test_config['rep'] = f"_{rep}_{second_rep}"

                                                        res, r_value = evaluate_benchmarking_test(evaluation_handler, experiment_config, test_config, True, True)

                                                        result = result_update(result, res, blockchain_config)

                                                logger.info(f"Current result: {result}")
                                                continue



                                        try:
                                            print(f"Writing result in {test_config['exp_dir']}")

                                            plot_aggregate_chart(evaluation_handler, blockchain_config, test_config, result)

                                            with open(f"{test_config['exp_dir']}/result.json", 'w+') as outfile:
                                                json.dump(result, outfile, default=datetimeconverter, indent=4)

                                        except Exception as e:
                                            logger.exception(e)
                                            logger.exception(f"Was not able to create result for {test_config['exp_dir']}")

                                        break
                                break
                    break
            break
main()