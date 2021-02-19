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

import argparse
import copy
import json
import logging.config
import os
import pprint
import sys
import threading

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.Experiment_Handler import Experiment_Handler
from src.Experiment_Handler import NetworkNotStartingError
from BlockchainFormation.utils.utils import *
from DAppFormation.DApp_Handler import DApp_Handler
from BlockchainFormation.Node_Handler import Node_Handler


class ArgParser:

    def __init__(self):
        """Initialize an ArgParser object.
        The general structure of calls from the command line is:
        run.py --config path_to_config

        """

        self.parser = argparse.ArgumentParser(description='This script evaluates Blockchains',
                                              usage='Give path to config with all experiment relevant settings')
        self.parser.add_argument('--config', '-c', help='enter path to config file')
        self.parser.add_argument('--exp_dir', '-e', help='enter path to experiment directory')
        self.parser.add_argument('--freqs', '-f', help='enter frequency', type=int, nargs='+')
        self.parser.add_argument('--shape', '-s', help='enter shape')
        self.parser.add_argument('--duration', '-d', help='enter duration',type=int)
        self.parser.add_argument('--delta_max_time', '-m', help='enter max time',type=int)



    def load_config(self, namespace_dict):
        """
        Loads the config from a given JSON file
        :param namespace_dict: namespace dict containing the config file path
        :return: config dict
        """
        # print(namespace_dict)
        if vars(namespace)["exp_dir"] == None:
            if namespace_dict['config'].endswith('.json'):
                try:
                    with open(namespace_dict['config']) as json_file:
                        return json.load(json_file)
                except:
                    logger.error("ERROR: Problem loading the given config file")
            else:
                logger.exception("Config file needs to be of type JSON")
                raise Exception("Config file needs to be of type JSON")

        else:
            if "exp_dir" in list(namespace_dict.keys()):
                try:
                    with open(f"{namespace_dict['exp_dir']}/config.json") as json_file:
                        config = json.load(json_file)
                        config['number_of_setups'] = 1
                        config['number_of_experiments'] = 1
                    for key in namespace_dict:
                            config["experiment_settings"][key] = namespace_dict[key]
                    return config

                except Exception as e:
                    logger.exception(e)
                    logger.error("ERROR: Problem loading the experiment")


if __name__ == '__main__':

    dir_name = os.path.dirname(os.path.realpath(__file__))

    logging.basicConfig(filename=f'{dir_name}/logger.log', level=logging.DEBUG,
                        format='%(asctime)s - %(threadName)s - %(name)s - %(levelname)s - %(message)s')
    logging.captureWarnings(True)
    # create logger with
    logger = logging.getLogger(__name__)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(threadName)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(ch)



    logger.info("               ___           ___     ___                ")
    logger.info("              |   |   ___   |   |   |   |               ")
    logger.info("              | D |\ |   | /| P |---| S |               ")
    logger.info("              |___| \| L |/ |___|   |___|               ")
    logger.info("                     |___|                              ")
    logger.info("                                                        ")
    logger.info(" ====================================================== ")
    logger.info("            Distributed Ledger Performance Scan         ")
    logger.info(" ====================================================== ")
    logger.info("                                                        ")
    logger.info("                                                        ")
    logger.info("   ____________       _____________       ____________  ")
    logger.info("  /__________ /|     /___________ /|     /__________ /| ")
    logger.info(" |           | |    |            | |    |           | | ")
    logger.info(" |    BMW    |-|----|   Uni.LU   |-|----|  FhG FIT  | | ")
    logger.info(" |           | |    |            | |    |    FIM    | | ")
    logger.info(" |           | |    |            | |    |           | | ")
    logger.info(" |  P. Ross  | /    |            | /    |J. Sedlmeir| / ")
    logger.info(" |___________|/     |____________|/     |___________|/  ")
    logger.info("                                                        ")
    logger.info("                                                        ")
    logger.info(" ====================================================== ")
    logger.info("     Licensed under the Apache License, Version 2.0     ")
    logger.info(" =======================================================")
    logger.info("                                                        ")
    logger.info("                                                        ")
    logger.info("         ____    _____      _      ____    _____        ")
    logger.info("        / ___|  |_   _|    / \    |  _ \  |_   _|       ")
    logger.info("        \___ \    | |     / _ \   | |_) |   | |         ")
    logger.info("         ___) |   | |    / ___ \  |  _ <    | |         ")
    logger.info("        |____/    |_|   /_/   \_\ |_| \_\   |_|         ")
    logger.info("                                                        ")
    logger.info("                                                        ")

    argparser = ArgParser()
    namespace = argparser.parser.parse_args()

    # loading the total experiment config
    config = argparser.load_config(vars(namespace))

    # print(vars(namespace))
    # print(vars(namespace)["exp_dir"])
    # print(vars(namespace)["exp_dir"] is None)
    # print(vars(namespace)["exp_dir"] == None)
    # print(vars(namespace)["exp_dir"] == "None")
    if vars(namespace)["exp_dir"] == None:
        print("Startup mode selected")
        #  os.system(f"truncate -s 0 {dir_name}/logger.log")
        #  os.truncate(path=f"{dir_name}/logger.log", length=10)

        # splitting the config into single experiment configs
        setup_configs = []
        experiment_configs = []

        blockchain_config = config['blockchain_formation_settings']
        client_config = config['client_settings']
        experiment_config = config['experiment_settings']
        number_setups = config['number_of_setups']
        number_experiments = config['number_of_experiments']

        # Loop through all possible setups and start network/clients, run experiments and shutdown network/client again
        for index in range(0, number_setups):
            blockchain_config_run = {}
            if len(blockchain_config['vm_count']) == 1:
                blockchain_config_run['vm_count'] = blockchain_config['vm_count'][0]
            elif len(blockchain_config['vm_count']) == number_setups:
                blockchain_config_run['vm_count'] = blockchain_config['vm_count'][index]
            else:
                raise Exception(f"config[blockchain_formation_settings][vm_count] has invalid length")

            if len(blockchain_config['instance_type']) == 1:
                blockchain_config_run['instance_type'] = blockchain_config['instance_type'][0]
            elif len(blockchain_config['instance_type']) == number_setups:
                blockchain_config_run['instance_type'] = blockchain_config['instance_type'][index]
            else:
                raise Exception(f"config[blockchain_formation_settings][instance_type] has invalid length")

            blockchain_config_run['instance_provision'] = "aws"

            if len(blockchain_config['aws_region']) == 1:
                blockchain_config_run['aws_region'] = blockchain_config['aws_region'][0]
            elif len(blockchain_config['aws_region']) == number_setups:
                blockchain_config_run['aws_region'] = blockchain_config['aws_region'][index]
            else:
                raise Exception(f"config[blockchain_formation_settings][aws_region] has invalid length")

            for key in blockchain_config:
                if key in ["vm_count", "instance_type", "instance_provision", "aws_region"]:
                    pass
                elif key == f"{blockchain_config['blockchain_type']}_settings":
                        help = blockchain_config[f"{blockchain_config['blockchain_type']}_settings"]
                        help_run = {}
                        for l in help:
                            if len(help[l]) == 1:
                                help_run[l] = help[l][0]
                            elif len(help[l]) == number_setups:
                                help_run[l] = help[l][index]
                            else:
                                raise Exception(f"config[blockchain_formation_settings][{blockchain_config['blockchain_type']}_settings][{l}] has invalid length")
                        blockchain_config_run[f"{blockchain_config['blockchain_type']}_settings"] = help_run

                else:
                    blockchain_config_run[key] = blockchain_config[key]

            client_config_run = {}
            for key in client_config:
                if len(client_config[key]) == 1 or type(client_config[key] is dict):
                    client_config_run[key] = client_config[key][0]
                elif len(client_config[key]) == number_setups:
                    client_config_run[key] = client_config[key][index]
                else:
                    raise Exception(f"config[client_settings][{key}] has invalid length")

            setup_configs.append(dict([("blockchain_formation_settings", blockchain_config_run), ("client_settings", client_config_run)]))

        for index in range(0, number_experiments):
            experiment_config_run = {}
            for key in experiment_config:
                if len(experiment_config[key]) == 1:
                    experiment_config_run[key] = experiment_config[key][0]
                elif len(experiment_config[key]) == number_experiments:
                    experiment_config_run[key] = experiment_config[key][index]
                else:
                    raise Exception(f"config[experiment_settings][{key}] has invalid length")

            experiment_configs.append(experiment_config_run)

        for index in range(0, number_setups):

            # os.system("rm logger.log")
            # os.system("touch logger.log")
            try:

                blockchain_config_help = setup_configs[index]['blockchain_formation_settings']

                # Create Client VMs if needed with the same subnet/security/proxy settings as blockchain network
                # if blockchain_config_help['instance_provision'] == "aws":

                client_config_help = copy.deepcopy(blockchain_config_help)

                # TODO Doo we need client_config and client_formation config? Only one should be enough right?
                # Delete blockchain specific settings from conf
                client_config_help.pop(f"{blockchain_config_help['blockchain_type']}_settings", None)

                # TODO Implement option to host client nodes in a different subnet. Needed since the private VPC subnets are rather small (<60 IPs available)

                client_config_help["vm_count"] = setup_configs[index]['client_settings']["number_of_clients"]
                client_config_help["instance_type"] = setup_configs[index]['client_settings']["client_type"]
                client_config_help["instance_provision"] = setup_configs[index]['client_settings']['instance_provision']
                client_config_help['aws_region'] = setup_configs[index]['client_settings']["aws_region"]

                client_config_help["user"] = blockchain_config["user"]
                client_config_help["priv_key_path"] = blockchain_config["priv_key_path"]

                # elif blockchain_config['instance_provision'] == "own":
                    # client_config = dapp_config['client_settings']

                if blockchain_config_help["blockchain_type"] == "indy":
                    client_config_help["blockchain_type"] = "indy_client"
                elif blockchain_config_help["blockchain_type"] == "acapy":
                    blockchain_config_help["blockchain_type"] = "indy"
                    client_config_help["blockchain_type"] = "acapy"
                else:
                    client_config_help["blockchain_type"] = "client"

                client_config_help["tag_name"] = setup_configs[index]['client_settings']["tag_name"]
                client_config_help['exp_dir'] = setup_configs[index]['client_settings']["exp_dir"]

                # Set this to None temporarily to allow threading
                client_config_help["client_settings"] = {
                    # "target_network_conf": self.vm_handler_blockchain.get_config_path(),
                    "target_network_conf": None
                }

                if blockchain_config_help["blockchain_type"] == "fabric" and blockchain_config_help["fabric_settings"]["prometheus"] == True:
                    logger.info("Fabric selected - adding additional config")
                    additional_config_help = copy.deepcopy(blockchain_config_help)
                    # Insert prometheus_settings in fabric_config
                    additional_config_help.pop(f"{blockchain_config_help['blockchain_type']}_settings", None)
                    additional_config_help["vm_count"] = 1
                    additional_config_help["aws_region"] = {"eu-central-1": 1}
                    additional_config_help["instance_type"] = "m5.large"
                    additional_config_help["blockchain_type"] = "prometheus"
                    additional_config_help["user"] = blockchain_config_help["user"]
                    additional_config_help["priv_key_path"] = blockchain_config_help["priv_key_path"]
                    additional_config_help["prometheus_settings"] = {}
                    additional_config_help["tag_name"] = "blclab_prometheus"
                    additional_config_help["additional_settings"] = {
                        "target_network_conf": None
                    }
                else:
                    additional_config_help = None

                """
                logger.info("Blockchain config: ")
                pprint.pprint(blockchain_config_help)
                logger.info("  ")
                logger.info("  ")
                logger.info("Client config: ")
                pprint.pprint(client_config_help)
                logger.info("  ")
                logger.info("  ")
                logger.debug("Additional config: ")
                pprint.pprint(additional_config_help)
                """

                # Creating a new Experiment Handler
                if blockchain_config_help["blockchain_type"] == "fabric" and blockchain_config_help["fabric_settings"]["prometheus"] == True:
                    # experiment_handler = Experiment_Handler(logger, DApp_Handler(Node_Handler(blockchain_config_help), Node_Handler(client_config_help), logger, Node_Handler(additional_config_help)), config, [experiment_configs[index]])
                    experiment_handler = Experiment_Handler(logger, DApp_Handler(Node_Handler(blockchain_config_help), Node_Handler(client_config_help), logger, Node_Handler(additional_config_help)), config, experiment_configs)
                else:
                    # experiment_handler = Experiment_Handler(logger, DApp_Handler(Node_Handler(blockchain_config_help), Node_Handler(client_config_help), logger), config, [experiment_configs[index]])
                    experiment_handler = Experiment_Handler(logger, DApp_Handler(Node_Handler(blockchain_config_help), Node_Handler(client_config_help), logger), config, experiment_configs)

                logger.info("                                                          ")
                logger.info("==========================================================")
                logger.info("==========Starting Blockchain and Client Network==========")
                logger.info("==========================================================")
                logger.info("                                                          ")

                try:

                    experiment_handler.start_dapp()

                    experiment_handler.run_experiment()



                # catching ctrl-c and killing network if desired
                except KeyboardInterrupt:
                    logger.info("CTRL-C detected. Exiting gracefully by terminating network if desired.")
                    if yes_or_no("Do you want to shut down the whole network? If yes, the next experiment will be carried out."):
                        pass
                    else:
                        raise KeyboardInterrupt

                except Exception as e:
                    logger.exception(e)
                    pass

                logger.info("                                                        ")
                logger.info("========================================================")
                logger.info("======= Terminating Blockchain and Client Network ======")
                logger.info("=======                                           ======")
                logger.info("=======          Evaluation Experiment            ======")
                logger.info("========================================================")
                logger.info("                                                        ")

                network_termination_thread = threading.Thread(target=experiment_handler.terminate_network, name="DApp-Termination")
                experiment_evaluation_thread = threading.Thread(target=experiment_handler.evaluate_experiment, name="Experiment-Evaluation")

                network_termination_thread.start()
                experiment_evaluation_thread.start()
                network_termination_thread.join()
                experiment_evaluation_thread.join()

            except Exception as e:
                logger.exception(e)
                logger.info(f"Setup {index} failed.")


    else:
        print("\n\n\n")
        print(config)
        print("\n\n\n")
        print([config["experiment_settings"]])
        experiment_handler = Experiment_Handler(logger, DApp_Handler(Node_Handler(config["blockchain_formation_settings"]), Node_Handler(config["client_settings"]), logger), config, [config["experiment_settings"]])
        try:
            experiment_handler.run_experiment()
        except Exception as e:
            logger.exception(e)



    logger.info("                                                        ")
    logger.info("                                                        ")
    logger.info("                 _____   _   _   ____                   ")
    logger.info("                | ____| | \ | | |  _ \                  ")
    logger.info("                |  _|   |  \| | | | | |                 ")
    logger.info("                | |___  | |\  | | |_| |                 ")
    logger.info("                |_____| |_| \_| |____/                  ")
    logger.info("                                                        ")
    logger.info("                                                        ")
    logger.info("                                                        ")
