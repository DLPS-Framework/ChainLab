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
from BlockchainFormation.blockchain_specifics.fabric.Fabric_Network import *
import logging

utc = pytz.utc

import matplotlib
import matplotlib.pyplot as plt
from BlockchainFormation.Node_Handler import Node_Handler
from scipy import stats

from src.utils.csv_handling import *

from paramiko import SSHException


class BlockchainNotRespondingError(Exception):
    """Base class for exceptions in this module."""
    pass


class FileNotCompleteError(Exception):
    """Base class for exceptions in this module."""
    pass


class RetryLimitExceededException(Exception):
    """Base class for exceptions in this module."""
    pass


class AbortSetupException(Exception):
    """Base class for exceptions in this module."""
    pass



def get_keys(blockchain_config):
    """

    :return:
    """

    if blockchain_config['blockchain_type'] == "fabric":
        return ['scheduled_freq', 'throughputs_receive', 'throughputs_send', 'latencies', 'latencies_avg', 'latencies_std', 'effectivities', 'blockchain_cpus', 'client_cpus',
                'blockchain_pings', 'client_pings', 'blockchain_incomings', 'blockchain_outgoings', 'blockchain_disk_utilizations',
                'blockchain_single_cpus', 'blockchain_energy_consumption', 'blockchain_storage_consumption', 'blockchain_traffic',
                'client_incomings', 'client_outgoings', 'client_disk_utilizations', 'client_single_cpus',
                'client_energy_consumption', 'client_traffic', 'number_of_transactions', 'total_time',
                'peer_single_cpus_max', 'peer_incomings_max', 'peer_outgoings_max', 'orderer_single_cpus_max', 'orderer_incomings_max', 'orderer_outgoings_max',
                'peer_single_cpus_submax', 'peer_incomings_submax', 'peer_outgoings_submax', 'orderer_single_cpus_submax', 'orderer_incomings_submax', 'orderer_outgoings_submax',
                'peer_single_cpus_sum', 'orderer_single_cpus_sum']
    else:
        return ['scheduled_freq', 'throughputs_receive', 'throughputs_send', 'latencies', 'latencies_avg', 'latencies_std', 'effectivities', 'blockchain_cpus',
                'client_cpus',
                'blockchain_pings', 'client_pings', 'blockchain_incomings', 'blockchain_outgoings',
                'blockchain_disk_utilizations',
                'blockchain_single_cpus', 'blockchain_energy_consumption', 'blockchain_storage_consumption',
                'blockchain_traffic',
                'client_incomings', 'client_outgoings', 'client_disk_utilizations', 'client_single_cpus',
                'client_energy_consumption', 'client_traffic', 'number_of_transactions', 'total_time',
                'node_single_cpus_max', 'node_incomings_max', 'node_outgoings_max',
                'node_single_cpus_submax', 'node_incomings_submax', 'node_outgoings_submax',
                'node_single_cpus_sum']

def get_keys_rev(blockchain_config):
    """

    :return:
    """

    if blockchain_config['blockchain_type'] == "fabric":
        return ['scheduled_freq', 'throughput_receive', 'throughput_send', 'latency', 'latency_avg', 'latency_std', 'effectivity', 'blockchain_cpus', 'client_cpus',
                'blockchain_pings', 'client_pings', 'blockchain_incomings', 'blockchain_outgoings', 'blockchain_disk_utilizations',
                'blockchain_single_cpus', 'blockchain_energy_consumption', 'blockchain_storage_consumption', 'blockchain_traffic',
                'client_incomings', 'client_outgoings', 'client_disk_utilizations', 'client_single_cpus',
                'client_energy_consumption', 'client_traffic', 'number_of_transactions', 'total_time',
                'peer_single_cpus_max', 'peer_incomings_max', 'peer_outgoings_max', 'orderer_single_cpus_max', 'orderer_incomings_max', 'orderer_outgoings_max',
                'peer_single_cpus_submax', 'peer_incomings_submax', 'peer_outgoings_submax', 'orderer_single_cpus_submax', 'orderer_incomings_submax', 'orderer_outgoings_submax',
                'peer_single_cpus_sum', 'orderer_single_cpus_sum']

    else:
        return ['scheduled_freq', 'throughput_receive', 'throughput_send', 'latency', 'latency_avg', 'latency_std', 'effectivity', 'blockchain_cpus', 'client_cpus',
                'blockchain_pings', 'client_pings', 'blockchain_incomings', 'blockchain_outgoings',
                'blockchain_disk_utilizations',
                'blockchain_single_cpus', 'blockchain_energy_consumption', 'blockchain_storage_consumption',
                'blockchain_traffic',
                'client_incomings', 'client_outgoings', 'client_disk_utilizations', 'client_single_cpus',
                'client_energy_consumption', 'client_traffic', 'number_of_transactions', 'total_time',
                'node_single_cpus_max', 'node_incomings_max', 'node_outgoings_max',
                'node_single_cpus_submax', 'node_incomings_submax', 'node_outgoings_submax',
                'node_single_cpus_sum']


def get_res_result_mapping():
    """

    :return:
    """
    return {'scheduled_freq': 'scheduled_freq',
            'throughputs_receive': 'throughput_receive',
            'throughputs_send': 'throughput_send',
            'latencies': 'latency',
            'latencies_avg': 'latency_avg',
            'latencies_std': 'latency_std',
            'effectivities': 'effectivity',
            'blockchain_cpus': 'blockchain_cpus',
            'client_cpus': 'client_cpus',
            'blockchain_pings': 'blockchain_pings',
            'client_pings': 'client_pings',
            'blockchain_incomings': 'blockchain_incomings',
            'blockchain_outgoings': 'blockchain_outgoings',
            'blockchain_disk_utilizations': 'blockchain_disk_utilizations',
            'blockchain_single_cpus': 'blockchain_single_cpus',
            'blockchain_energy_consumption': 'blockchain_energy_consumption',
            'blockchain_storage_consumption': 'blockchain_storage_consumption',
            'blockchain_traffic': 'blockchain_traffic',
            'client_incomings': 'client_incomings',
            'client_outgoings': 'client_outgoings',
            'client_disk_utilizations': 'client_disk_utilizations',
            'client_single_cpus': 'client_single_cpus',
            'client_energy_consumption': 'client_energy_consumption',
            'client_traffic': 'client_traffic',
            'number_of_transactions': 'number_of_transactions',
            'total_time': 'total_time',
            'peer_single_cpus_max': 'peer_single_cpus_max',
            'peer_incomings_max': 'peer_incomings_max',
            'peer_outgoings_max': 'peer_outgoings_max',
            'node_single_cpus_max': 'node_single_cpus_max',
            'node_incomings_max': 'node_incomings_max',
            'node_outgoings_max': 'node_outgoings_max',
            'orderer_single_cpus_max': 'orderer_single_cpus_max',
            'orderer_incomings_max': 'orderer_incomings_max',
            'orderer_outgoings_max': 'orderer_outgoings_max',
            'peer_single_cpus_submax': 'peer_single_cpus_submax',
            'peer_incomings_submax': 'peer_incomings_submax',
            'peer_outgoings_submax': 'peer_outgoings_submax',
            'node_single_cpus_submax': 'node_single_cpus_submax',
            'node_incomings_submax': 'node_incomings_submax',
            'node_outgoings_submax': 'node_outgoings_submax',
            'orderer_single_cpus_submax': 'orderer_single_cpus_submax',
            'orderer_incomings_submax': 'orderer_incomings_submax',
            'orderer_outgoings_submax': 'orderer_outgoings_submax',
            'peer_single_cpus_sum': 'peer_single_cpus_sum',
            'orderer_single_cpus_sum': 'orderer_single_cpus_sum',
            'node_single_cpus_sum': 'node_single_cpus_sum'
        }


def get_res_result_mapping_rev():
    """

    :return:
    """
    return {'scheduled_freq': 'scheduled_freq',
            'throughput_receive': 'throughputs_receive',
            'throughput_send': 'throughputs_send',
            'latency': 'latencies',
            'latency_avg': 'latencies_avg',
            'latency_std': 'latencies_std',
            'effectivity': 'effectivities',
            'blockchain_cpus': 'blockchain_cpus',
            'client_cpus': 'client_cpus',
            'blockchain_pings': 'blockchain_pings',
            'client_pings': 'client_pings',
            'blockchain_incomings': 'blockchain_incomings',
            'blockchain_outgoings': 'blockchain_outgoings',
            'blockchain_disk_utilizations': 'blockchain_disk_utilizations',
            'blockchain_single_cpus': 'blockchain_single_cpus',
            'blockchain_energy_consumption': 'blockchain_energy_consumption',
            'blockchain_storage_consumption': 'blockchain_storage_consumption',
            'blockchain_traffic': 'blockchain_traffic',
            'client_incomings': 'client_incomings',
            'client_outgoings': 'client_outgoings',
            'client_disk_utilizations': 'client_disk_utilizations',
            'client_single_cpus': 'client_single_cpus',
            'client_energy_consumption': 'client_energy_consumption',
            'client_traffic': 'client_traffic',
            'number_of_transactions': 'number_of_transactions',
            'total_time': 'total_time',
            'peer_single_cpus_max': 'peer_single_cpus_max',
            'peer_incomings_max': 'peer_incomings_max',
            'peer_outgoings_max': 'peer_outgoings_max',
            'node_single_cpus_max': 'node_single_cpus_max',
            'node_incomings_max': 'node_incomings_max',
            'node_outgoings_max': 'node_outgoings_max',
            'orderer_single_cpus_max': 'orderer_single_cpus_max',
            'orderer_incomings_max': 'orderer_incomings_max',
            'orderer_outgoings_max': 'orderer_outgoings_max',
            'peer_single_cpus_submax': 'peer_single_cpus_submax',
            'peer_incomings_submax': 'peer_incomings_submax',
            'peer_outgoings_submax': 'peer_outgoings_submax',
            'node_single_cpus_submax': 'node_single_cpus_submax',
            'node_incomings_submax': 'node_incomings_submax',
            'node_outgoings_submax': 'node_outgoings_submax',
            'orderer_single_cpus_submax': 'orderer_single_cpus_submax',
            'orderer_incomings_submax': 'orderer_incomings_submax',
            'orderer_outgoings_submax': 'orderer_outgoings_submax',
            'peer_single_cpus_sum': 'peer_single_cpus_sum',
            'orderer_single_cpus_sum': 'orderer_single_cpus_sum',
            'node_single_cpus_sum': 'node_single_cpus_sum'
        }


def start_resources_measurements_blockchain(experiment_handler, experiment_config, test_config):
    """
    Start the resource measurement framework on the clients and blockchain instances, i.e. vmstat, ifstat, iostat, ...
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

    blockchain_ssh_clients = experiment_handler.dapp_handler.blockchain_handler.ssh_clients
    blockchain_scp_clients = experiment_handler.dapp_handler.blockchain_handler.scp_clients

    # Measurements are performed on all nodes
    indices = blockchain_config['node_indices']

    channels = []

    # Doing the same on orderers (and maybe more) in case the blockchain is fabric
    if blockchain_config['blockchain_type'] == "fabric":
        indices = indices + blockchain_config['orderer_indices'] + blockchain_config['zookeeper_indices'] + blockchain_config['kafka_indices']
        indices = unique(indices)

        if blockchain_config['fabric_settings']['database'] == "CouchDB" and (('external' in blockchain_config['fabric_settings'] and blockchain_config['fabric_settings']['external'] == 1) or ('external_database' in blockchain_config['fabric_settings'] and blockchain_config['fabric_settings']['external_database'] == 1)):
            indices = indices + blockchain_config['db_indices']

    # starting measurements on all blockchain VMs
    if client_config["blockchain_type"] != "acapy":
        n = len(indices)
        for node, index in enumerate(indices):

            measurements = {}
            measurements['iostat'] = "iostat -c 1 -x -g ALL -H | grep --line-buffered ALL | while read line; do echo $(date +%s) $line; done > io.log"
            measurements['vmstat'] = "vmstat 1 -n -a | while read line; do echo $(date +%s) $line; done > resources_measurement.log"
            measurements['ping'] = f"ping -U {blockchain_config['ips'][(index + 1) % n]} | sed -u 's#time=##g' | while read line; do echo $(date +%s) $line; done > ping.log"
            measurements['ifstat'] = "ifstat -n | while read line; do echo $(date +%s) $line; done > network.log"
            measurements['npstat'] = "mpstat -P ON 1 | while read line; do echo $(date +%s) $line; done > single_cpus.log"

            measurements_command = ""
            for key in measurements:
                if measurements_command != "":
                    measurements_command = measurements_command + "; "

                measurements_command = measurements_command + f"({measurements[key]} &)"

            channel = blockchain_ssh_clients[index].get_transport().open_session()
            channel.exec_command(measurements_command)
            channels.append(channel)

            # Measuring df
            stdin, stdout, stderr = blockchain_ssh_clients[index].exec_command(f"df > /home/ubuntu/df_before.log")
            wait_and_log(stdout, stderr)


def start_resources_measurements_clients(experiment_handler, experiment_config, test_config):
    """

    :param blockchain_config:
    :param client_config:
    :param experiment_config:
    :param test_config:
    :param logger:
    :param blockchain_ssh_clients:
    :param blockchain_scp_clients:
    :param client_ssh_clients:
    :param client_scp_clients:
    """

    blockchain_config = experiment_handler.blockchain_formation_config
    client_config = experiment_handler.client_config
    logger = experiment_handler.logger

    client_ssh_clients = experiment_handler.dapp_handler.client_handler.ssh_clients
    client_scp_clients = experiment_handler.dapp_handler.client_handler.scp_clients

    channels = []
    n = len(blockchain_config['node_indices'])

    for client, _ in enumerate(client_config['priv_ips']):

        measurements = {}
        measurements['iostat'] = "iostat -c 1 -x -g ALL -H | grep --line-buffered ALL | while read line; do echo $(date +%s) $line; done > io.log"
        measurements['vmstat'] = "vmstat 1 -n -a | while read line; do echo $(date +%s) $line; done > /home/ubuntu/resources_measurement.log"
        if n > 0:
            measurements['ping'] = f"ping -U {blockchain_config['priv_ips'][blockchain_config['node_indices'][client % n]]} | sed -u 's#time=##g' | while read line; do echo $(date +%s) $line; done > /home/ubuntu/ping.log"
        measurements['ifstat'] = "ifstat -n | while read line; do echo $(date +%s) $line; done > /home/ubuntu/network.log"
        measurements['npstat'] = "mpstat -P ON 1 | while read line; do echo $(date +%s) $line; done > /home/ubuntu/single_cpus.log"

        measurements_command = ""
        for key in measurements:
            if measurements_command != "":
                measurements_command = measurements_command + ";"

            measurements_command = measurements_command + f"({measurements[key]} &)"

        channel = client_ssh_clients[client].get_transport().open_session()
        channel.exec_command(measurements_command)
        channels.append(channel)


def start_benchmarking_measurements(experiment_handler, experiment_config, test_config, max_time, frequency):
    """
    Starts the Node JS benchmarking script on all clients and waits untill all requests are sent from these clients
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

    blockchain_ssh_clients = experiment_handler.dapp_handler.blockchain_handler.ssh_clients
    blockchain_scp_clients = experiment_handler.dapp_handler.blockchain_handler.scp_clients

    client_ssh_clients = experiment_handler.dapp_handler.client_handler.ssh_clients
    client_scp_clients = experiment_handler.dapp_handler.client_handler.scp_clients

    channels = []
    # TODO: make small breaks!!
    # If the frequency is f, then every client has to wait for number_of_clients/f seconds until he may send a request again
    # Consequently, the time between two clients sending a request should be (number_of_clients)/f seconds
    # With f = frequency * number_of_clients, we get that the time delta should be
    if experiment_config['shape'] == "smooth":
        delta = 1 / (frequency * len(client_config['priv_ips']))
        logger.info(f"Delay between clients: {delta}")
    else:
        delta = 0

    logger.info(f"Scheduled frequency per client: {frequency}")
    if client_config["blockchain_type"] == "acapy":
        client_indices = client_config["coordinator_indices"]
    else:
        client_indices = range(0, len(client_ssh_clients))

    # print(f"client_indices: {client_indices}")

    logger.info(f"New scheduled frequency per client: {frequency}")
    for _, client in enumerate(client_indices):

        if client * delta < experiment_config['duration']:
            start = time.time()
            try:
                # logger.info(f"Sending transactions from client {client} for duration {experiment_config['duration'] - client * delta}")
                client_channel = client_ssh_clients[client].get_transport().open_session()
                client_channel.exec_command(
                    f"source /home/ubuntu/.profile && cd /home/ubuntu/setup && DEBUG='*' node benchmarking.js --method {experiment_config['method']} --arg {experiment_config['arg']} --arg2 {experiment_config['arg2']} --mode {experiment_config['mode']} --duration {experiment_config['duration'] - client * delta} --shape {experiment_config['shape']} --frequency {frequency} --max_time {experiment_config['delta_max_time']} &> benchmarking.log && cat benchmarking_worker*.csv >> benchmarking.csv && rm benchmarking_worker*.csv")
                # logger.debug(f"Started sending requests on client {client}")
                channels.append(client_channel)
            except Exception as e:
                logger.info(f"Client {client} was not reachable - abort!")
                logger.exception(e)
                channels.append(client_channel)
            end = time.time()
            time.sleep(max(delta - (end - start), 0))

        else:
            pass
            # stdin, stdout, stderr = client_ssh_clients[client].exec_command("touch /home/ubuntu/setup/benchmarking.csv && touch /home/ubuntu/setup/benchmarking.log")
            # wait_and_log(stdout, stderr)

    """
    time.sleep(experiment_config['duration']/2)
    logger.info("Shutting down the raft leader")
    # Fabric_Network.shutdown_raft_nonleader(blockchain_config, blockchain_ssh_clients, blockchain_scp_clients, logger)
    Fabric_Network.stop_node(experiment_handler.dapp_handler.blockchain_handler, 1, 0)
    time.sleep(experiment_config['duration'] / 2)
    """

    logger.info(f"Waiting until all requests have been sent")
    status_flags = wait_till_done(client_config, [client_ssh_clients[index] for index in client_indices], [client_config['pub_ips'][index] for index in client_indices],
                                  np.ceil(max_time / 60) * 60 + 10, 10, "/home/ubuntu/setup/benchmarking.csv", False,
                                  max_time, logger)

    if False in status_flags:
        return False

    else:
        logger.info("Finished with sending the requests")
        return True


def get_benchmarking_data(experiment_handler, experiment_config, test_config):
    """
    Pulls the benchmarking data from the client and blockchain instances
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

    blockchain_ssh_clients = experiment_handler.dapp_handler.blockchain_handler.ssh_clients
    blockchain_scp_clients = experiment_handler.dapp_handler.blockchain_handler.scp_clients

    client_ssh_clients = experiment_handler.dapp_handler.client_handler.ssh_clients
    client_scp_clients = experiment_handler.dapp_handler.client_handler.scp_clients

    logger.info("Getting the measurement data")

    path = test_config['exp_dir']
    freq = test_config['freq']
    rep = test_config['rep']

    # logger.info("Getting csvs and logs for evaluation from clients and nodes")
    if client_config["blockchain_type"] == "acapy":
        client_indices = client_config["coordinator_indices"]
    else:
        client_indices = range(0, len(client_ssh_clients))

    for _, client in enumerate(client_indices):
        client_scp_clients[client].get(f"/home/ubuntu/setup/benchmarking.csv", path + f"/data/freq{freq}_client{client}_tx_data{rep}.csv")
        client_scp_clients[client].get(f"/home/ubuntu/setup/benchmarking.log", path + f"/logs/freq{freq}_client{client}_tx_data{rep}.log")
        client_scp_clients[client].get(f"/home/ubuntu/resources_measurement.log", path + f"/data/freq{freq}_client{client}_resources{rep}.csv")
        if len(blockchain_ssh_clients) > 0:
            client_scp_clients[client].get(f"/home/ubuntu/ping.log", path + f"/data/freq{freq}_client{client}_ping{rep}.csv")

        client_scp_clients[client].get(f"/home/ubuntu/io.log", path + f"/data/freq{freq}_client{client}_io{rep}.csv")
        client_scp_clients[client].get(f"/home/ubuntu/network.log", path + f"/data/freq{freq}_client{client}_network{rep}.csv")
        client_scp_clients[client].get(f"/home/ubuntu/single_cpus.log", path + f"/data/freq{freq}_client{client}_single_cpus{rep}.csv")
        os.system(f"awk 'NF>1' {path}/data/freq{freq}_client{client}_single_cpus{rep}.csv | awk '!/CPU/' | awk '!/all/' > {path}/data/freq{freq}_client{client}_single_cpus_clean{rep}.csv")
        stdin, stdout, stderr = client_ssh_clients[client].exec_command("rm /home/ubuntu/setup/benchmarking.csv /home/ubuntu/setup/benchmarking.log /home/ubuntu/ping.log /home/ubuntu/resources_measurement.log /home/ubuntu/io.log /home/ubuntu/network.log /home/ubuntu/single_cpus.log")
        stdout.readlines()
        stdin, stdout, stderr = client_ssh_clients[client].exec_command(
            "for pid in $(pidof iostat); do kill -9 $pid; done && for pid in $(pidof vmstat); do kill -9 $pid; done && for pid in $(pidof ping); do kill -9 $pid; done && for pid in $(pidof ifstat); do kill -9 $pid; done && for pid in $(pidof mpstat); do kill -9 $pid; done")
        stdout.readlines()

    types = ['node']
    if blockchain_config['blockchain_type'] == "vendia":
        types = []
    if blockchain_config['blockchain_type'] == "fabric":
        if blockchain_config['fabric_settings']['orderer_type'].upper() == "KAFKA":
            if 'internal_orderer' in blockchain_config['fabric_settings'] and blockchain_config['fabric_settings']['internal_orderer'] == 1:
                types = ['peer', 'zookeeper', 'kafka']
            else:
                types = ['peer', 'orderer', 'zookeeper', 'kafka']
        else:
            if 'internal_orderer' in blockchain_config['fabric_settings'] and blockchain_config['fabric_settings']['internal_orderer'] == 1:
                types = ['peer']
            else:
                types = ['peer', 'orderer']

        if blockchain_config['fabric_settings']['database'] == "CouchDB" and (('external' in blockchain_config['fabric_settings'] and blockchain_config['fabric_settings']['external'] == 1) or ('external_database' in blockchain_config['fabric_settings'] and blockchain_config['fabric_settings']['external_database'] == 1)):
            types.append('db')

    for type in types:
        type_indices = blockchain_config[f'{type}_indices']

        if client_config["blockchain_type"] == "acapy":
            blockchain_ssh_clients = [client_ssh_clients[i] for i in client_config["agent_indices"]]
            blockchain_scp_clients = [client_scp_clients[i] for i in client_config["agent_indices"]]
            type_indices = [0]

            # print(blockchain_scp_clients)
            # print(type_indices)

        for node, index in enumerate(type_indices):
            blockchain_scp_clients[index].get(f"/home/ubuntu/resources_measurement.log", path + f"/data/freq{freq}_{type}{node}_resources{rep}.csv")
            blockchain_scp_clients[index].get(f"/home/ubuntu/ping.log", path + f"/data/freq{freq}_{type}{node}_ping{rep}.csv")
            blockchain_scp_clients[index].get(f"/home/ubuntu/network.log", path + f"/data/freq{freq}_{type}{node}_network{rep}.csv")
            blockchain_scp_clients[index].get(f"/home/ubuntu/io.log", path + f"/data/freq{freq}_{type}{node}_io{rep}.csv")
            blockchain_scp_clients[index].get(f"/home/ubuntu/single_cpus.log", path + f"/data/freq{freq}_{type}{node}_single_cpus{rep}.csv")
            os.system(f"awk 'NF>1' {path}/data/freq{freq}_{type}{node}_single_cpus{rep}.csv | awk '!/CPU/' | awk '!/all/' > {path}/data/freq{freq}_{type}{node}_single_cpus_clean{rep}.csv")
            stdin, stdout, stderr = blockchain_ssh_clients[index].exec_command("rm /home/ubuntu/resources_measurement.log /home/ubuntu/ping.log /home/ubuntu/network.log /home/ubuntu/io.log /home/ubuntu/single_cpus.log")
            stdout.readlines()
            stdin, stdout, stderr = blockchain_ssh_clients[index].exec_command(
                "for pid in $(pidof iostat); do kill -9 $pid; done && for pid in $(pidof vmstat); do kill -9 $pid; done && for pid in $(pidof ping); do kill -9 $pid; done && for pid in $(pidof ifstat); do kill -9 $pid; done && for pid in $(pidof mpstat); do kill -9 $pid; done")
            stdout.readlines()

    # logger.info("All Measurements should now be pulled successfully")
    if blockchain_config['blockchain_type'] == "fabric":
        type = "peer"
    else:
        type = "node"

    if client_config["blockchain_type"] == "acapy":
        pass
    else:
        for node, index in enumerate(blockchain_config['node_indices']):
            stdin, stdout, stderr = blockchain_ssh_clients[index].exec_command(f"df > /home/ubuntu/df_after.log")
            wait_and_log(stdout, stderr)
            blockchain_scp_clients[index].get(f"/home/ubuntu/df_before.log", path + f"/data/freq{freq}_{type}{node}_df_before{rep}.csv")
            blockchain_scp_clients[index].get(f"/home/ubuntu/df_after.log", path + f"/data/freq{freq}_{type}{node}_df_after{rep}.csv")
            stdin, stdout, stderr = blockchain_ssh_clients[index].exec_command("rm /home/ubuntu/df_before.log /home/ubuntu/df_after.log")
            wait_and_log(stdout, stderr)


def evaluate_benchmarking_test(experiment_handler, experiment_config, test_config, demo, plot):
    """
    Evaluates a finished benchmark test
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

    path = test_config['exp_dir']
    freq = test_config['freq']
    rep = test_config['rep']

    # print(test_config)

    logger.info("Evaluating the data")

    measurements = {}

    # the data containing the cpu utilization of all the blockchain nodes
    measurements['blockchain_cpu_data'] = {}
    # the data containing the cpu utilization of all the clients
    measurements['client_cpu_data'] = []
    # the data containing the network speed (ping) among all the blockchain nodes
    measurements['blockchain_ping_data'] = {}
    # the data containing the network speed (ping) between the client and their respective blockchain nodes
    measurements['client_ping_data'] = []
    # the data cotaining the upload and download rate
    measurements['blockchain_network_data'] = {}
    measurements['client_network_data'] = {}
    # the data containing disk writing and reading
    measurements['blockchain_io_data'] = {}
    measurements['client_io_data'] = {}
    # the data containing the cpus usage of the most used core
    measurements['blockchain_single_cpu_data'] = {}
    measurements['client_single_cpu_data'] = {}

    # the data containing the total energy consumption
    measurements['blockchain_energy_consumption_data'] = {}
    measurements['client_energy_consumption_data'] = {}

    # the data containing the total storage required
    measurements['blockchain_storage_data'] = {}

    measurements['success_rates'] = []

    success_rates = []
    tx_data = []
    tx_data_all = []

    if client_config["blockchain_type"] == "acapy":
        client_indices = client_config["coordinator_indices"]
    else:
        client_indices = range(0, len(client_config['priv_ips']))

    # print(client_indices)
    for i, client in enumerate(client_indices):
        if i % 4 != 3:
            pass
            # continue
        else:
            pass

        # Reading tx_data on client {client} and removing invalid responses")
        try:
            # print(f"looking for /data/freq{freq}_client{client}_tx_data{rep}.csv")
            # print(path + f"/data/freq{freq}_client{client}_tx_data{rep}.csv")
            data = readCSV(path + f"/data/freq{freq}_client{client}_tx_data{rep}.csv", None)
            try:
                data = check_data(data, 3, logger, f"freq{freq}_client{client}_tx_data{rep}.csv")
            except Exception as e:
                print("Exception ")
                print(data)
                continue
            data_all = data
            data = data[np.where(data[:, 2] != -1)]
            if demo == False:
                success_rate = len(data[:, 0]) / (test_config['frequency'] * experiment_config['duration'])
                success_rates.append(success_rate)
                if (success_rate < 0 and (test_config['frequency'] * experiment_config['duration']) > 2):
                    logger.info(f"Too little valid responses on client {client}:")
                    logger.info(f"Expected length: {round(test_config['frequency'] * experiment_config['duration'], 1)}, actual length: {len(data[:, 0])} - repeating...")
                    raise BlockchainNotRespondingError()

        except Exception as e:
            # pass
            logger.exception(e)
            # logger.info(f"No response from blockchain on client {client}")
            # raise BlockchainNotRespondingError()

            data = []
            data_all = []

        # Putting everything together in tx_datas
        if tx_data == []:
            tx_data = data
        else:
            try:
                tx_data = np.concatenate((tx_data, data), axis=0)
            except Exception as e:
                pass
                # logger.exception(e)
                # raise Exception("Error when concatenating tx data")

        if tx_data_all == []:
            tx_data_all = data_all
        else:
            try:
                tx_data_all = np.concatenate((tx_data_all, data_all), axis=0)
            except Exception as e:
                pass
                # logger.exception(e)
                # raise Exception("Error when concatenating tx data all")

    cut_before = 0.1
    cut_after = 0.1

    tx_data_print = tx_data
    tx_data_all_print = tx_data_all

    tx_data = tx_data[tx_data[:, 0].argsort()]
    tx_data_print = tx_data_print[tx_data_print[:, 0].argsort()]

    tx_data[:, 0] = tx_data[:, 1] - tx_data[:, 2]
    tx_data_all[:, 0] = tx_data_all[:, 1] - tx_data_all[:, 2]

    tx_data_print[:, 0] = tx_data_print[:, 1] - tx_data_print[:, 2]
    tx_data_all_print[:, 0] = tx_data_all_print[:, 1] - tx_data_all_print[:, 2]

    tx_data = tx_data[:, 0:2]
    tx_data_all = tx_data_all[:, 0:2]

    tx_data_print = tx_data_print[:, 0:2]
    tx_data_all_print = tx_data_all_print[:, 0:2]


    # print("tx_data")
    # print(tx_data)
    # print("\ntx_data_all")
    # print(tx_data_all)

    base = min(tx_data_print[:, 0])
    up = max(tx_data_print[:, 0])
    # print(f"base: {base}")
    base_all = min(tx_data_all_print[:, 0])
    up_all = max(tx_data_all_print[:, 0])
    # print(f"base_all: {base_all}")

    tx_data[:, :] = tx_data[:, :] - base
    tx_data_all[:, :] = tx_data_all[:, :] - base_all

    tx_data_print[:, :] = tx_data_print[:, :] - base
    tx_data_all_print[:, :] = tx_data_all_print[:, :] # - base_all
    # print("tx_data: ")
    # print(tx_data)
    # print("\ntx_data_all")
    # print(tx_data_all)


    try:

        # if demo == False and effectivity < experiment_config['success_bound']:
        if demo == False and test_config['frequency'] * experiment_config['duration'] / len(success_rates) > 5 and min(success_rates) == 0:
            logger.info(f"Too little valid responses")
            # logger.info(f"Success rates: {success_rates}")
            logger.info(f"Expected length: {round(test_config['frequency'] * experiment_config['duration'], 1)}, actual length: {len(data[:, 0])} - repeating...")
            raise BlockchainNotRespondingError()

    except Exception as e:
        # logger.exception(e)
        if demo == False:
            logger.info(f"Success rates: {success_rates}")
        raise BlockchainNotRespondingError()

    tx_data_send = tx_data[tx_data[:, 0].argsort()]
    n = len(tx_data_send[:, 0])
    # print(f"n: {n}")
    # print("tx_data_send")
    # print(tx_data_send)
    # tx_data_send = tx_data_send[list(range(round(cut_before * n), round((1 - cut_after) * n))), :]
    # print(np.where((tx_data_send[:, 0] > cut_before * (up - base)) & (tx_data_send[:, 0] < (1 - cut_after) * (up - base))))
    tx_data_send = tx_data_send[np.where((tx_data_send[:, 0] > cut_before * (up - base)) & (tx_data_send[:, 0] < (1 - cut_after) * (up - base))), :][0]
    # print(tx_data_send)
    # print(np.arange(n * cut_before, n * cut_before + tx_data_send.shape[1]))
    tx_data_send[:, 1] = np.arange(n * cut_before, n * cut_before + len(tx_data_send[:, 0]))
    # print("After")
    # print(tx_data_send)

    effectivity = len(tx_data_send[:, 0]) / (float(test_config['freq']) * experiment_config['duration'] * (1 - cut_before - cut_after))
    print(effectivity)
    print(len(tx_data_print[:, 0]) / len(tx_data_all_print))
    logger.info(f"Effectivity: {effectivity}")

    n_all = len(tx_data_all[:, 0])
    tx_data_send_all = tx_data_all[tx_data_all[:, 0].argsort()]
    # tx_data_send_all = tx_data_send_all[list(range(round(cut_before * n), round((1 - cut_after) * n))), :]
    tx_data_send_all = tx_data_send_all[np.where((tx_data_send_all[:, 0] > cut_before * (up_all - base_all)) & (tx_data_send_all[:, 0] < (1 - cut_after) * (up_all - base_all))), :][0]
    tx_data_send_all[:, 1] = np.arange(n * cut_before, n * cut_before + len(tx_data_send_all))
    # print(tx_data_send_all)

    # print(tx_data_send_all)

    tx_data_receive = tx_data[tx_data[:, 1].argsort()]
    tx_data_receive = tx_data_receive[np.where((tx_data_receive[:, 0] > cut_before * (up - base)) & (tx_data_receive[:, 0] < (1 - cut_after) * (up - base))), :][0]
    tx_data_receive[:, 0] = tx_data_receive[:, 1]
    tx_data_receive[:, 1] = np.arange(n * cut_before, n * cut_before + len(tx_data_receive))
    # print(tx_data_receive)

    # print(tx_data_receive)
    
    tx_data_send_print = tx_data_print[tx_data_print[:, 0].argsort()]
    tx_data_send_print[:, 1] = np.arange(0, len(tx_data_send_print))

    tx_data_send_all_print = tx_data_all_print[tx_data_all_print[:, 0].argsort()]
    tx_data_send_all_print[:, 1] = np.arange(0, len(tx_data_send_all_print))

    tx_data_receive_print = tx_data_print[tx_data_print[:, 1].argsort()]
    tx_data_receive_print[:, 0] = tx_data_receive_print[:, 1]
    tx_data_receive_print[:, 1] = np.arange(0, len(tx_data_receive_print))

    number_of_transactions = len(tx_data_receive_print[:, 0])
    total_time = max(tx_data_print[:, 1]) / 1000

    slope_receive = 0

    try:
        # logger.debug(f"Sent: {tx_data_send}")
        # logger.debug(f"Received: {tx_data_receive}")
        slope_send, intercept_send, r_value_send, p_value_send, std_err_send = stats.linregress(tx_data_send.astype(np.float))
        slope_send_all, intercept_send_all, r_value_send_all, p_value_send_all, std_err_send_all = stats.linregress(tx_data_send_all.astype(np.float))
        slope_receive, intercept_receive, r_value_receive, p_value_receive, std_err_receive = stats.linregress(tx_data_receive.astype(np.float))
        # intercept_send = intercept_send + cut_before * n
        # intercept_send_all = intercept_send_all + cut_before * n
        # intercept_receive = intercept_receive + cut_before * n

    except Exception as e:
        logger.exception(e)
        # slope_send, intercept_send, r_value_send, p_value_send, std_err_send = stats.linregress(tx_data_send.astype(np.float))
        # slope_receive, intercept_receive, r_value_receive, p_value_receive, std_err_receive = stats.linregress(tx_data_receive.astype(np.float))
        logger.info(f"Sent: {tx_data_send_all}")
        logger.info(f"Received: {tx_data_receive}")
        raise Exception("Error when computing the regression")

    # for the latency, wey only take 50% of the data, because most of the time the blockchain can keep up in the beginning
    slope_receive_latency, intercept_receive_latency, r_value_latency, p_value_latency, std_err_receive_latency = stats.linregress(tx_data_receive.astype(np.float)[0:int(np.ceil(len(tx_data_receive) / 2)), :])
    # intercept_receive_latency = intercept_receive_latency

    r_value = min(r_value_send ** 2, r_value_receive ** 2)

    # print(f"Slope send: {slope_send_all}")
    # print(f"Slope receive: {slope_receive}")

    linear_send = slope_send * np.sort(np.append(tx_data_send[:, 0], tx_data_send[:, 1])) + intercept_send
    linear_send_all = slope_send_all * np.sort(np.append(tx_data_send_all[:, 0], tx_data_send_all[:, 1])) + intercept_send_all
    linear_receive = slope_receive * np.sort(np.append(tx_data_receive[:, 0], tx_data_receive[:, 1])) + intercept_receive
    linear_receive_latency = slope_receive_latency * np.sort(np.append(tx_data_receive[:, 0], tx_data_receive[:, 1])) + intercept_receive_latency

    linear_send_print = slope_send * np.sort(np.append(tx_data_send_print[:, 0], tx_data_send_print[:, 1])) + intercept_send
    linear_send_all_print = slope_send_all * np.sort(np.append(tx_data_send_all_print[:, 0], tx_data_send_all_print[:, 1])) + intercept_send_all
    linear_receive_print = slope_receive * np.sort(np.append(tx_data_receive_print[:, 0], tx_data_receive_print[:, 1])) + intercept_receive
    linear_receive_latency_print = slope_receive_latency * np.sort(np.append(tx_data_receive_print[:, 0], tx_data_receive_print[:, 1])) + intercept_receive_latency

    # calculate the throughput in unit tx/s and the latency in unit s
    throughput_send = slope_send * 1000
    throughput_send_all = slope_send_all * 1000
    throughput_receive = slope_receive * 1000

    print(slope_receive_latency/slope_send)

    latency = abs(intercept_receive_latency / slope_receive_latency - intercept_send / slope_send)

    # print(tx_data[:, 1] - tx_data[:, 0])
    n = len(tx_data[:, 0])
    tx_data_cut = tx_data[list(range(round(1/6*n), round(5/6*n))), :]

    latency_avg = np.mean(tx_data_cut[:, 1] - tx_data_cut[:, 0])
    latency_std = np.std(tx_data_cut[:, 1] - tx_data_cut[:, 0])

    logger.info(f"The throughput is {round(throughput_receive, 1)} tx/s at requesting {round(throughput_send_all, 1)} tx/s, and the latency is {round(latency, 0)} ms")
    logger.info(f"Average latency: {latency_avg}, standard deviation of latency: {latency_std}")

    transaction_data = {}
    transaction_data['tx_data'] = tx_data
    transaction_data['tx_data_all'] = tx_data_all
    transaction_data['tx_data_print'] = tx_data_print
    transaction_data['tx_data_all_print'] = tx_data_all_print
    transaction_data['effectivity'] = effectivity
    transaction_data['tx_data_send'] = tx_data_send
    transaction_data['tx_data_receive'] = tx_data_receive
    transaction_data['tx_data_send_print'] = tx_data_send_print
    transaction_data['tx_data_receive_print'] = tx_data_receive_print
    transaction_data['throughput_send'] = throughput_send
    transaction_data['latency'] = latency
    transaction_data['latency_avg'] = latency_avg
    transaction_data['latency_std'] = latency_std
    transaction_data['r_value'] = r_value
    transaction_data['tx_data_send_all'] = tx_data_send_all
    transaction_data['tx_data_send_all_print'] = tx_data_send_all_print
    transaction_data['slope_send_all'] = slope_send_all
    transaction_data['throughput_send_all'] = throughput_send_all
    transaction_data['intercept_send_all'] = intercept_send_all
    transaction_data['slope_receive'] = slope_receive
    transaction_data['intercept_receive'] = intercept_receive
    transaction_data['linear_send'] = linear_send
    transaction_data['linear_send_print'] = linear_send_print
    transaction_data['throughput_receive'] = throughput_receive
    transaction_data['linear_receive'] = linear_receive
    transaction_data['linear_receive_print'] = linear_receive_print
    transaction_data['linear_send_all'] = linear_send_all
    transaction_data['linear_send_all_print'] = linear_send_all_print
    transaction_data['linear_receive_latency'] = linear_receive_latency
    transaction_data['linear_receive_latency_print'] = linear_receive_latency_print

    try:
        transaction_data['number_of_transactions'] = number_of_transactions[0]
    except:
        transaction_data['number_of_transactions'] = number_of_transactions

    transaction_data['total_time'] = total_time

    # print(transaction_data)

    measurements['transaction_data'] = transaction_data

    # getting the resources logs for cpu, memory... measurement on clients

    stats_data = {}
    stats_data['cpu_data'] = {}
    stats_data['network_data'] = {}
    stats_data['io_data'] = {}

    blockchain_types = ['node']
    if blockchain_config['blockchain_type'] == "vendia":
        blockchain_types = []
    if blockchain_config['blockchain_type'] == "fabric":
        if blockchain_config['fabric_settings']['orderer_type'].upper() == "KAFKA":
            if 'internal_orderer' in blockchain_config['fabric_settings'] and blockchain_config['fabric_settings']['internal_orderer'] == 1:
                blockchain_types = ['peer', 'zookeeper', 'kafka']
            else:
                blockchain_types = ['peer', 'orderer', 'zookeeper', 'kafka']
        else:
            if 'internal_orderer' in blockchain_config['fabric_settings'] and blockchain_config['fabric_settings']['internal_orderer'] == 1:
                blockchain_types = ['peer']
            else:
                blockchain_types = ['peer', 'orderer']

    if blockchain_config['blockchain_type'] == "fabric":
        try:
            if blockchain_config['fabric_settings']['database'] == "CouchDB" and (('external' in blockchain_config['fabric_settings'] and blockchain_config['fabric_settings']['external'] == 1) or ('external_database' in blockchain_config['fabric_settings'] and blockchain_config['fabric_settings']['external_database'] == 1)):
                blockchain_types.append('db')

        except Exception as e:
            logger.exception(e)
            pass

    types = blockchain_types + ['client']
    for type in types:
        stats_data['cpu_data'][f'{type}_avg_cpu_data'] = collect_data(experiment_handler, path, type, base, "resources", freq, [0, 13], 1, 2, "minmax", logger, rep)

        temp = collect_data(experiment_handler, path, type, base, "single_cpus_clean", freq, [0, 2, 3, 5], 1, 4, None, logger, rep)
        # adding sys cpu and user cpu
        temp[:, 2] = temp[:, 2] + temp[:, 3]
        temp = np.delete(temp, 3, 1)
        # for each timestamp, find the minimum and maximum cpu utilization
        # TODO add standard deviation
        stats_strings = ["max", "submax", "mean", "median", "supmin", "min", "sum", "std"]
        for stat in stats_strings:
            stats_data['cpu_data'][f'{type}_single_cpu_data_{stat}'] = []

        for timestamp in np.unique(temp[:, 0]):
            for freq_index in np.unique(temp[:, -1][np.where((temp[:, 0] == timestamp))]):
                values = np.sort(temp[:, 2][np.where((temp[:, 0] == timestamp) & (temp[:, -1] == freq_index))])
                for stat in stats_strings:
                    stats_data['cpu_data'][f'{type}_single_cpu_data_{stat}'].append([timestamp, get_stat(values, stat), freq_index])

        for stat in stats_strings:
            stats_data['cpu_data'][f'{type}_single_cpu_data_{stat}'] = np.array(stats_data['cpu_data'][f'{type}_single_cpu_data_{stat}'])

        if len(blockchain_config['priv_ips']) > 0:
            stats_data['network_data'][f'{type}_ping_data'] = collect_data(experiment_handler, path, type, base, "ping", freq, [0, 7], 1, 2, "minmax", logger, rep)

        stats_data['network_data'][f'{type}_traffic_data_in'] = collect_data(experiment_handler, path, type, base, "network", freq, [0, 1], 2, 2, "minmax", logger, rep)
        stats_data['network_data'][f'{type}_traffic_data_out'] = collect_data(experiment_handler, path, type, base, "network", freq, [0, 2], 2, 2, "minmax", logger, rep)

        stats_data['io_data'][f'{type}_io_data'] = collect_data(experiment_handler, path, type, base, "io", freq, [0, 16], 1, 2, "minmax", logger, rep)
        stats_data[f'{type}_storage_data'] = get_storage_data(blockchain_config, path, freq, rep)

    single_cpu_data = {}
    energy_consumption_data = {}
    traffic_data = {}
    derived_data = {}

    for type in types:
        for stat in stats_strings:
            temp = stats_data['cpu_data'][f'{type}_single_cpu_data_{stat}']
            single_cpu_data[f'{type}_single_cpu_data_{stat}'] = {}
            derived_data[f'{type}_single_cpu_data_{stat}'] = {}
            for stat2 in stats_strings:
                single_cpu_data[f'{type}_single_cpu_data_{stat}'][stat2] = []
                derived_data[f'{type}_single_cpu_data_{stat}'][stat2] = {}
                for timestamp in np.unique(temp[:, 0]):
                    values = np.sort(temp[:, 1][np.where((temp[:, 0] == timestamp))])
                    single_cpu_data[f'{type}_single_cpu_data_{stat}'][stat2].append([timestamp, get_stat(values, stat2)])

            for stat2 in stats_strings:
                single_cpu_data[f'{type}_single_cpu_data_{stat}'][stat2] = np.array(single_cpu_data[f'{type}_single_cpu_data_{stat}'][stat2])
                for stat3 in stats_strings:
                    A = single_cpu_data[f'{type}_single_cpu_data_{stat}'][stat2]
                    values = np.sort(A[(A[:, 0] > 0) & (A[:, 0] < experiment_config['duration'] * 1000)][:, 1])
                    derived_data[f'{type}_single_cpu_data_{stat}'][stat2][stat3] = get_stat(values, stat3)

        for mode in ["in", "out"]:
            derived_data[f'{type}_traffic_data_{mode}'] = {}
            for stat in stats_strings:
                # print(stat)
                # print(stats_data['network_data'])
                derived_data[f'{type}_traffic_data_{mode}'][stat] = {}
                try:
                    A = stats_data['network_data'][f'{type}_traffic_data_{mode}'][stat]
                    values = np.sort(A[(A[:, 0] > 0) & (A[:, 0] < experiment_config['duration'] * 1000)][:, 1])
                    for stat2 in stats_strings:
                        derived_data[f'{type}_traffic_data_{mode}'][stat][stat2] = get_stat(values, stat2)
                except:
                    derived_data[f'{type}_traffic_data_{mode}'][stat][stat2] = 0

        derived_data[f'{type}_avg_cpu_data'] = {}
        derived_data[f'{type}_ping_data'] = {}
        derived_data[f'{type}_io_data'] = {}
        for stat in stats_strings:
            derived_data[f'{type}_avg_cpu_data'][stat] = {}
            A = stats_data['cpu_data'][f'{type}_avg_cpu_data'][stat]
            values = np.sort(A[(A[:, 0] > 0) & (A[:, 0] < experiment_config['duration'] * 1000)][:, 1])
            for stat2 in stats_strings:
                try:
                    derived_data[f'{type}_avg_cpu_data'][stat][stat2] = get_stat(values, stat)
                except:
                    derived_data[f'{type}_avg_cpu_data'][stat][stat2] = 0

            derived_data[f'{type}_ping_data'][stat] = {}
            if len(blockchain_config['priv_ips']) > 0 and blockchain_config['blockchain_type'] != "vendia":
                A = stats_data['network_data'][f'{type}_ping_data'][stat]
                values = np.sort(A[(A[:, 0] > 0) & (A[:, 0] < experiment_config['duration'] * 1000)][:, 1])
                for stat2 in stats_strings:
                    derived_data[f'{type}_ping_data'][stat][stat2] = get_stat(values, stat)
            else:
                derived_data[f'{type}_ping_data'][stat][stat2] = 0

            derived_data[f'{type}_io_data'][stat] = {}
            A = stats_data['io_data'][f'{type}_io_data'][stat]
            values = np.sort(A[(A[:, 0] > 0) & (A[:, 0] < experiment_config['duration'] * 1000)][:, 1])
            for stat2 in stats_strings:
                derived_data[f'{type}_io_data'][stat][stat2] = get_stat(values, stat)


    # derived_data['single_cpu_data'] = single_cpu_data
    # derived_data['energy_consumption_data'] = energy_consumption_data
    # derived_data['traffic_data'] = traffic_data

    for type in types:
        total_traffic = {}
        for mode in ['in', 'out']:
            total_traffic[f'{type}_{mode}'] = derived_data[f'{type}_traffic_data_{mode}']['sum']['sum']

    total_data = {}
    total_data['transaction_data'] = transaction_data
    total_data['stats_data'] = stats_data
    total_data['derived_data'] = derived_data
    total_data['single_cpu_data'] = single_cpu_data

    with open(f"{test_config['exp_dir']}/evaluation/total_data_freq_{test_config['freq']}{rep}.json", 'w+') as outfile:
        json.dump(total_data, outfile, default=datetimeconverter, indent=4)

    if plot:
        plot_benchmarking_run(experiment_handler, experiment_config, test_config, total_data, freq)

    pos = 10

    result = {}
    result['scheduled_freq'] = freq
    result['throughput_send'] = total_data['transaction_data']['throughput_send_all']
    result['throughput_receive'] = total_data['transaction_data']['throughput_receive']
    result['latency'] = total_data['transaction_data']['latency']
    result['latency_avg'] = total_data['transaction_data']['latency_avg']
    result['latency_std'] = total_data['transaction_data']['latency_std']
    result['effectivity'] = min(total_data['transaction_data']['effectivity'], 1)
    result['number_of_transactions'] = total_data['transaction_data']['number_of_transactions']
    result['total_time'] = total_data['transaction_data']['total_time']
    
    if len(blockchain_config['priv_ips']) > 0 and blockchain_config["blockchain_type"] != "vendia":
        result['blockchain_cpus'] = np.sort([derived_data[f'{type}_avg_cpu_data']['max']['mean'] for type in blockchain_types])[-1]
        result['blockchain_single_cpus'] = np.sort([derived_data[f'{type}_single_cpu_data_max']['max']['mean'] for type in blockchain_types])[-1]
        result['blockchain_pings'] = np.sort([derived_data[f'{type}_ping_data']['max']['mean'] for type in blockchain_types])[-1]
        result['blockchain_incomings'] = np.sort([derived_data[f'{type}_traffic_data_in']['max']['mean'] for type in blockchain_types])[-1]
        result['blockchain_outgoings'] = np.sort([derived_data[f'{type}_traffic_data_out']['max']['mean'] for type in blockchain_types])[-1]
        result['blockchain_disk_utilizations'] = np.sort([derived_data[f'{type}_io_data']['max']['mean'] for type in blockchain_types])[-1]
        result['blockchain_energy_consumption'] = np.sum([derived_data[f'{type}_single_cpu_data_sum']['sum']['sum'] for type in blockchain_types])
        result['blockchain_storage_consumption'] = total_data['stats_data'][f'{type}_storage_data']
        result['blockchain_traffic'] = np.sum([derived_data[f'{type}_traffic_data_in']['sum']['sum'] for type in blockchain_types]) + np.sum([derived_data[f'{type}_traffic_data_out']['sum']['sum'] for type in blockchain_types])
    else:
        result['blockchain_cpus'] = 0
        result['blockchain_single_cpus'] = 0
        result['blockchain_pings'] = 0
        result['blockchain_incomings'] = 0
        result['blockchain_outgoings'] = 0
        result['blockchain_disk_utilizations'] = 0
        result['blockchain_energy_consumption'] = 0
        result['blockchain_storage_consumption'] = 0
        result['blockchain_traffic'] = 0


    result['client_cpus'] = derived_data['client_avg_cpu_data']['max']['mean']
    result['client_single_cpus'] = derived_data['client_single_cpu_data_max']['max']['mean']

    if len(blockchain_config['priv_ips']) > 0 and blockchain_config["blockchain_type"] != "vendia":
        result['client_pings'] = derived_data['client_ping_data']['max']['mean']
    else:
        result['client_pings'] = 0

    result['client_incomings'] = derived_data['client_traffic_data_in']['max']['mean']
    result['client_outgoings'] = derived_data['client_traffic_data_out']['max']['mean']
    result['client_disk_utilizations'] = derived_data['client_io_data']['max']['mean']
    result['client_energy_consumption'] = derived_data['client_single_cpu_data_sum']['sum']['sum']
    result['client_traffic'] = derived_data['client_traffic_data_in']['sum']['sum'] + derived_data['client_traffic_data_out']['sum']['sum']

    if blockchain_config['blockchain_type'] == "fabric":
        types = ['peer', 'orderer']
    # elif blockchain_config['blockchain_type'] == "vendia":
        # types = []
    else:
        types = ['node']

    for stat in ['max', 'submax']:
        for type in types:
            try:
                result[f'{type}_single_cpus_{stat}'] = derived_data[f'{type}_single_cpu_data_max'][stat]['mean']
            except:
                result[f'{type}_single_cpus_{stat}'] = 0

            try:
                result[f'{type}_incomings_{stat}'] = derived_data[f'{type}_traffic_data_in'][stat]['mean']
            except:
                result[f'{type}_incomings_{stat}'] = 0

            try:
                result[f'{type}_outgoings_{stat}'] = derived_data[f'{type}_traffic_data_out'][stat]['mean']
            except:
                result[f'{type}_outgoings_{stat}'] = 0

    for type in types:
        try:
            result[f'{type}_single_cpus_sum'] = derived_data[f'{type}_single_cpu_data_sum']['sum']['sum']
        except:
            result[f'{type}_single_cpus_sum'] = 0

    # print(result)
    # print("average_latencies:")
    # print(result["latency_avg"])

    return result, r_value


def plot_aggregate_chart(experiment_handler, blockchain_config, test_config, result):
    blockchain_config = experiment_handler.blockchain_formation_config
    client_config = experiment_handler.client_config
    logger = experiment_handler.logger

    # Using seaborn's style
    # lt.style.use('seaborn')
    # plt.tight_layout()

    base_size = 8
    # base_size = 8

    nice_fonts = {
        "text.usetex": False,
        "axes.labelsize": base_size + 2,
        "font.size": base_size + 2,
        "legend.fontsize": base_size,
        "xtick.labelsize": base_size + 2,
        "ytick.labelsize": base_size + 2
    }

    plt.rcParams.update(nice_fonts)
    plt.rcParams['savefig.dpi'] = 300
    plt.rcParams['figure.figsize'] = 10.4, 4
    # plt.rcParams["legend.shadow"] = False
    # plt.rcParams["legend.framealpha"] = False

    plt.subplot(1, 2, 1)

    ax1 = plt.gca()

    type = "node"
    if blockchain_config['blockchain_type'] == "fabric":
        type = "peer"

    # fig, ax = plt.subplots(figsize=(6.4, 6.4))

    runs = result['runs']

    lns = []

    ax1.set_xlabel("Request rate $f_{\mathrm{req}}$ (tx/s)", labelpad=5)
    ax1.set_ylabel("Response rate $f_{\mathrm{resp}}$ (tx/s)", labelpad=10)
    ax2 = ax1.twinx()
    ax2.set_ylabel("Latency $l$ (s)", labelpad=10)

    norm_traffic = 1024

    ax3 = ax1.twinx()
    lns = lns + ax3.plot(runs['throughputs_send'], np.array(runs['effectivities']) * 100, color="darkorange", label="effectivity", linestyle=":", marker="s")
    lns = lns + ax1.plot(runs['throughputs_send'], runs['throughputs_receive'], color="darkgreen", label="throughput", marker="o")
    lns = lns + ax3.plot(runs['throughputs_send'], np.array(runs['blockchain_cpus']), color="red", label="max. CPU", linestyle="--", marker=">")
    lns = lns + ax2.plot(runs['throughputs_send'], np.array(runs['latencies']).astype(int) / 1000, color="deepskyblue", label="latency", linestyle="--", marker="d")
    try:
        ax2.errorbar(runs['throughputs_send'], np.array(runs['latencies_avg']).astype(int) / 1000, yerr=np.array(runs['latencies_std']).astype(int) / 1000, color="deepskyblue", label="latency", linestyle="-", marker="d")
    except Exception as e:
        print("Cannot plot avg_latency because it does not exist")
    if len(blockchain_config['priv_ips']) > 0:
        lns = lns + ax3.plot(runs['throughputs_send'], np.array(runs['blockchain_pings']) / 10, color="deepskyblue", label="blockchain ping (max)", linestyle="--", marker="v")
        lns = lns + ax3.plot(runs['throughputs_send'], np.array(runs['client_pings']) / 10, color="mediumblue", label="client ping (max)", linestyle=":", marker="o")
        lns = lns + ax3.plot(runs['throughputs_send'], np.array(runs['blockchain_incomings']) / norm_traffic, color="pink", label="blockchain incoming traffic (max)", linestyle="--", marker=">")
        lns = lns + ax3.plot(runs['throughputs_send'], np.array(runs['blockchain_outgoings']) / norm_traffic, label="blockchain outgoing traffic (max)", color="grey", linestyle='--', marker="<")
        lns = lns + ax3.plot(runs['throughputs_send'], np.array(runs['blockchain_disk_utilizations']), label="blockchain i/o utilization (max)", color="black", linestyle='--', marker="s")
        lns = lns + ax3.plot(runs['throughputs_send'], np.array(runs[f'{type}_single_cpus_max']), label=f"{type} single cpus (max)", color="red", linestyle="--", marker="o")
        lns = lns + ax3.plot(runs['throughputs_send'], np.array(runs['blockchain_energy_consumption']) / 60, label="blockchain energy consumption", color="orange", linestyle="--", marker="o")
        
    lns = lns + ax3.plot(runs['throughputs_send'], np.array(runs['client_single_cpus']), label="client single cpus (max)", color="darkred", linestyle="--", marker="o")
    lns = lns + ax3.plot(runs['throughputs_send'], np.array(runs['client_cpus']), color="darkred", label="client CPU (max)", linestyle=":", marker="s")
    lns = lns + ax3.plot(runs['throughputs_send'], np.array(runs['client_incomings']) / norm_traffic, color="pink", label="client incoming traffic (max)", linestyle="--", marker=">")
    lns = lns + ax3.plot(runs['throughputs_send'], np.array(runs['client_outgoings']) / norm_traffic, label="client outgoing traffic (max)", color="grey", linestyle='--', marker="<")
    lns = lns + ax3.plot(runs['throughputs_send'], np.array(runs['client_disk_utilizations']), label="client i/o utilization (max)", color="black", linestyle='--', marker="s")
    
    # lns = lns + ax3.plot(runs['throughputs_send'], np.array(np.array(runs['client_energy_consumption']) + np.array(runs['blockchain_energy_consumption'])) / 1000, label="total energy consumption", color="purple", linestyle="--", marker="o")
    # lns = lns + ax3.plot(runs['throughputs_send'], np.array((np.array(runs['client_energy_consumption']) + np.array(runs['blockchain_energy_consumption'])) / np.array(runs['number_of_transactions'])), label="energy consumption per transaction", color="purple", linestyle="--", marker="s")
    # lns = lns + ax3.plot(runs['throughputs_send'], np.array(np.array(runs['client_traffic']) + np.array(runs['blockchain_traffic'])) / 10000, label="total traffic", color="yellow", linestyle="--", marker="o")
    # lns = lns + ax3.plot(runs['throughputs_send'], np.array((np.array(runs['client_traffic']) + np.array(runs['blockchain_traffic'])) / np.array(runs['number_of_transactions']) / 10), label="traffic per transaction", color="yellow", linestyle="--", marker="s")

    ax2.set_ylim(bottom=0)
    ax3.set_ylim(bottom=0, top=102)

    # ax3.set_ylabel("effectivity, CPU (\%), traffic (10 MB/s), ping (ms)")
    ax3.set_ylabel("Effectivity, CPU usage (\%)")
    ax3.spines['right'].set_position(("outward", 60))

    labs = [l.get_label() for l in lns]
    ax1.legend(lns, labs, loc="upper left")

    """
    ax1.legend(lns, labs, loc="lower left", bbox_to_anchor=(0.5, 0.01))
    ax1.set_xlim(left=0)
    ax1.set_ylim(bottom=0)
    ax2.set_ylim(bottom=0, top=0.25)
    ax1.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(50))
    """

    ax1.get_xaxis().set_major_formatter(matplotlib.ticker.FormatStrFormatter('%i'))
    ax1.get_yaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
    ax2.get_yaxis().set_major_formatter(matplotlib.ticker.FormatStrFormatter('%.2f'))
    ax3.get_yaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))

    # plt.title(f"{blockchain_config['blockchain_type']} network, {len(blockchain_config['node_indices'])} nodes, {client_config['vm_count']} clients, {experiment_config['mode']} {experiment_config['method']}")

    plt.savefig(test_config['exp_dir'] + f"/chart.pdf", bbox_inches="tight")
    plt.close()


def modify(data):
    """
    TODO
    :param data:
    :return:
    """

    result = {}
    temp = np.array([[unique, np.max(data[data[:, 0] == unique][:, 1])] for unique in set(data[:, 0])])
    result["max"] = temp[temp[:, 0].argsort()]
    temp = np.array([[unique, np.sort(data[data[:, 0] == unique][:, 1])[(max(-2, -len(data[data[:, 0] == unique][:, 1])))]] for unique in set(data[:, 0])])
    result["submax"] = temp[temp[:, 0].argsort()]
    temp = np.array([[unique, np.mean(data[data[:, 0] == unique][:, 1])] for unique in set(data[:, 0])])
    result["mean"] = temp[temp[:, 0].argsort()]
    temp = np.array([[unique, np.median(data[data[:, 0] == unique][:, 1])] for unique in set(data[:, 0])])
    result["median"] = temp[temp[:, 0].argsort()]
    temp = np.array([[unique, np.sort(data[data[:, 0] == unique][:, 1])[(min(1, len(data[data[:, 0] == unique][:, 1])-1))]] for unique in set(data[:, 0])])
    result["supmin"] = temp[temp[:, 0].argsort()]
    temp = np.array([[unique, np.min(data[data[:, 0] == unique][:, 1])] for unique in set(data[:, 0])])
    result["min"] = temp[temp[:, 0].argsort()]
    temp = np.array([[unique, np.sum(data[data[:, 0] == unique][:, 1])] for unique in set(data[:, 0])])
    result["sum"] = temp[temp[:, 0].argsort()]
    temp = np.array([[unique, np.std(data[data[:, 0] == unique][:, 1])] for unique in set(data[:, 0])])
    result["std"] = temp[temp[:, 0].argsort()]
    return result


def check_data(data, number_of_columns, logger, file):
    """
    :param data: some np.array
    :return: raises FileNotCompleteException in case the data lacks some entries
    """
    # print(f"The type of data is {type(data)}")
    try:
        if data.shape[1] != number_of_columns:
            print(data)
            raise FileNotCompleteError(f"Expected {number_of_columns} columns, got {data.shape[1]}")

    except Exception as e:
        # logger.exception(e)
        # print(file)
        # if data == []:
            # print("[]")
        # else:
            # print(data)
        print(f"Other error for {file}")
        # raise FileNotCompleteError("Other error")

    try:
        if np.isnan(np.array(data, dtype=float)).any():
            data = np.array(data, dtype=float)
            logger.info("Deleted non-numerical lines")
            # logger.info(f"Before: {data.shape}")
            data = data[~np.isnan(data).any(axis=1)]
            # logger.info(f"After: {data.shape}")

    except Exception as e:
        try:
            # logger.exception(e)
            # print(data)
            temp = pd.DataFrame(data)
            # print(temp)
            # print(temp)
            for col in temp.columns:
                temp[col] = pd.to_numeric(temp[col], "coerce")
            # print(temp)
            print(np.array(temp, dtype=float))
            return np.array(temp, dtype=float)
        except Exception as f:
            logger.exception(f)
            # raise FileNotCompleteError(f"Error in file {file}")

    return data


def result_init(blockchain_config):
    result = {}
    result["runs"] = {}

    for key in get_keys(blockchain_config):
        result['runs'][key] = []

    return result


def result_update(result, res, blockchain_config):
    try:

        res_result_mapping = get_res_result_mapping()

        for key in get_keys(blockchain_config):
            result['runs'][key].append(res[res_result_mapping[key]])

        throughput_receive = max(result['runs']['throughputs_receive'])
        # print(f"throughput_receive:{throughput_receive}")
        indices = np.where(result['runs']['throughputs_receive'] >= 0.98 * throughput_receive)[0]
        # print(f"indices:{indices}")
        throughput_send = min([result['runs']['throughputs_send'][i] for i in indices])
        # print(f"throughput_send:{throughput_send}")
        index = np.where(result['runs']['throughputs_send'] == throughput_send)[0][0]
        # print(f"index:{index}")

        res_result_mapping_rev = get_res_result_mapping_rev()

        for key in get_keys_rev(blockchain_config):

            # if key not in ['blockchain_energy_consumption', 'client_energy_consumption', 'number_of_transactions', 'total_time', 'blockchain_traffic', 'client_traffic']:
            if True:
                if key == 'latency' or key == 'latency_avg' or key == 'latency_std':
                    try:
                        result[key] = result['runs'][res_result_mapping_rev[key]][index]
                    except:
                        print("Error as expected")
                        try:
                            print(index)
                            print(res_result_mapping_rev)
                            print(res_result_mapping_rev[key])
                            print(result)
                            print(result['runs'])
                        except Exception as e:
                            print(e)
                    # try:
                        # result[key] = np.mean(result['runs'][res_result_mapping_rev[key]][index - 1], [res_result_mapping_rev[key]][index - 2])
                    # except:
                        # result[key] = result['runs'][res_result_mapping_rev[key]][index - 1]
                else:
                    result[key] = result['runs'][res_result_mapping_rev[key]][index]
            else:
                result[key] = sum(result['runs'][res_result_mapping_rev[key]])

        result['energy_per_transaction'] = np.float(result['blockchain_energy_consumption'] + result['client_energy_consumption']) / np.float(result['number_of_transactions'])
        result['traffic_per_transaction'] = np.float(result['blockchain_traffic'] + result['client_traffic']) / np.float(result['number_of_transactions'])
        # if it has not been measured yet
        if result['blockchain_storage_consumption'] == "":
            result['storage_per_transaction'] = ""
        else:
            result['storage_per_transaction'] = np.float(result['blockchain_storage_consumption']) / np.float(result['number_of_transactions'])

        return result

    except Exception as e:

        print(e)
        raise Exception(("Error when updating result"))


def plot_benchmarking_run(experiment_handler, experiment_config, test_config, data, freq):
    blockchain_config = experiment_handler.blockchain_formation_config
    client_config = experiment_handler.client_config
    logger = experiment_handler.logger

    rep = test_config["rep"]

    sign_send = ""
    sign_send_all = "$-$"
    sign_receive = "$-$"
    if (data['transaction_data']['intercept_send_all'] >= 0):
        sign_send_all = "+$"

    if (data['transaction_data']['intercept_receive'] >= 0):
        sign_receive = "$+$"

    # Using seaborn's style
    # lt.style.use('seaborn')
    # plt.tight_layout()

    base_size = 8

    plt.rcParams['xtick.bottom'] = True
    plt.rcParams['xtick.labelbottom'] = True
    plt.rcParams['xtick.labeltop'] = False
    plt.rcParams['ytick.left'] = plt.rcParams['ytick.right'] = True
    plt.rcParams['ytick.labelleft'] = True
    plt.rcParams['ytick.labelright'] = False
    plt.rcParams['axes.titlepad'] = 15
    plt.rcParams['lines.markersize'] = 2


    plt.style.use('seaborn-paper')

    # base_size = 8

    nice_fonts = {
        "text.usetex": False,
        "axes.labelsize": base_size + 2,
        "font.size": base_size + 2,
        "legend.fontsize": base_size,
        "xtick.labelsize": base_size + 0.5,
        "ytick.labelsize": base_size + 0.5,
        "axes.titlesize": base_size + 3
    }
    
    plt.rcParams.update(nice_fonts)
    plt.rcParams['savefig.dpi'] = 300
    plt.rcParams['lines.markersize'] = 3
    plt.rcParams['figure.figsize'] = 10.4, 4.0
    plt.rcParams['lines.linewidth'] = 2.5
    plt.rcParams['legend.title_fontsize'] = base_size
    plt.rcParams["legend.loc"] = 'lower right'


    plt.subplot(1, 2, 1)

    plt.subplots_adjust(wspace=0.3)

    ax1 = plt.gca()

    prop_cycle = plt.rcParams['axes.prop_cycle']
    colors = prop_cycle.by_key()['color']

    # lns = lns + ax1.plot(np.sort(np.append(tx_data_receive[:, 0], tx_data_receive[:, 1])), linear_receive_latency, color="green")
    lns2 = ax1.plot(np.sort(np.append(data['transaction_data']['tx_data_send_all_print'][:, 0] / 1000, data['transaction_data']['tx_data_send_all_print'][:, 1] / 1000)), data['transaction_data']['linear_send_all_print'],
                    label=f"linear(requests): y" + "$=$" + f"{'{:,.0f}'.format(data['transaction_data']['slope_send_all'] * 1000)}" + "x" + f"{sign_send_all}" + "" + f"{'{:,.0f}'.format(abs(data['transaction_data']['intercept_send_all']))}", color=colors[0], zorder=10, linewidth=1.5, linestyle="--")
    lns1 = ax1.plot(data['transaction_data']['tx_data_send_all_print'][:, 0] / 1000, data['transaction_data']['tx_data_send_all_print'][:, 1], label="requests", color=colors[0], zorder=15)
    lns4 = ax1.plot(np.sort(np.append(data['transaction_data']['tx_data_receive_print'][:, 0], data['transaction_data']['tx_data_receive_print'][:, 1]) / 1000), data['transaction_data']['linear_receive_print'],
                    label=f"linear(responses): y" + "$=$" + f"{'{:,.0f}'.format(data['transaction_data']['slope_receive'] * 1000)}" + "x" + f"{sign_receive}" + "" + f"{'{:,.0f}'.format(abs(data['transaction_data']['intercept_receive']))}", color=colors[1], zorder=20, linewidth=1.5, linestyle="--")
    lns3 = ax1.plot(data['transaction_data']['tx_data_receive_print'][:, 0] / 1000, data['transaction_data']['tx_data_receive_print'][:, 1], label="responses", color=colors[1], zorder=25)
    lns = lns1
    lns += lns2
    lns += lns3
    lns += lns4

    # ax1.set_xlim(left=-0.5, right=2.0)
    # ax1.set_ylim(bottom=0, top=50)
    ax1.set_ylim(bottom=0, top=len(data['transaction_data']['tx_data_send_all_print'][:, 0])*1.1)

    ax1.set_xlabel("Time (s)", labelpad=5)
    ax1.set_ylabel("Cumulative number of transactions (10$^3$)", labelpad=10)

    ax2 = ax1.twinx()
    ax1.set_zorder(ax2.get_zorder() + 1)
    ax1.patch.set_visible(False)

    type = "node"
    if blockchain_config['blockchain_type'] == "fabric":
        type = "peer"

    norm_traffic = 1024
    # lns = lns + ax1.plot(tx_data_receive[:, 0] / 1000, tx_data_receive[:, 1], label="responses", color="darkgreen")ax2.plot(blockchain_cpu_data[f'{type}_cpu_data'][:, 0], blockchain_cpu_data[f'{type}_cpu_data'][:, 1], label=f"{type} blockchain cpu usage (min, max)", color="red", linestyle='--', marker=">")
    # ax2.plot(blockchain_cpu_data[f'{type}_cpu_data'][:, 0], blockchain_cpu_data[f'{type}_cpu_data'][:, 2], color="red", linestyle="--", marker=">")
    # lns = lns + ax1.plot(tx_data_receive[:, 0] / 1000, tx_data_receive[:, 1], label="responses", color="darkgreen")ax2.plot(client_cpu_data[:, 0], client_cpu_data[:, 1], label=f"client cpu usage (min, max)", color="darkred", linestyle=':', marker="s")
    # ax2.plot(client_cpu_data[:, 0], client_cpu_data[:, 2], color="darkred", linestyle=":", marker="s")
    if blockchain_config['blockchain_type'] == "fabric":
        if 'internal_orderer' in blockchain_config['fabric_settings'] and blockchain_config['fabric_settings']['internal_orderer'] == 1:
            types = ['peer']
        else:
            types = ['peer', 'orderer']

        for type in types:
            if type == ["peer"]:
                marker_min = "<"
                marker_max = ">"
            else:
                marker_min = "o"
                marker_max = "."

            lns = lns + ax2.plot(data['single_cpu_data'][f'{type}_single_cpu_data_max']['max'][:, 0] / 1000, data['single_cpu_data'][f'{type}_single_cpu_data_max']['max'][:, 1], label=f"{type} blockchain single core cpu usage (min, max)", color="red", linestyle='--', marker=marker_max, zorder=0)
            ax2.plot(data['single_cpu_data'][f'{type}_single_cpu_data_min']['min'][:, 0] / 1000, data['single_cpu_data'][f'{type}_single_cpu_data_min']['min'][:, 1], color="red", linestyle="--", marker=marker_min, zorder=0)
            lns = lns + ax2.plot(data['stats_data']['network_data'][f'{type}_ping_data']['max'][:, 0] / 1000, np.array(data['stats_data']['network_data'][f'{type}_ping_data']['max'][:, 1]) - 2 * experiment_config["delay"], label=f" $\Delta$ node ping (min, max)", color="deepskyblue", linestyle="--", marker=marker_max, zorder=0)
            ax2.plot(data['stats_data']['network_data'][f'{type}_ping_data']['min'][:, 0] / 1000, np.array(data['stats_data']['network_data'][f'{type}_ping_data']['min'][:, 1]), color="deepskyblue", linestyle="--", marker=marker_max)
            lns = lns + ax2.plot(data['stats_data']['network_data'][f'{type}_traffic_data_in']['max'][:, 0] / 1000, np.array(data['stats_data']['network_data'][f'{type}_traffic_data_in']['max'][:, 1]) / norm_traffic, label=f"{type} incoming traffic (min, max)", color="pink", linestyle='--', marker=marker_max, zorder=0)
            ax2.plot(data['stats_data']['network_data'][f'{type}_traffic_data_in']['min'][:, 0] / 1000, np.array(data['stats_data']['network_data'][f'{type}_traffic_data_in']['min'][:, 1]) / norm_traffic, color="pink", linestyle="--", marker=marker_min, zorder=0)
            lns = lns + ax2.plot(data['stats_data']['network_data'][f'{type}_traffic_data_out']['max'][:, 0] / 1000, np.array(data['stats_data']['network_data'][f'{type}_traffic_data_out']['max'][:, 1]) / norm_traffic, label=f"{type} outgoing traffic (min, max)", color="grey", linestyle='--', marker=marker_max, zorder=0)
            ax2.plot(data['stats_data']['network_data'][f'{type}_traffic_data_out']['min'][:, 0] / 1000, np.array(data['stats_data']['network_data'][f'{type}_traffic_data_out']['min'][:, 1]) / norm_traffic, color="grey", linestyle="--", marker=marker_min, zorder=0)
            
    elif blockchain_config['blockchain_type'] != "vendia":
        type = "node"
        marker_min = "<"
        marker_max = ">"
        lns = lns + ax2.plot(data['single_cpu_data'][f'{type}_single_cpu_data_max']['max'][:, 0] / 1000, data['single_cpu_data'][f'{type}_single_cpu_data_max']['max'][:, 1], label=f"cpu usage (min, max)", color="red", linestyle='--', marker=None)
        ax2.plot(data['single_cpu_data'][f'{type}_single_cpu_data_min']['min'][:, 0] / 1000, data['single_cpu_data'][f'{type}_single_cpu_data_min']['min'][:, 1], color="red", linestyle="--", marker=marker_min)
        # lns = lns + ax2.plot(data['stats_data']['network_data'][f'{type}_ping_data']['max'][:, 0] / 1000, np.array(data['stats_data']['network_data'][f'{type}_ping_data']['max'][:, 1]) - 2 * experiment_config["delay"], label=f" $\Delta$ node ping (min, max)", color="deepskyblue", linestyle="--", marker=marker_max)
        # ax2.plot(data['stats_data']['network_data'][f'{type}_ping_data']['min'][:, 0] / 1000, np.array(data['stats_data']['network_data'][f'{type}_ping_data']['min'][:, 1]), color="deepskyblue", linestyle="--", marker=marker_max)
        lns = lns + ax2.plot(data['stats_data']['network_data'][f'{type}_traffic_data_in']['max'][:, 0] / 1000, np.array(data['stats_data']['network_data'][f'{type}_traffic_data_in']['max'][:, 1]) / norm_traffic, label=f"incoming traffic (max)", color="pink", linestyle=':', marker=None)
        # ax2.plot(data['stats_data']['network_data'][f'{type}_traffic_data_in']['min'][:, 0] / 1000, np.array(data['stats_data']['network_data'][f'{type}_traffic_data_in']['min'][:, 1]) / norm_traffic, color="pink", linestyle=":", marker=marker_min)
        lns = lns + ax2.plot(data['stats_data']['network_data'][f'{type}_traffic_data_out']['max'][:, 0] / 1000, np.array(data['stats_data']['network_data'][f'{type}_traffic_data_out']['max'][:, 1]) / norm_traffic, label=f"outgoing traffic (max)", color="grey", linestyle=':', marker=None)
        # ax2.plot(data['stats_data']['network_data'][f'{type}_traffic_data_out']['min'][:, 0] / 1000, np.array(data['stats_data']['network_data'][f'{type}_traffic_data_out']['min'][:, 1]) / norm_traffic, color="grey", linestyle="--", marker=marker_min)

    type = "node"
    if blockchain_config['blockchain_type'] == "fabric":
        type = "peer"
    else:
        marker_min = "<"
        marker_max = ">"

    if blockchain_config['blockchain_type'] != "vendia":
        lns = lns + ax2.plot(data['stats_data']['io_data'][f'{type}_io_data']['max'][:, 0] / 1000, np.array(data['stats_data']['io_data'][f'{type}_io_data']['max'][:, 1]), label=f"i/o utilization (max)", color="black", linestyle='-.', marker=None)
        # ax2.plot(data['stats_data']['io_data'][f'{type}_io_data']['min'][:, 0] / 1000, np.array(data['stats_data']['io_data'][f'{type}_io_data']['min'][:, 1]), color="black", linestyle=":", marker=None)

    # lns = lns + ax2.plot(data['single_cpu_data']['client_single_cpu_data_max']['max'][:, 0] / 1000, data['single_cpu_data']['client_single_cpu_data_max']['max'][:, 1], label=f"client single core cpu usage (max)", color=colors[3], linestyle=':', marker="s")
    # ax2.plot(data['single_cpu_data']['client_single_cpu_data_min']['min'][:, 0] / 1000, data['single_cpu_data']['client_single_cpu_data_min']['min'][:, 1], color="darkred", linestyle="--", marker="s")

    # if len(blockchain_config['priv_ips']) > 0 and blockchain_config["blockchain_type"] != "vendia":
        # lns = lns + ax2.plot(data['stats_data']['network_data']['client_ping_data']['max'][:, 0] / 1000, np.array(data['stats_data']['network_data']['client_ping_data']['max'][:, 1]) - experiment_config["delay"], label=f" $\Delta$ client ping (min, max)", color="mediumblue", linestyle=":", marker="s")
        # ax2.plot(data['stats_data']['network_data']['client_ping_data']['min'][:, 0] / 1000, np.array(data['stats_data']['network_data']['client_ping_data']['min'][:, 1]), color="mediumblue", linestyle="--", marker="s")

        # lns = lns + ax2.plot(data['stats_data']['network_data'][f'client_traffic_data_in']['max'][:, 0] / 1000, np.array(data['stats_data']['network_data'][f'client_traffic_data_in']['max'][:, 1]) / norm_traffic, label=f"client incoming traffic (min, max)", color="pink", linestyle='--', marker="o")
        # ax2.plot(data['stats_data']['network_data'][f'client_traffic_data_in']['min'][:, 0] / 1000, np.array(data['stats_data']['network_data'][f'client_traffic_data_in']['min'][:, 1]) / norm_traffic, color="pink", linestyle="--", marker="o")
        # lns = lns + ax2.plot(data['stats_data']['network_data'][f'client_traffic_data_out']['max'][:, 0] / 1000, np.array(data['stats_data']['network_data'][f'client_traffic_data_out']['max'][:, 1]) / norm_traffic, label=f"client outgoing traffic (min, max)", color="grey", linestyle='--', marker="o")
        # ax2.plot(data['stats_data']['network_data'][f'client_traffic_data_out']['min'][:, 0] / 1000, np.array(data['stats_data']['network_data'][f'client_traffic_data_out']['min'][:, 1]) / norm_traffic, color="grey", linestyle="--", marker="o")
        # lns = lns + ax2.plot(data['stats_data']['io_data'][f'client_io_data']['max'][:, 0] / 1000, np.array(data['stats_data']['io_data'][f'client_io_data']['max'][:, 1]), label=f"client i/o utilization (min, max)", color="black", linestyle='--', marker="s")
        # ax2.plot(data['stats_data']['io_data'][f'client_io_data']['min'][:, 0] / 1000, np.array(data['stats_data']['io_data'][f'client_io_data']['min'][:, 1]), color="black", linestyle="--", marker="o")

    ax2.set_xlim(left=-10, right=(experiment_config['duration'] + experiment_config['delta_max_time']))
    ax2.set_ylim(bottom=0, top=100)
    ax2.set_ylabel("CPU utilization (%), Traffic (MB/s)")
    ax2.get_yaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x), ',')))

    """
    if blockchain_config['blockchain_type'] == 'fabric':
        type = "orderer"
        lns = lns + ax2.plot(blockchain_single_cpu_data[f'{type}_single_cpu_data_max'][:, 0] / 1000, blockchain_single_cpu_data[f'{type}_single_cpu_data_max'][:, 1], label=f"{type} blockchain single core cpu usage (min, max)", color="red", linestyle=':', marker="v")
        ax2.plot(blockchain_single_cpu_data[f'{type}_single_cpu_data_min'][:, 0] / 1000, blockchain_single_cpu_data[f'{type}_single_cpu_data_min'][:, 1], color="red", linestyle=":", marker="^")
        lns = lns + ax2.plot(blockchain_ping_data[f'{type}_ping_data'][:, 0] / 1000, np.array(blockchain_ping_data[f'{type}_ping_data'][:, 1]) - 2 * experiment_config["delay"], label=f" $\Delta$ node ping (min, max)", color="deepskyblue", linestyle=":", marker="v")
        ax2.plot(blockchain_ping_data[f'{type}_ping_data'][:, 0] / 1000, np.array(blockchain_ping_data[f'{type}_ping_data'][:, 2]) - 2 * experiment_config["delay"], color="deepskyblue", linestyle=":", marker="^")
        lns = lns + ax2.plot(blockchain_network_data[f'{type}_network_data_in'][:, 0] / 1000, np.array(blockchain_network_data[f'{type}_network_data_in'][:, 1]) / norm_traffic, label=f"{type} incoming traffic (min, max)", color="pink", linestyle=':', marker="v")
        ax2.plot(blockchain_network_data[f'{type}_network_data_in'][:, 0] / 1000, np.array(blockchain_network_data[f'{type}_network_data_in'][:, 2]) / norm_traffic, color="pink", linestyle=":", marker="^")
        lns = lns + ax2.plot(blockchain_network_data[f'{type}_network_data_out'][:, 0] / 1000, np.array(blockchain_network_data[f'{type}_network_data_out'][:, 1]) / norm_traffic, label=f"{type} outgoing traffic (min, max)", color="grey", linestyle=':', marker="v")
        ax2.plot(blockchain_network_data[f'{type}_network_data_out'][:, 0] / 1000, np.array(blockchain_network_data[f'{type}_network_data_out'][:, 2]) / norm_traffic, color="grey", linestyle=":", marker="^")
        lns = lns + ax2.plot(blockchain_io_data[f'{type}_io_data'][:, 0] / 1000, np.array(blockchain_io_data[f'{type}_io_data'][:, 1]), label=f"{type} i/o utilization (min, max)", color="black", linestyle=':', marker="v")
        ax2.plot(blockchain_io_data[f'{type}_io_data'][:, 0] / 1000, np.array(blockchain_io_data[f'{type}_io_data'][:, 2]), color="black", linestyle="--", marker="s")

    if blockchain_config['blockchain_type'] == 'fabric' and blockchain_config['fabric_settings']['orderer_type'].upper() == 'KAFKA':
        type = "kafka"
        lns = lns + ax2.plot(blockchain_cpu_data[f'{type}_cpu_data'][:, 0] / 1000, blockchain_cpu_data[f'{type}_cpu_data'][:, 1], label=f"{type} cpu usage", color="red", linestyle='-', marker=">")
        ax2.plot(blockchain_cpu_data[f'{type}_cpu_data'][:, 0] / 1000, blockchain_cpu_data[f'{type}_cpu_data'][:, 2], color="red", linestyle="-", marker=">")

        type = "zookeeper"
        lns = lns + ax2.plot(blockchain_cpu_data[f'{type}_cpu_data'][:, 0] / 1000, blockchain_cpu_data[f'{type}_cpu_data'][:, 1], label=f"{type} cpu usage", color="red", linestyle='-.', marker=">")
        ax2.plot(blockchain_cpu_data[f'{type}_cpu_data'][:, 0] / 1000, blockchain_cpu_data[f'{type}_cpu_data'][:, 2], color="red", linestyle="-.", marker=">")

    # plt.title(f"{blockchain_config['blockchain_type']} network, {len(blockchain_config['node_indices'])} nodes, {client_config['vm_count']} clients, {experiment_config['mode']} {experiment_config['method']} @ {freq} tx/s")
    """

    labs = [l.get_label() for l in lns]
    ax1.legend(lns, labs, loc=(-0.065, -0.45), ncol=2)

    ax1.get_xaxis().set_major_formatter(matplotlib.ticker.FormatStrFormatter('%i'))
    ax1.get_yaxis().set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, p: format(int(x/1000), ',')))

    plt.savefig(test_config['exp_dir'] + f"/evaluation/freq{freq}{rep}.pdf", bbox_inches="tight")
    plt.close()


def collect_data(experiment_handler, path, type, base, resource, freq, columns, header1, header2, mode, logger, rep):
    blockchain_config = experiment_handler.blockchain_formation_config
    client_config = experiment_handler.client_config
    logger = experiment_handler.logger

    data = []

    if type == "client":
        if client_config["blockchain_type"] != "acapy":
            indices = range(0, len(client_config['priv_ips']))
        else:
            indices = client_config["coordinator_indices"]
    else:
        if client_config["blockchain_type"] != "acapy":
            if type == "peer":
                indices = range(0, len(blockchain_config[f'{type}_indices']))
            elif type == "db":
                indices = range(0, len(blockchain_config[f'{type}_indices']))
            else:
                indices = blockchain_config[f'{type}_indices']
        else:
            indices = client_config["agent_indices"]

    # print(type)
    # print(indices)
    for i, index in enumerate(indices):
        if type == "client" and i % 4 != 3:
            # continue
            pass
        else:
            # print(f"{i}")
            pass


        temp = readCSV(path + f"/data/freq{freq}_{type}{index}_{resource}{rep}.csv", header1)
        # print(testfun(temp))
        # print(f"freq{freq}_{type}{index}_{resource}{rep}.csv")
        try:
            temp = check_data(temp[:, columns], header2, logger, f"freq{freq}_{type}{index}_{resource}{rep}.csv")
            # normalize the time
            temp[:, 0] = (temp[:, 0] - base / 1000) * 1000
            # remove non-numeric data

            # add a column for the index of the node to make them distinguishable
            if mode != "minmax":
                temp = np.insert(temp, np.size(temp, 1), values=index, axis=1)

            if data == []:
                data = temp
            else:
                data = np.concatenate((data, temp), axis=0)

        except:
            logger.warn(f"No or broken data for freq{freq}_{type}{index}_{resource}{rep}.csv")

    try:
        data = np.vstack(data[:, :]).astype(np.float)

        if mode == "minmax":
            data = modify(data)
        else:
            # print(f"Other mode for {resource}")
            pass

        return data

    except:
        logger.warn("No data for ...")
        return []


def get_storage_data(blockchain_config, path, freq, rep):
    if blockchain_config['blockchain_type'] == "fabric":
        type = "peer"
    else:
        type = "node"

    consumed_storage = []

    try:
        for node, index in enumerate(blockchain_config['node_indices']):
            data_before = readCSV(path + f"/data/freq{freq}_{type}{node}_df_before{rep}.csv", 1)
            data_after = readCSV(path + f"/data/freq{freq}_{type}{node}_df_after{rep}.csv", 1)

            for row in data_before:
                if data_before[row][-1] == '/data':
                    storage_before = data_before[row][2]
                    break

            for row in data_after:
                if data_after[row][-1] == '/data':
                    storage_after = data_after[row][2]
                    break

            consumed_storage.append(storage_after - storage_before)

        return np.mean(consumed_storage)

    except:
        return ""


def set_delays(experiment_handler, experiment_config):
    if experiment_config['delay'] != 0:
        # setting delay and traffic bound
        # https://netbeez.net/blog/how-to-use-the-linux-traffic-control/

        blockchain_config = experiment_handler.blockchain_formation_config
        client_config = experiment_handler.client_config
        logger = experiment_handler.logger

        blockchain_ssh_clients = experiment_handler.dapp_handler.blockchain_handler.ssh_clients
        blockchain_scp_clients = experiment_handler.dapp_handler.blockchain_handler.scp_clients

        client_ssh_clients = experiment_handler.dapp_handler.client_handler.ssh_clients
        client_scp_clients = experiment_handler.dapp_handler.client_handler.scp_clients

        all_ips = blockchain_config['priv_ips'] + client_config['priv_ips']
        logger.debug(f"all ips: {all_ips}")

        if blockchain_config['blockchain_type'] != "fabric":

            for index in blockchain_config["node_indices"]:

                target_ips = []
                for index2 in range(len(blockchain_config['node_indices'])):
                    if index2 != index:
                        target_ips.append(blockchain_config['priv_ips'][index2])

                target_ip_string = "("
                for ip in target_ips:
                    if target_ip_string != "(":
                        target_ip_string = target_ip_string + " "

                    target_ip_string = target_ip_string + f"{ip}"

                target_ip_string = target_ip_string + ")"

                logger.info(f"Target ips for {blockchain_config['priv_ips'][index]}: {target_ip_string}")

                stdin, stdout, stderr = blockchain_ssh_clients[index].exec_command(f"bash /home/ubuntu/set_delays.sh set {experiment_config['delay']}ms {target_ip_string}")
                logger.info(stdout.readlines())
                logger.info(stderr.readlines())

            for index, _ in enumerate(client_config['priv_ips']):

                target_ips = []
                n = len(blockchain_config['node_indices'])

                target_ips = []
                for index2, _ in enumerate(client_config['priv_ips']):
                    if index2 % n != index:
                        target_ips.append(blockchain_config['priv_ips'][index2])

                target_ip_string = "'"
                for ip in target_ips:
                    if target_ip_string != "'":
                        target_ip_string = target_ip_string + " "

                    target_ip_string = target_ip_string + f"{ip}"

                target_ip_string = target_ip_string + "'"

                logger.info(f"Target ips for {client_config['priv_ips'][index]}: {target_ip_string}")

                stdin, stdout, stderr = blockchain_ssh_clients[index].exec_command(f"bash /home/ubuntu/set_delays.sh set {experiment_config['delay']}ms {target_ip_string}")
                logger.info(stdout.readlines())
                logger.info(stderr.readlines())

        else:

            # currently only reasonable for raft
            for org in range(0, blockchain_config['fabric_settings']['org_count']):

                peer_range = range(org * blockchain_config['fabric_settings']['peer_count'], (org + 1) * (blockchain_config['fabric_settings']['peer_count']))

                peer_indices = []
                peer_ips = []

                db_indices = []
                db_ips = []

                for _, node in enumerate(peer_range):
                    peer_indices.append(blockchain_config['peer_indices'][node])
                    peer_ips.append(blockchain_config['priv_ips'][blockchain_config['peer_indices'][node]])

                    if blockchain_config['fabric_settings']['database'] == "CouchDB" and (('external' in blockchain_config['fabric_settings'] and blockchain_config['fabric_settings']['external'] == 1) or ('external_database' in blockchain_config['fabric_settings'] and blockchain_config['fabric_settings']['external_database'] == 1)):
                        db_indices.append(blockchain_config['db_indices'][node])
                        db_ips.append(blockchain_config['priv_ips'][blockchain_config['db_indices'][node]])

                if blockchain_config['fabric_settings']['orderer_count'] % blockchain_config['fabric_settings']['org_count'] == 0:

                    n = int(blockchain_config['fabric_settings']['orderer_count'] / blockchain_config['fabric_settings']['org_count'])

                    orderer_indices = []
                    orderer_ips = []

                    for orderer in range(org * n, (org + 1) * n):
                        orderer_indices.append(blockchain_config['orderer_indices'][orderer])
                        orderer_ips.append(blockchain_config['priv_ips'][blockchain_config['orderer_indices'][orderer]])

                else:

                    orderer_indices = []
                    orderer_ips = []

                client_indices = []
                client_ips = []
                for client in range(0, len(client_config['priv_ips'])):
                    if client % blockchain_config['fabric_settings']['org_count'] != org:
                        pass
                    else:
                        client_indices.append(client)
                        client_ips.append(client_config['priv_ips'][client])

                indices_blockchain = peer_indices + orderer_indices + db_indices
                indices_clients = client_indices

                target_ips_excluded = peer_ips + db_ips + orderer_ips + client_ips

                target_ip_string = "'"
                for ip in all_ips:

                    if ip in target_ips_excluded:
                        pass
                    else:
                        if target_ip_string != "'":
                            target_ip_string = target_ip_string + " "

                        target_ip_string = target_ip_string + f"{ip}"

                target_ip_string = target_ip_string + "'"

                logger.info(f"For org{org + 1}")
                logger.info(f"Blockchain indices: {indices_blockchain}")
                logger.info(f"Client indices: {indices_clients}")
                logger.info(f"Target ips: {target_ip_string}")

                for index in indices_blockchain:
                    stdin, stdout, stderr = blockchain_ssh_clients[index].exec_command(f"bash /home/ubuntu/set_delays.sh set {experiment_config['delay']}ms {target_ip_string}")
                    logger.info(stdout.readlines())
                    logger.info(stderr.readlines())

                for index in indices_clients:
                    stdin, stdout, stderr = client_ssh_clients[index].exec_command(f"bash /home/ubuntu/set_delays.sh set {experiment_config['delay']}ms {target_ip_string}")
                    logger.info(stdout.readlines())
                    logger.info(stderr.readlines())

            if blockchain_config['fabric_settings']['orderer_count'] % blockchain_config['fabric_settings']['org_count'] != 0:

                logger.info("Remaining")
                logger.info(f"Orderer indices: {blockchain_config['orderer_indices']}")

                for orderer in blockchain_config['orderer_indices']:

                    target_ip_string = "'"
                    for ip in all_ips:
                        if ip != blockchain_config['priv_ips'][orderer]:
                            if target_ip_string != "'":
                                target_ip_string = target_ip_string + " "
                            target_ip_string = target_ip_string + f"{ip}"

                    target_ip_string = target_ip_string + "'"

                    logger.info(f"For {blockchain_config['priv_ips'][orderer]}")
                    logger.info(f"Target ips: {target_ip_string}")

                    stdin, stdout, stderr = blockchain_ssh_clients[orderer].exec_command(f"bash /home/ubuntu/set_delays.sh set {experiment_config['delay']}ms {target_ip_string}")
                    logger.info(stdout.readlines())
                    logger.info(stderr.readlines())

        experiment_handler.dapp_handler.close_ssh_scp_clients


def reset_delays(experiment_handler, experiment_config):
    blockchain_config = experiment_handler.blockchain_formation_config
    client_config = experiment_handler.client_config
    logger = experiment_handler.logger

    blockchain_ssh_clients = experiment_handler.dapp_handler.blockchain_handler.ssh_clients
    blockchain_scp_clients = experiment_handler.dapp_handler.blockchain_handler.scp_clients

    client_ssh_clients = experiment_handler.dapp_handler.client_handler.ssh_clients
    client_scp_clients = experiment_handler.dapp_handler.client_handler.scp_clients

    if experiment_config['delay'] != 0:
        # setting delay and traffic bound
        # https://netbeez.net/blog/how-to-use-the-linux-traffic-control/

        blockchain_config = experiment_handler.blockchain_formation_config
        client_config = experiment_handler.client_config
        logger = experiment_handler.logger

        blockchain_ssh_clients = experiment_handler.dapp_handler.blockchain_handler.ssh_clients
        blockchain_scp_clients = experiment_handler.dapp_handler.blockchain_handler.scp_clients

        for client in blockchain_ssh_clients + client_ssh_clients:
            stdin, stdout, stderr = client.exec_command(f"bash /home/ubuntu/set_delays.sh reset {experiment_config['delay']}ms none")
            logger.info(stdout.readlines())
            logger.info(stderr.readlines())


def restart_blockchain(experiment_handler, experiment_config):
    blockchain_config = experiment_handler.blockchain_formation_config
    client_config = experiment_handler.client_config
    logger = experiment_handler.logger

    raise BlockchainNotRespondingError

    if blockchain_config['blockchain_type'] in ["couchdb", "fabric", "geth", "indy", "parity", "quorum", "sawtooth"]:
        logger.debug("Trying to restart the Network, since Blockchain not responding")

        reset_delays(experiment_handler, experiment_config)

        if blockchain_config["blockchain_type"] == "fabric":

            experiment_handler.dapp_handler.blockchain_handler.restart_network()
            # experiment_handler.dapp_handler.blockchain_handler.restart_network(experiment_config["number_of_endorsers"])
            
        else:

            experiment_handler.dapp_handler.blockchain_handler.restart_network()

        time.sleep(5)

        set_delays(experiment_handler, experiment_config)

    else:

        raise BlockchainNotRespondingError


def get_stat(values, stat):

    if stat == "max":
        return values[-1]
    elif stat == "submax":
        return values[max(-2, -len(values))]
    elif stat == "mean":
        return np.mean(values)
    elif stat == "median":
        return np.median(values)
    elif stat == "supmin":
        return values[min(1, len(values)-1)]
    elif stat == "min":
        return values[0]
    elif stat == "sum":
        return np.sum(values)
    elif stat == "std":
        return np.std(values)
    else:
        print(f"Invalid stat: {stat}")