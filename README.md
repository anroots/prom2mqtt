# prom2mqtt

Run [Prometheus][] queries and send resulting values to a MQTT server.

prom2mqtt is a simple bridge to pass data held by Prometheus into MQTT.

## Install

Install is tested with Ansible on Raspberry Pi. Should work on any Debian based Linux env w/ Python3.

- Copy repo source
- Install dependencies (or create venv)
```
pip3 install -r requirements.txt
```
- Create config file (use provided `prom2mqtt.yml` as sample)
- Start `prom2mqtt`
```
python3 prom2mqtt --config /path/to/prom2mqtt.yml
```

Sample Systemd unit file is in `prom2mqtt.service`. Sample Ansible task list for deployment is
in `ansible.sample.yml`.

## Development

Local development environment with `venv`. A passwordless MQTT server can be run with `docker-compose`
for testing.

## License

MIT license.

[Prometheus]: https://prometheus.io/
[MQTT]: https://mqtt.org/
