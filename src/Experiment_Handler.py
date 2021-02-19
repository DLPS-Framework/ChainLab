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

import copy
import threading

import time
import datetime

import os
import json

from DAppFormation import DApp_Handler
from BlockchainFormation import Node_Handler

import pytz

from src.benchmarking.utils import *
from src.benchmarking.benchmarking import benchmarking
from src.benchmarking.crashmarking import crashmarking
from BlockchainFormation.utils.utils import datetimeconverter

utc = pytz.utc


class NetworkNotStartingError(Exception):
    """Base class for exceptions in this module."""
    pass


class Experiment_Handler:
    """
    Class handling the creation of the blockchain network, execution of benchmarks and termination of the blockchain network.
    Also starts the evaluation process.
    """

    def __init__(self, logger, dapp_handler, config, experiment_configs):

        self.logger = logger

        # Overall settings
        self.dapp_handler = dapp_handler

        self.config = config

        # Settings for experiments
        self.experiment_configs = experiment_configs

        self.blockchain_formation_config = dapp_handler.blockchain_handler.config
        self.client_config = dapp_handler.client_handler.config

    def start_dapp(self):
        """
        Sets up the blockchain network
        :return:
        """

        try:
            self.dapp_handler.start_dapp_network()

        except Exception as e:
            self.logger.exception(e)
            raise NetworkNotStartingError()


    def run_experiment(self):
        """
        Runs the benchmarks on the previous set up blockchain
        :return:
        """
        try:
            self.logger.info("                                                          ")
            self.logger.info("==========================================================")
            self.logger.info("================= Running the Experiment =================")
            self.logger.info("==========================================================")
            self.logger.info("                                                          ")

            ts = time.time()
            st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d_%H-%M-%S')

            exp_dir = f"/experiments/exp_{st}_{self.blockchain_formation_config['blockchain_type']}"

            for index in range(0, len(self.experiment_configs)):

                if index != 0:
                    # self.logger.info("Conducting a clean restart to be unbiased also in the second run")
                    # if self.dapp_handler.blockchain_handler.config["blockchain_type"] == "fabric":
                        # self.dapp_handler.restart_blockchain(self.experiment_configs[index]["number_of_endorsers"])
                    # else:
                        # self.dapp_handler.restart_blockchain()

                    time.sleep(5)

                try:
                    # print(exp_dir)
                    # print(self.config['experiment_settings']['exp_dir'])


                    try:
                        os.makedirs(self.config['experiment_settings']['exp_dir'][0] + exp_dir)
                        self.experiment_configs[index]['exp_dir'] = self.config['experiment_settings']['exp_dir'][0] + exp_dir
                        self.logger.info(f"Created {str(self.experiment_configs[index]['exp_dir'])} directory")

                    except Exception as e:
                        self.logger.exception(e)
                        print("\n\n\n")
                        print(self.experiment_configs)
                        print(exp_dir)
                        dirs = self.experiment_configs[index]['exp_dir'].split("/")
                        print(dirs)
                        dirs[-1] = exp_dir.split("/")[-1]
                        dirs = dirs[0:-1]
                        print(dirs)
                        print("/".join(dirs))
                        self.experiment_configs[index]['exp_dir'] = "/".join(dirs)

                    # except OSError:
                        # self.logger.error("Creation of the directories failed")

                    with open(f"{self.experiment_configs[index]['exp_dir']}/config.json", 'w+') as outfile:
                        json.dump(self.config, outfile, default=datetimeconverter, indent=4)

                    print(self.experiment_configs[index])
                    self.run_benchmarking(self.experiment_configs[index])

                except AbortSetupException:
                    raise AbortSetupException()
                except Exception as e:
                    self.logger.exception(e)

        except AbortSetupException:
            raise AbortSetupException("Blockchain not responding anymore - exiting")

        except Exception as e:
            self.logger.info("Problems occurred when running the experiment")
            self.logger.exception(e)
            raise Exception("Experiment had to be aborted")


    def terminate_network(self):
        """
        Terminates the blockchain
        :return:
        """

        self.dapp_handler.terminate_dapp_network()

    def run_benchmarking(self, experiment_config):
        """
        TODO
        :param blockchain_config:
        :param client_config:
        :param experiment_config:
        :param logger:
        :return:
        """

        blockchain_config = self.blockchain_formation_config
        client_config = self.client_config
        logger = self.logger

        if (experiment_config['base'] == "None" and experiment_config['step'] == "None"):
            if experiment_config['mode'] == "public":
                if (experiment_config['method'] in ["writeData", "invokeDoNothing", "readData", "readMuchData", "writeMuchData, writeMuchData2"]):
                    experiment_config['bases'] = [0]
                    experiment_config['steps'] = [100]
                elif (experiment_config['method'] in ["invokeMatrixMultiplication", "setMatrixMultiplication"]):
                    experiment_config['bases'] = [0]
                    experiment_config['steps'] = [100]

            elif (experiment_config['mode'] == "private"):
                if (experiment_config['method'] in ["writeData", "invokeDoNothing", "readData", "readMuchData", "writeMuchData", "writeMuchData2"]):
                    experiment_config['bases'] = [0]
                    experiment_config['steps'] = [10]
                elif (experiment_config['method'] in ["invokeMatrixMultiplication", "setMatrixMultiplication"]):
                    experiment_config['bases'] = [0]
                    experiment_config['steps'] = [10]

                else:
                    raise Exception("Invalid mode")
        else:
            experiment_config['bases'] = []
            experiment_config['bases'].append(experiment_config['base'])
            experiment_config['steps'] = []
            experiment_config['steps'].append(experiment_config['step'])

        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d_%H-%M-%S')

        experiment_config['exp_dir'] = f"{experiment_config['exp_dir']}/{experiment_config['method']}_{st}"

        try:
            os.makedirs(f"{experiment_config['exp_dir']}")
            logger.info(f"Created {experiment_config['exp_dir']} directory")

        except OSError:
            pass
            # logger.error("Creation of the directories failed")

        try:
            # logging into exp_dir
            fileh = logging.FileHandler(f"{experiment_config['exp_dir']}/logger.log", 'a')
            formatter = logging.Formatter('%(asctime)s - %(threadName)s - %(name)s - %(levelname)s - %(message)s')
            fileh.setFormatter(formatter)

            logger.addHandler(fileh)

        except Exception as e:
            logger.exception(e)

        logger.info("                                 ")
        logger.info("=================================")
        logger.info("   Performing the benchmarking   ")
        logger.info("=================================")
        logger.info("                                 ")
        logger.info("")

        try:
            if 'test' not in experiment_config.keys():
                res = benchmarking(self, experiment_config)
            elif experiment_config['test'] == 'benchmarking':
                res = benchmarking(self, experiment_config)
            elif experiment_config['test'] == 'crashmarking':
                res = crashmarking(self, experiment_config)
            else:
                logger.info("Invalid test type")
                raise Exception("Invalid test type")

            logger.debug(f"result from benchmarking: {res}")

            result = dict()
            result['blockchain_config'] = blockchain_config
            result['client_config'] = client_config
            result['experiment_config'] = experiment_config
            result['result'] = res

        except BlockchainNotRespondingError:
            raise AbortSetupException("Blockchain not responding")
        except RetryLimitExceededException:
            raise AbortSetupException("Retries exceeded")
        except Exception as e:
            logger.exception(e)
            try:
                logger.info("Repeat benchmarking once")
                res = benchmarking(self, experiment_config)

                result = dict()
                result['blockchain_config'] = blockchain_config
                result['client_config'] = client_config
                result['experiment_config'] = experiment_config
                result['result'] = res

            except BlockchainNotRespondingError:
                raise AbortSetupException
            except Exception as e:
                logger.exception(e)
                raise AbortSetupException("Benchmarking failed at second attempt as well - skipping this config")

        with open(f"{experiment_config['exp_dir']}/result.json", 'w+') as outfile:
            json.dump(result, outfile, default=datetimeconverter, indent=4)

        logger.info("                                           ")
        logger.info("===========================================")
        logger.info("     Benchmarking experiment completed     ")
        logger.info("===========================================")
        logger.info("                                           ")

        try:
            logger.removeHandler(fileh)
        except Exception as e:
            logger.exception(e)


    def evaluate_experiment(self):
        """
        Evaluates the measurements and creates plots etc.
        :return:
        """
        try:
            self.logger.info("                                         ")
            self.logger.info("=========================================")
            self.logger.info("==========Evaluating Experiment==========")
            self.logger.info("=========================================")
            self.logger.info("                                         ")
            # TODO open result.json and make (statistical) evaluation
            # TODO Add final_evaluation and plotter here
        except Exception as e:
            self.logger.info("Problems occurred when evaluating the experiment")
            self.logger.info(str(e))


class Evaluation_Handler:

    def __init__(self, blockchain_formation_config, client_config, logger):

        self.blockchain_formation_config = blockchain_formation_config
        self.client_config = client_config
        self.logger = logger