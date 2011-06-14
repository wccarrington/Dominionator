#!/usr/bin/env python

import cPickle, struct

def send(output, value):
    data = cPickle.dumps(value)
    d = struct.pack('>i',len(data))+data
    output.write(d)
    output.flush()

def recv(input):
    n_s = input.read(4)
    if len(n_s) == 0:
        raise KeyboardInterrupt()
    n = struct.unpack('>i', n_s)[0]
    data_s = input.read(n)
    data = cPickle.loads(data_s)
    return data

