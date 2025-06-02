import sys
import os
import re
import pickle
import gzip
import itertools
import math
import json
import argparse
import importlib.resources
from collections import namedtuple
from contextlib import closing
from apycula import codegen
from apycula import chipdb
from apycula.chipdb import add_attr_val, get_shortval_fuses, get_longval_fuses, get_bank_fuses, get_long_fuses
from apycula import attrids
from apycula import bslib
from apycula import bitmatrix
from apycula.wirenames import wirenames, wirenumbers
from deepdiff import DeepDiff

db_new = None
db_old = None

def main(device):
    global db_new
    global db_old

    old_path = sys.argv[1]
    new_path = sys.argv[2]

    print(f'Compare {device}...')
    path = f'{old_path}/{device}.pickle'
    with closing(gzip.open(path, 'rb')) as f:
        db_old = pickle.load(f)

    path = f'{new_path}/{device}.pickle'
    with closing(gzip.open(path, 'rb')) as f:
        db_new = pickle.load(f)

    # checks
    for name, old, new in [
            ('Chip flags',  db_old.chip_flags, db_new.chip_flags),
            ('Extra func',  db_old.extra_func, db_new.extra_func),
            ('HCLK pips',   db_old.hclk_pips, db_new.hclk_pips),
            ('Diff IO types',  db_old.diff_io_types, db_new.diff_io_types),
            ('Tile types',  db_old.tile_types, db_new.tile_types),
            ('Pad PLL',  db_old.pad_pll, db_new.pad_pll),
            ('Simplio rows',  db_old.simplio_rows, db_new.simplio_rows),
            ('Botom IO',  db_old.bottom_io, db_new.bottom_io),
            ('Nodes',  db_old.nodes, db_new.nodes),
            ('Longval',  db_old.longval, db_new.longval),
            ('Shortval',  db_old.shortval, db_new.shortval),
            ('Long fuses',  db_old.longfuses, db_new.longfuses),
            ('Logicinfo',  db_old.logicinfo, db_new.logicinfo),
            ('Pin bank',  db_old.pin_bank, db_new.pin_bank),
            ('Pinout',  db_old.pinout, db_new.pinout),
            ('Packages',  db_old.packages, db_new.packages),
            ('Wire delay',  db_old.wire_delay, db_new.wire_delay),
            ('Timing',  db_old.timing, db_new.timing),
            ('Grid',  db_old.grid, db_new.grid),
            ]:
        diff = DeepDiff(old, new)
        if diff:
            print(f'{name}: DIFF')
            if False and name == 'Grid':
                for diff_r, diff_d in diff.items():
                    print(diff_r, ':', diff_d)
        else:
            print(f'{name}: Ok')
    import ipdb; ipdb.set_trace()

if __name__ == '__main__':
    old_path = sys.argv[1]
    new_path = sys.argv[2]
    print(f'Compare old bases:{old_path} with new bases:{new_path}')
    #for device in ['GW1N-1', 'GW2A-18C']:
    for device in [sys.argv[3]]:
    #for device in ['GW2A-18C']:
        main(device)
        print()
