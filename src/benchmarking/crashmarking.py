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

import datetime
import json
import gc
import os
import time
import random
import numpy as np
import pytz
from BlockchainFormation.utils.utils import *
from src.Experiment_Handler import *
from src.benchmarking.utils import *
from DAppFormation import DApp_Handler
from BlockchainFormation import Node_Handler
import logging

utc = pytz.utc

import matplotlib
import matplotlib.pyplot as plt
from BlockchainFormation.Node_Handler import Node_Handler
from scipy import stats

from src.utils.csv_handling import *

from paramiko import SSHException

from src.benchmarking import *


def crashmarking(experiment_handler, experiment_config):
    """
    TODO
    :param blockchain_config:
    :param client_config:
    :param experiment_config:
    :param logger:
    :param blockchain_ssh_clients:
    :param blockchain_scp_clients:
    :param client_ssh_clients:
    :param client_scp_clients:
    :return:
    """

    blockchain_config = experiment_handler.blockchain_formation_config
    client_config = experiment_handler.client_config
    logger = experiment_handler.logger

    keys = get_keys(blockchain_config)

    result = {key: [] for key in keys}

    res_result_mapping = get_res_result_mapping()

    set_delays(experiment_handler, experiment_config)

    for r in range(1, experiment_config['repetition_runs'] + 1):
        logger.info(f"New repetition: r = {r}")

        test_config = {}
        test_config['exp_dir'] = f"{experiment_config['exp_dir']}/{experiment_config['method']}_{experiment_config['mode']}_{experiment_config['shape']}_{r}"
        test_config['frequency'] = experiment_handler['frequency']
        logger.info(f"Performing {experiment_config['method']}_{experiment_config['mode']}_{experiment_config['shape']}_{r} experiment (crashtest)")
        try:
            os.makedirs(f"{test_config['exp_dir']}/logs")
            os.mkdir(f"{test_config['exp_dir']}/data")
            os.mkdir(f"{test_config['exp_dir']}/evaluation")

        except Exception as e:
            logger.exception(e)

        total_config = dict()
        total_config['blockchain_formation_settings'] = blockchain_config
        total_config['client_settings'] = client_config
        total_config['experiment_settings'] = experiment_config

        with open(f"{experiment_config['exp_dir']}/config.json", 'w+') as outfile:
            json.dump(total_config, outfile, default=datetimeconverter, indent=4)

        logger.info(f"Starting new crashtest with frequency {experiment_handler['frequency']}")

        try:
            res, ramp = crash_test(experiment_handler, experiment_config, test_config)
        except Exception as e:
            logger.exception(e)
            logger.info("This run failed - repeating once")
            try:
                res, ramp = crash_test(experiment_handler, experiment_config, test_config)
            except Exception as e:
                raise Exception("Second time something does not work - abort")
        try:
            for key in keys:
                result[key].append(res[res_result_mapping[key]])

        except Exception as e:
            raise Exception("Something went wrong with the result")

        gc.collect()
        logger.debug(f"GC stats:{gc.get_stats()}")

    return result


def crash_test(experiment_handler, experiment_config, test_config):
    """
    TODO
    :param blockchain_config:
    :param client_config:
    :param experiment_config:
    :param test_config:
    :param logger:
    :param blockchain_ssh_clients:
    :param blockchain_scp_clients:
    :param client_ssh_clients:
    :param client_scp_clients:
    :return:
    """

    blockchain_config = experiment_handler.blockchain_formation_config
    client_config = experiment_handler.client_config
    logger = experiment_handler.logger

    experiment_handler.dapp_handler.create_ssh_scp_clients()

    result = result_init(blockchain_config)

    # a counter for the i'th iteration - implying repetitions
    retries = 0
    restarts = 0

    while retries < test_config['repetitions']:

        # the total frequency
        frequency = test_config['frequency']

        # the frequency per client
        freq = (test_config['frequency']) / len(client_config['priv_ips'])

        # the frequency for naming the logs
        test_config['freq'] = f"{round(freq, 1)}"

        max_time = experiment_config['duration'] + experiment_config['delta_max_time']

        logger.info("")
        logger.info(f"New benchmarking run started @ frequency {test_config['freq']} and max_time {max_time}")

        # waiting such that all i/o from the last run is over
        time.sleep(7)

        try:
            start_resources_measurements_blockchain(experiment_handler, experiment_config, test_config)
            start_resources_measurements_clients(experiment_handler, experiment_config, test_config)

            # waiting in order to get CPU and ping also some time in advance of the test
            time.sleep(7)

            if not start_benchmarking_measurements(experiment_handler, experiment_config, test_config, max_time, frequency):
                retries = retries + 1
                ramp = ramp - 1
                logger.info("Timeout - trying again with the same specification")
                time.sleep(7)
                continue

            time.sleep(7)
            get_benchmarking_data(experiment_handler, experiment_config, test_config)

            exception_indicator = False

            res, r_value = evaluate_benchmarking_test(experiment_handler, experiment_config, test_config, False, True)

        except SSHException:

            experiment_handler.dapp_handler.refresh_ssh_scp_clients

            exception_indicator = True

        except BlockchainNotRespondingError as e:

            logger.exception(e)

            restart_blockchain(experiment_handler, experiment_config)

            restarts = restarts + 1

            exception_indicator = True

        except Exception as e:
            logger.exception(e)
            exception_indicator = True

    experiment_handler.dapp_handler.close_ssh_scp_clients
