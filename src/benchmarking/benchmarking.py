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
from DAppFormation import DApp_Handler
from BlockchainFormation import Node_Handler
import logging

utc = pytz.utc

import matplotlib
import matplotlib.pyplot as plt
from BlockchainFormation.Node_Handler import Node_Handler
from scipy import stats

from src.utils.csv_handling import *

from src.benchmarking.utils import *

from paramiko import SSHException


def benchmarking(experiment_handler, experiment_config):
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

    for r in range(1, experiment_config['localization_runs'] + experiment_config["repetition_runs"] + 1):
        logger.info(f"New outer benchmarking loop: r = {r}")
        test_config = {}
        test_config['exp_dir'] = f"{experiment_config['exp_dir']}/{experiment_config['method']}_{experiment_config['mode']}_{experiment_config['shape']}_{r}"
        logger.info(f"Performing {experiment_config['method']}_{experiment_config['mode']}_{experiment_config['shape']}_{r} experiment")
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

        limit = 2
        ramp_bound = experiment_config["ramp_bound"]

        if r < experiment_config["localization_runs"] + 1:
            k = 0
            while k < limit:
                k = k + 1
                try:
                    # time.sleep(10)
                    try:
                        test_config['freqs'] = experiment_config['freqs']
                        test_config['rep'] = "_0"
                    except:
                        test_config['base'] = experiment_config['bases'][-1]
                        test_config['step'] = experiment_config['steps'][-1]
                        test_config['rep'] = ""

                    try:
                        logger.info(f"Starting new series with frequencies {test_config['freqs']}")
                    except:
                        logger.info(f"Starting new localization run with base {round(test_config['base'])} and increment {round(test_config['step'])}")

                    try:
                        res, ramp = benchmarking_test(experiment_handler, experiment_config, test_config)
                    except Exception as e:
                        logger.exception(e)
                        logger.info("Trying once again with the same specification")
                        res, ramp = benchmarking_test(experiment_handler, experiment_config, test_config)

                    if (ramp > ramp_bound) or (ramp > ramp_bound - 1 and k == limit) or ("freqs" in experiment_config and len(experiment_config['freqs']) <= ramp_bound):
                        logger.info(f"Prepraring bases and steps for the next run at {round(experiment_config['success_base_rate'] * 100)}% with {round(experiment_config['success_step_rate'] * 100)}% steps")
                        experiment_config['bases'].append(res['throughput_receive'] * experiment_config["success_base_rate"])
                        experiment_config['steps'].append(res['throughput_receive'] * experiment_config["success_step_rate"])

                        for key in keys:
                            result[key].append(res[res_result_mapping[key]])

                        break

                        logger.info("Not enough measurements!")
                        if k == limit:
                            logger.info(f"Preparing bases and steps for the next run at {round(experiment_config['failure_base_rate'] * 100)}% with {round(experiment_config['failure_step_rate'] * 100)}% steps")
                            experiment_config['bases'].append(float(experiment_config['bases'][-1]) * experiment_config["failure_base_rate"])
                            experiment_config['steps'].append(max(1.0, float(experiment_config['bases'][-1]) * experiment_config["failure_step_rate"]))
                            break
                        continue

                except BlockchainNotRespondingError:
                    raise BlockchainNotRespondingError

                except Exception as e:
                    logger.exception(e)
                    logger.info(f"Benchmarking run with method {experiment_config['method']}, arg {experiment_config['arg']}, mode {experiment_config['mode']}, duration {experiment_config['duration']} failed at repetition {r}")

                    if k == limit:
                        logger.info(f"Preparing bases and steps for the next run at {round(experiment_config['failure_base_rate'] * 100)}% with {round(experiment_config['failure_step_rate'] * 100)}% steps")
                        experiment_config['bases'].append(float(experiment_config['bases'][-1]) * experiment_config["failure_base_rate"])
                        experiment_config['steps'].append(max(1.0, float(experiment_config['steps'][-1]) * experiment_config["failure_step_rate"]))
                        break

                    try:
                        logger.debug(f"res: {res}")
                        logger.debug(f"result: {result}")
                    except Exception as e:
                        logger.exception(e)

                    continue

        else:
            k = 0
            while k < limit:
                k = k + 1
                try:
                    # time.sleep(10)
                    test_config['base'] = experiment_config['bases'][-1]
                    test_config['step'] = experiment_config['steps'][-1]

                    logger.debug("")
                    logger.debug(f"Starting new repetition run with base {round(experiment_config['bases'][-1])} and increment {round(experiment_config['steps'][-1], 1)}")
                    try:
                        res, ramp = benchmarking_test(experiment_handler, experiment_config, test_config)
                    except:
                        logger.info("Trying once again with the same specification")
                        res, ramp = benchmarking_test(experiment_handler, experiment_config, test_config)

                    if (ramp > ramp_bound - 1):

                        for key in keys:
                            result[key].append(res[res_result_mapping[key]])
                        logger.debug(f"Final throughput of the measurement: {round(res['throughput_receive'])}")
                        break
                    else:
                        logger.info("Not enough measurements!")
                        continue

                except BlockchainNotRespondingError:
                    raise BlockchainNotRespondingError

                except Exception as e:
                    logger.exception(e)
                    logger.info(f"Benchmarking run with method {experiment_config['method']}, arg {experiment_config['arg']}, mode {experiment_config['mode']}, duration {experiment_config['duration']} failed at repetition {r}")
                    logger.info("Failed measurement - repeating")

                if k == limit:
                    raise RetryLimitExceededException(f"Abort after {limit + 1} invalid attempts")

        gc.collect()
        logger.debug(f"GC stats:{gc.get_stats()}")

    return result


def benchmarking_test(experiment_handler, experiment_config, test_config):
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

    # a counter for the i'th iteration - implying a gradual increase in request tx/s
    ramp = 0
    retries = 0
    restarts = {}
    limit = experiment_config["retry_limit"]
    while retries < limit:

        restarts[f"retry_{retries}"] = {}

        logger.info(f"Retry {retries}, limit: {limit}")
        logger.info(f"Ramp: {ramp}")
        ramp += 1

        restarts[f"retry_{retries}"][f"ramp_{ramp}"] = 0

        test_config['ramp'] = ramp

        try:
            if test_config['rep'] != "":
                test_config['rep'] = f"_{ramp}_{retries}"
        except Exception as e:
            logger.exception(e)
            test_config['rep'] = ""

        if client_config["blockchain_type"] == "acapy":
            n = len(client_config["coordinator_indices"])
        else:
            n = len(client_config['priv_ips'])

        try:
            frequency = test_config['freqs'][ramp-1] / n
            freq = round(test_config['freqs'][ramp-1], 1)

        except:
            frequency = (test_config['base'] + test_config['step'] * ramp) / n
            freq = round(test_config['base'] + test_config['step'] * ramp, 1)

        test_config['frequency'] = frequency
        test_config['freq'] = f"{freq}"

        max_time = experiment_config['duration'] + experiment_config['delta_max_time']

        logger.info("")
        logger.info(f"New benchmarking run started @ frequency {test_config['freq']} and max_time {max_time} (frequency {test_config['frequency']})")

        # waiting such that all i/o from the last run is over
        time.sleep(7)

        try:
            start_resources_measurements_blockchain(experiment_handler, experiment_config, test_config)
            start_resources_measurements_clients(experiment_handler, experiment_config, test_config)

            # waiting in order to get CPU and ping also some time in advance of the test
            time.sleep(7)
            logger.info(f"Using frequency of {frequency}")
            if not start_benchmarking_measurements(experiment_handler, experiment_config, test_config, max_time, frequency):
                retries = retries + 1
                ramp = ramp - 1
                logger.info("Timeout - trying again with the same specification")
                time.sleep(7)
                continue

            time.sleep(7)
            get_benchmarking_data(experiment_handler, experiment_config, test_config)
            logger.info("Got the measurement data data")
            exception_indicator = False

            """
            time.sleep(10)
            logger.info("Continuing...")
            continue
            """

            res, r_value = evaluate_benchmarking_test(experiment_handler, experiment_config, test_config, False, True)

        except SSHException as e:
            logger.exception(e)
            experiment_handler.dapp_handler.refresh_ssh_scp_clients

            exception_indicator = True

        except BlockchainNotRespondingError as e:

            logger.exception(e)

            restart_blockchain(experiment_handler, experiment_config)

            restarts[f"retry_{retries}"][f"ramp_{ramp}"] = restarts[f"retry_{retries}"][f"ramp_{ramp}"] + 1

            exception_indicator = True

            experiment_handler.dapp_handler.refresh_ssh_scp_clients

        except Exception as e:
            logger.exception(e)
            exception_indicator = True

        if (exception_indicator == True
                or abs(float(res['throughput_receive']) / float(res['throughput_send']) - 1) > experiment_config["throughput_delta_bound_receive"]
                or abs(float(res['throughput_send']) / (float(frequency) * n) - 1) > experiment_config["throughput_delta_bound_send"]
                or res['effectivity'] < experiment_config['success_bound']
                or (r_value < experiment_config["r2_bound"] and float(frequency) * n > experiment_config["frequency_bound"])
                or res['latency'] > experiment_config["latency_bound"]
                or ('freqs' in test_config and ramp > len(test_config['freqs']) - 1)):

            if (exception_indicator == True and retries < limit - 1):
                retries = retries + 1
                ramp = ramp - 1
                logger.info("Exception thrown - trying again with the same specification")
                continue

            elif (exception_indicator == True and retries >= limit - 1):
                logger.info("Exception thrown, but maximum retries already reached")
                logger.info(f"Passing with ramp {ramp}")
                pass

            elif ((abs(float(res['throughput_send']) / (float(frequency) * n) - 1) > experiment_config["throughput_delta_bound_send"]) and retries < limit - 1):
                retries = retries + 1
                ramp = ramp - 1
                logger.info("Sending rate differed significantly from expected rate (frequency)- trying again with the same specification")
                continue

            elif (abs(float(res['throughput_receive']) / float(res['throughput_send']) - 1) > experiment_config["throughput_delta_bound_receive"] and retries < limit - 1):
                retries = retries + 1
                ramp = ramp - 1
                logger.info("Receiving rate differed significantly from sending rate - trying again with the same specification")
                continue

            elif (((r_value < experiment_config["r2_bound"] and float(frequency) * n > experiment_config["frequency_bound"]) or res['effectivity'] < experiment_config['success_bound'] or res['latency'] > experiment_config["latency_bound"]) and retries < limit - 1):
                retries = retries + 1
                ramp = ramp - 1
                logger.info("Other reason (error, r² or latency) for trying again with the same specification")
                logger.debug(f"effectivity: {res['effectivity']}")
                logger.debug(f"r_value: {r_value}")
                continue

            if exception_indicator == False:
                logger.info("Updating result")
                result = result_update(result, res, blockchain_config)
                result["restarts"] = restarts

            if ('freqs' in test_config) or ramp > 1:
                if 'freqs' in test_config:
                    logger.info(f"Last measurement finished.")
                else:
                    logger.info(f"Maximum throughput reached with ramp={ramp} (ratio send/receive: {round(result['throughput_receive'] / result['throughput_send'], 3)})")

                logger.info(f"Plotting aggregated chart and starting consecutive round")
                # create aggregate chart and save experiment results as json
                plot_aggregate_chart(experiment_handler, blockchain_config, test_config, result)
                with open(f"{test_config['exp_dir']}/result.json", 'w+') as outfile:
                    json.dump(result, outfile, default=datetimeconverter, indent=4)

                return result, ramp

            else:

                logger.info(f"Benchmarking run failed with ramp={ramp}")
                raise Exception("Too few rampings")

        else:

            retries = 0

            result = result_update(result, res, blockchain_config)

            plot_aggregate_chart(experiment_handler, blockchain_config, test_config, result)
            with open(f"{test_config['exp_dir']}/result.json", 'w+') as outfile:
                json.dump(result, outfile, default=datetimeconverter, indent=4)

            logger.info(f"Maximum throughput not yet reached (ratio out/in: {round(res['throughput_receive'] / res['throughput_send'], 2)})")

    experiment_handler.dapp_handler.close_ssh_scp_clients
