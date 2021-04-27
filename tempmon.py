#!/usr/bin/env python3
import traceback
import argparse
import collections
import pathlib

SENSOR_PATH = ''


class Sensor(collections.OrderedDict):
    def __init__(self, path):
        sp = super()
        sp.__init__(self)

        self._path = pathlib.Path(path)
        self.sys_name = self._path.name
        self.name = ''

        self._get_name()
        self._get_temps()


    def _get_name(self):
        name = self._path.joinpath('name')

        if name.exists():
            name = name.read_text()
            self.name = name.rstrip()


    def _get_temps(self):
        temps = list(self._path.glob('temp*_input'))
        if not temps: return

        temps.sort()
        for temp_item in temps:
            temp_name = temp_item.name
            temp_item = temp_item.read_text()
            temp_item = temp_item.rstrip()
            self[temp_name] = str(int(temp_item) / 1000)


    def to_zabbix_keys(self):
        items = []
        for key in self.keys():
            items.append('{"{#CPUNAME}":' + key + '}')

        return '{"data":[' + ','.join(items) + ']}'


class HWMons:
    def __init__(self):
        self._path = pathlib.Path('/sys/class/hwmon')
        self.sensors = []

        for item in self._path.iterdir():
            tmp = Sensor(item.absolute())

            if tmp:
                self.sensors.append(tmp)


    def show_sensors(self):
        for sensor in self.sensors:
            print('{} "{}"'.format(sensor.sys_name, sensor.name))
            for (key, val) in sensor.items():
                print('\t{}: {}'.format(key, val))


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', dest='detect', default=False, action='store_true')
    parser.add_argument('-k', dest='key', default='')
    return parser.parse_args()


if __name__ == "__main__":
    try:
        args = get_args()

        if args.detect:
            sensors = HWMons()
            sensors.show_sensors()
        
        elif args.key:
            cpu = Sensor(SENSOR_PATH)
            print(cpu.get(args.key))
        
        else:
            cpu = Sensor(SENSOR_PATH)
            print(cpu.to_zabbix_keys())

    except Exception:
        traceback.print_exc()
