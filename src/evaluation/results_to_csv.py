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
from os import path
import pandas as pd

def main():
    """
    TODO
    :return:
    """

    dir_name = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    print("Loading filer config")
    try:
        json_file = open(f"{dir_name}/example_configs/evaluation/presentation.json")
        filter = json.load(json_file)
    except Exception as e:
        print(e)

    # collects all the experimental results which satisfy the conditions in the filter presentation.json
    configs = []
    results = []
    count = 0

    for rootdir in filter["directories"]:
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
                else:
                    print(f"    Examining {dir1}")

                # look whether the experiment directory has the expected shape
                for subdir2, dirs2, files2 in os.walk(os.path.join(rootdir, dir1)):
                    # print(f"        Loading {os.path.join(os.path.join(rootdir, dir1),'config.json')}")
                    if len(files2) >= 1 and files2[0] == "config.json":
                        print(f"        Reading {os.path.join(os.path.join(rootdir, dir1), 'config.json')}...")
                        try:
                            json_file = open(os.path.join(os.path.join(rootdir, dir1), "config.json"))
                            config = json.load(json_file)
                            # print(config)
                            # print("        Successfully loaded config.json")
                        except Exception as e:
                            print(e)
                            print(f"        Could not open {os.path.join(os.path.join(rootdir, dir1),'config.json')}")
                            continue

                        print("        Checking blockchain_type")
                        try:
                            blockchain_type = config['setup_config']['blockchain_formation_settings']['blockchain_type']

                        except Exception as e:
                            print(e)
                            print(f"        Could not determine blockchain_type")
                            continue

                        print("        Reading and checking blockchain_formation_settings")
                        blockchain_types = ["fabric_settings", "geth_settings", "parity_settings", "quorum_settings", "parity_settings", "sawtooth_settings", "indy_settings", "corda_settings"]
                        boo = True

                        try:
                            for key in filter["blockchain_formation_settings"]:
                                if (key in blockchain_types and key == f"{blockchain_type}_settings"):
                                    print(f"        Checking whether the {key} satisfy the filter requirements")
                                    boo = boo & check_filter(filter["blockchain_formation_settings"][f"{blockchain_type}_settings"], config['setup_config']['blockchain_formation_settings'][f'{blockchain_type}_settings'], "list")
                                elif (key in blockchain_types):
                                    pass

                                else:
                                    boo = boo & check_value(filter["blockchain_formation_settings"], config["setup_config"]['blockchain_formation_settings'], key, "list")
                        except Exception as e:
                            print(f"        Problem with some keys")
                            print(e)

                            boo = False

                        if boo == False:
                            print("        Some key in blockchain_formation_settings did not match - stepping to next exp_dir")
                            continue
                        else:
                            print(f"        All requirements in blockchain_formation_settings met")

                        boo = check_filter(filter['client_settings'], config['setup_config']['client_settings'], "list")

                        if boo == False:
                            print("Some key in client_settings did not match - next exp_dir")
                            continue
                        else:
                            print("        All requirements in client_settings met")

                        boo = check_filter(filter['experiment_settings'], config['experiment_config'], "list")

                        if boo == False:
                            print("Some key in experiment_settings did not match - next exp_dir")
                            continue
                        else:
                            print("        All requirements in experiment_settings met")

                        print(" ==========================================================")
                        print("        The folder probably contains suitable experiments")
                        # walk through every contained folder
                        for dir2 in dirs2:
                            try:
                                print(f"        Loading {os.path.join(subdir2,os.path.join(dir2, 'config.json'))}")
                                json_file = open(os.path.join(subdir2, os.path.join(dir2, 'config.json')))
                                config1 = json.load(json_file)

                            except Exception as e:
                                print(e)
                                raise Exception(f"Could not open {os.path.join(subdir2,os.path.join(dir2, 'config.json'))}")

                            #checking whether the configs match

                            boo = check_filter(filter["experiment_settings"], config1["experiment_settings"], "element")
                            if boo == False:
                                print(f"        The experiment in {dir2} does not meet the filter requirements")
                                break
                            else:
                                print("        The experiment meets the requirements of the fiter")

                            print("        Checking whether there are sufficiently many subfolders")
                            for subdir3, dirs3, files3 in os.walk(os.path.join(subdir2, dir2)):
                                try:
                                    if (len(dirs3) < config1["experiment_settings"]["localization_runs"]):
                                        print(f"The experiment in {dir2} has not been completed and is therefore omitted (too few repetitions)")
                                        continue
                                except:
                                    print("        There seems to be no flag localization runs - old experiment")
                                    continue

                                for dir3 in dirs3:
                                    # checking whether there is a result of the benchmarking run
                                    if path.exists(os.path.join(os.path.join(subdir3, dir3), "result.json")) == False:
                                        continue

                                    # checkin whether it is a repetition run
                                    try:
                                        if (int(dir3[-1].split("_")[-1]) <= config1["experiment_settings"]["localization_runs"]):
                                            print(f"        The experiment in {subdir3}/{dir3} is not a repetition run")
                                            continue
                                    except:
                                        print("        There seems to be no flag localizations runs - old experiment")

                                    number_of_runs = 0
                                    # checking whether the subfolder contains enough benchmarking runs
                                    for subdir4, dirs4, files4 in os.walk(os.path.join(subdir3, dir3 + "/evaluation")):
                                        number_of_runs = len(files4)
                                        # end after first iteration of os.walk4
                                        break

                                    if number_of_runs < 3:
                                        print(f"        The experiment in {subdir3}/{dir3} does not contain sufficiently many rampings")
                                        continue

                                    print("        Reading result.json")

                                    try:
                                        json_file = open(os.path.join(os.path.join(subdir3, dir3), "result.json"))
                                        result = json.load(json_file)
                                        print(f"        {result}")

                                    except:
                                        print(f"        Could not open {os.path.join(subdir3, 'result.json')}")

                                    try:# check whether the result is non-empty
                                        if result["throughput_receive"] == []:
                                            print("        No throughput found")
                                            continue
                                    except Exception as e:
                                        print(e)

                                    print(f"Adding {os.path.join(subdir3, 'result.json')}")
                                    configs.append(config1)
                                    results.append(result)

                                # end after first iteration of os.walk3
                                break

                    elif len(files2) == 0:
                        print("            Omitting directory because there is no file")
                    else:
                        print("            Check name of the file there - config.json expected!")
                    # stop after first level of os.walk2
                    break
            # stop after first level of os.walk1
            break

    # print(f"number of configs: {len(configs)}")
    # print(f"number of results: {len(results)}")

    header = []
    data = {}

    if len(configs) != len(results):
        raise Exception("number of configs and number of results are different - why???")

    if len(configs) == 0:
        raise Exception("no experiments found")

    header.append("exp_dir")
    data["exp_dir"] = []
    for i in range(0, len(configs)):
        data["exp_dir"].append(configs[i]["experiment_settings"]["exp_dir"])

    for key in ["vm_count", "instance_type", "blockchain_type"]:
        header.append("blockchain_" + key)
        data["blockchain_" + key] = []
        for i in range(0, len(configs)):
            data["blockchain_" + key].append(configs[i]["blockchain_formation_settings"][key])

    blockchain_types = filter["blockchain_formation_settings"]["blockchain_type"]
    for blockchain_type in blockchain_types:
        for key in filter["blockchain_formation_settings"][f"{blockchain_type}_settings"]:
            header.append(f"{blockchain_type}_{key}")
            data[f"{blockchain_type}_{key}"] = []

            for i in range(0, len(configs)):
                if blockchain_type == configs[i]["blockchain_formation_settings"]["blockchain_type"]:
                    data[f"{blockchain_type}_{key}"].append(configs[i]["blockchain_formation_settings"][f"{blockchain_type}_settings"][key])
                else:
                    data[f"{blockchain_type}_{key}"].append("")


    for key in ["vm_count", "instance_type"]:
        header.append("client_" + key)
        data["client_" + key] = []
        for i in range(0, len(configs)):
            data["client_" + key].append(configs[i]["client_settings"][key])

    for key in filter["experiment_settings"]:
        header.append(key)
        data[key] = []
        for i in range(0, len(configs)):
            try:
                data[key].append(configs[i]["experiment_settings"][key])
            except:
                data[key].append("")

    # counts = []
    # look for the longest row of measurements
    # for i in range(0, len(configs)):
    #     counts.append(len(results[i]["result"]["throughputs_receive"]))

    # count = max(counts)
    # print(f"longest measurement had {count} repetitions")

    units = ["tx/s",                 "ms",          "%",            "%",            "%",            "%",                        "%",                "ms",               "ms",           "kB/s",                     "kB/s",                 "%",                            "kB/s",             "kB/s",             "%",                   "%",                "%CPU x core x s",                      "kB",                     "kB/s",                    "%CPU x core",             "kB/s",              "",                    "s",          "%CPU x core x s",                "kB",                      "%",                "kB/s",                 "kB/s",               "kB/s",                  "kB/s",                    "kB/s",                      "%",                       "kB/s",             "kB/s",                           "%",                    "kB/s",                        "kB/s"]
    keys = ["throughput_receive", "latency", "effectivity", "blockchain_cpus", "client_cpus", "blockchain_single_cpus", "client_single_cpus", "blockchain_pings", "client_pings", "blockchain_incomings", "blockchain_outgoings", "blockchain_disk_utilizations", "client_incomings", "client_outgoings", "client_disk_utilizations", "disk_utilizations", "blockchain_energy_consumption", "blockchain_storage_consumption", "blockchain_traffic", "client_energy_consumption", "client_traffic", "number_of_transactions", "total_duration", "energy_per_transaction", "storage_per_transaction", 'peer_single_cpus_max', 'peer_incomings_max', 'peer_outgoings_max', 'orderer_single_cpus_max', 'orderer_incomings_max', 'orderer_outgoings_max', 'peer_single_cpus_submax', 'peer_incomings_submax', 'peer_outgoings_submax', 'orderer_single_cpus_submax', 'orderer_incomings_submax', 'orderer_outgoings_submax']

    if len(units) != len(keys):
        raise Exception("units and keys do not have the same length")

    for k in range(0, len(keys)):
        key = keys[k]
        unit = units[k]
        data[key + f"_({unit})"] = []
        header.append(key + f"_({unit})")
        for i in range(0, len(configs)):
            try:
                data[key + f"_({unit})"].append(results[i][key])
            except:
                data[key + f"_({unit})"].append("")


    df = pd.DataFrame(data, columns=header)

    df.to_csv(path_or_buf=f"{dir_name}/{filter['target_directory']}/evaluation.csv", sep=";", decimal=".")



def check_filter(filter_range, config_range, type):

    boo = True
    for key in filter_range:
        boo = boo & check_value(filter_range, config_range, key, type)

    return boo


def check_value(filter_range, config_range, key, type):

    if filter_range[key] == []:
        # print(f"        Omitting filter for key {key} because no requirements are specified")
        return True
    else:
        for value in filter_range[key]:
            if type == "list":
                if value in config_range[key]:
                    # print(f"        Found filter value <<{value}>> for key {key} in config: {config_range[key]}")
                    return True
            elif type == "element":
                if value == config_range[key]:
                    # print(f"        Found filter value <<{value} for key {key} in config: {config_range[key]}")
                    return True

        return False

"""

    for subdir in os.walk(subdir):
        count = 0
        for file in os.walk(subdir):
            if (file.name == "config.json"):
                print("found a config")
                count = count + 1
            else:
                print("Unexpected file found")
                count = count + 1

        if count != 1:
            if count == 0:
                print(f"found no config in {subdir} in {dir}")
            else:
                print(f"found too many configs in {subdir} in {dir}")

        # filter the config
        with open(file) as json_file:
            config = json.load(json_file)

        for k in filter:
            if (filter[k] == config[k]):
                configs.append(config)

# check the number of configs with this specification
print(f"number of configs remaining: {len(configs)}")
# now, print the keys regarding which the resulting configs differ
remaining_keys = []
for k in configs[0]:
    boo = False
    for index in range(1, len(configs)):
        if (configs[0][k] != configs[index][k]):
            boo = True
            remaining_keys[k] = []

# add keys which are equal everywhere to filter
# add other keys to remaining_keys

print(f"Remaining degrees of freedom: {remaining_keys}")

x_values = "node_count"
y_values1 = "frequency_receive"
y_values2 = "latency"

charts = []
labels = []

name = []
for k in remaining_keys:
    name.append(f"{config[k]}")

charts.append()
labels.append("_".join(name))

for config in configs:
    for k in remaining_keys:


"""


main()
