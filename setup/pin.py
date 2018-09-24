#!/usr/bin/env python
# -*- coding: utf-8 -*-

gpio_path = '/sys/class/gpio/'
export_file = gpio_path +'export'
unexport_file = gpio_path +'unexport'
direction_file = gpio_path + 'gpio{}/direction'
value_file = gpio_path +'gpio{}/value' 

class GPIO:
    def __init__(self, pin, export=True):
        if not (type(pin) is int):
            raise TypeError('"pin" mast be int')
        if pin < 0 or pin > 125:
            raise ValueError('Incorrect pin number')
        self.pin = pin
        self.inverted = False
        self.export = export
        if export:
            self.export()

    def export(self):
        print('Exporting pin GPIO{}'.format(pin))
        try:
            export = open(export_file, 'w')
            export.write(str(self.pin))
            export.close()
        except IOError as (errno, strerror):
            if errno == 16:
                pass
            else:
                raise IOError(errno, strerror)
        self.set_dir('in')        

    def set_dir(self, dir):
        if dir == 'in' or dir == 'out':
            direction = open(direction_file.format(self.pin), 'w')
            direction.write(dir)
            direction.close()
        else:
             raise ValueError('Only in/out accepted')
    def get_dir(self):
        direction = open(direction_file.format(self.pin), 'r')
        dir = direction.read()
        direction.close()
        return dir.strip()

    def get_val(self):
        value = open(value_file.format(self.pin), 'r')
        val = value.read()
        value.close()
        val = bool(int(val.strip()))
        return int(val != self.inverted)

    def set_val(self, v):
        if type(v) is int:
            if v != 0:
                val = True
            else:
                val = False
        elif type(v) is bool:
            val = v
        elif type(v) is str:
            if v == '0':
                val = False
            elif v == '1':
                val = True
            else:
                 raise ValueError('Only 1/0 accepted')

        value = open(value_file.format(self.pin), 'w')
        value.write(str(int(val != self.inverted)))
        value.close()

    def __str__(self):
        return 'GPIO{}:\tdir={}\tval={}'.format(
            self.pin,
            self.get_dir(), 
            self.get_val())

    def __del__(self):
        if self.export:
            print('Unexporting pin GPIO{}'.format(self.pin))
            self.set_dir('in')
            unexport = open(unexport_file, 'w')
            unexport.write(str(self.pin))
            unexport.close()
