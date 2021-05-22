import paho.mqtt.client as mqtt
import time
import yaml
import argparse
import logging
import sys
import requests


def read_config(config_path):
    with open(config_path) as file:
        return yaml.load(file, Loader=yaml.SafeLoader)


def on_connect(client, userdata, flags, rc):
    logging.info('Connected to MQTT with result code ' + str(rc))


def run_prom_query(query, config):

    url = '{0}://{1}/api/v1/query'.format(
        config.get('prom').get('protocol'),
        config.get('prom').get('host')
    )
    payload = {'query': query.get('query')}
    logging.info('Running prom query %s?query=%s', url, payload['query'])
    response = requests.get(url, params=payload, verify=config.get('prom').get('ca-path'))

    if not response.ok:
        logging.error(response.content)
        return

    response = response.json()

    if response.get('status') != 'success':
        logging.error('Got result %s from Prometheus: %s', response.get('status'), response.get('error'))
        return
    if not len(response.get('data').get('result')):
        logging.info('No results from query, returning default value of %s', query.get('noresultsval'))
        return query.get('noresultsval')

    query_result = response.get('data').get('result')[0].get('value')[1]
    logging.info('Prom query %s result is %s', payload['query'], query_result)

    return query_result


def main(args):
    config = read_config(args.config)

    client = mqtt.Client(client_id=config.get('mqtt').get('client-id'))
    client.on_connect = on_connect

    if config.get('mqtt').get('username'):
        client.username_pw_set(config.get('mqtt').get('username'), config.get('mqtt').get('password'))

    client.connect(config.get('mqtt').get('host'), config.get('mqtt').get('port'))
    client.enable_logger()

    time.sleep(2)

    while True:
        if client.is_connected():
            logging.fatal('Not connected to MQTT, exiting')
            sys.exit(1)

        for query in config.get('prom2mqtt').get('queries'):
            query_result_value = run_prom_query(query, config)
            client.publish(query.get('topic'), query_result_value)
        time.sleep(config.get('prom2mqtt').get('sleep'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Prometheus metrics to mqtt')
    parser.add_argument('--config', default='/etc/prom2mqtt/prom2mqtt.yml',
                        help='Path to the config file')

    args = parser.parse_args()
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    logging.info('Starting prom2mqtt...')
    main(args)
