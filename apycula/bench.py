import re
import os
import sys
import tempfile
import subprocess
import importlib.resources
from collections import deque, Counter, namedtuple
from itertools import chain, count, zip_longest
from functools import reduce
from random import shuffle, seed
from warnings import warn
from math import factorial
import numpy as np
from multiprocessing.dummy import Pool
import pickle
import json
from wirenames import wirenames, clknames
from PIL import Image, ImageDraw
from shutil import copytree

from apycula import codegen
from apycula import bslib
from apycula import pindef
from apycula import fuse_h4x
from apycula import gowin_pack
from apycula import tiled_fuzzer
from apycula import codegen
from apycula import bslib
#TODO proper API
#from apycula import dat19_h4x
from apycula import tm_h4x
from apycula import chipdb

gowinhome = os.getenv("GOWINHOME")
if not gowinhome:
    raise Exception("GOWINHOME not set")

# device = os.getenv("DEVICE")
device = sys.argv[1]

params = {
    "GW1NS-2": {
        "package": "LQFP144",
        "device": "GW1NS-2C-LQ144-5",
        "partnumber": "GW1NS-UX2CLQ144C5/I4",
    },
    "GW1N-9": {
        "package": "PBGA256",
        "device": "GW1N-9-PBGA256-6",
        "partnumber": "GW1N-LV9PG256C6/I5",
    },
    "GW1N-4": {
        "package": "PBGA256",
        "device": "GW1N-4-PBGA256-6",
        "partnumber": "GW1N-LV4PG256C6/I5",
    },
    "GW1N-1": {
        "package": "LQFP144",
        "device": "GW1N-1-LQFP144-6",
        "partnumber": "GW1N-LV1LQ144C6/I5",
    },
}[device]

# collect all routing bits of the tile
_route_mem = {}
def route_bits(db, row, col):
    mem = _route_mem.get((row, col), None)
    if mem != None:
        return mem

    bits = set()
    for w in db.grid[row][col].pips.values():
        for v in w.values():
            bits.update(v)
    _route_mem.setdefault((row, col), bits)
    return bits

def get_fuse_num(ttyp, bits):
    # bits YYXX
    for i, fs in enumerate(fse['header']['fuse'][1]):
        if fs[ttyp] == bits:
            return i
    return -1

def print_longval(ttyp, table, contains = None, must_all = False):
    "ttyp, num, contains = 0"
    for row in fse[ttyp]['longval'][table]:
        if contains == None:
            print(row)
        else:
            are_all = must_all
            for val in contains:
                if val in row[16:]:
                    are_all = True
                    if not must_all:
                        break
                else:
                    if must_all:
                        are_all = False
                        break
            if are_all:
                print(row)

def print_longval_key(ttyp, table, key, ignore_key_elem = 0, zeros = True):
    if zeros:
        sorted_key = (sorted(key) + [0] * 16)[:16 - ignore_key_elem]
        end = 16
    else:
        sorted_key = sorted(key)
        end = ignore_key_elem + len(sorted_key)
    for rec in fse[ttyp]['longval'][table]:
        k = rec[ignore_key_elem:end]
        if k == sorted_key:
            print(rec)

def print_alonenode(ttyp, contains = 0):
    "ttyp, contains = 0"
    for row in fse[ttyp]['alonenode'][69]:
        if contains == 0 or contains in row:
            print(row)

def get_wires_to(fse, ttyp, wiren):
    for wr in [wire for wire in fse[ttyp]['wire'][2] if wire[1] == wiren]:
        print(wr)

def get_wires_from(fse, ttyp, wiren):
    for wr in [wire for wire in fse[ttyp]['wire'][2] if wire[0] == wiren]:
        print(wr)

def get_grid_rc(fse, row, col):
    grow = 0
    h = fse[fse['header']['grid'][61][row][col]]['height']
    while row:
        grow += h
        h = fse[fse['header']['grid'][61][row][col]]['height']
        row -= 1
    gcol = 0
    w = fse[fse['header']['grid'][61][row][col]]['width']
    while col:
        gcol += w
        w = fse[fse['header']['grid'][61][row][col]]['width']
        col -= 1
    return (grow, gcol, h, w)

def pict(bm, name):
    im = bslib.display(None, bm)
    im_scaled = im.resize((im.width * 10, im.height * 10), Image.NEAREST)
    im_scaled.save(f"/home/rabbit/tmp/{name}")

def deep_bank_cmp(bel, ref_bel):
    keys = set(bel.bank_flags.keys())
    ref_keys = set(ref_bel.bank_flags.keys())
    if keys != ref_keys:
        print(f' keys diff:{keys ^ ref_keys}')
        return
    for key, val in bel.bank_flags.items():
        if val != ref_bel.bank_flags[key]:
            print(f' val diff: {key}:{val} vs {ref_bel.bank_flags[key]}')

def deep_io_cmp(bel, ref_bel, irow, icol, ibel):
    iostd_keys = set(bel.iob_flags.keys())
    ref_iostd_keys = set(ref_bel.iob_flags.keys())
    if iostd_keys != ref_iostd_keys:
        print(f' iostd diff:{iostd_keys ^ ref_iostd_keys}')
    for iostd_key, typ_rec in bel.iob_flags.items():
        ref_typ_rec = ref_bel.iob_flags[iostd_key]
        if set(typ_rec.keys()) != set(ref_typ_rec.keys()):
            print(f' type diff:{iostd_key} {set(typ_rec.keys()) ^ set(ref_typ_rec.keys())}')
            continue
        if typ_rec == ref_typ_rec:
            continue
        print(f' {iostd_key}')
        for typ_key, flag_rec in typ_rec.items():
            ref_flag_rec = ref_typ_rec[typ_key]
            if set(flag_rec.flags.keys()) != set(ref_flag_rec.flags.keys()):
                print(f'  flag diff:{iostd_key} {typ_key} {set(flag_rec.flags.keys()) ^ set(ref_flag_rec.flags.keys())}')
                continue
            if flag_rec == ref_flag_rec:
                continue;
            print(f'  {typ_key}')
            if flag_rec.encode_bits != ref_flag_rec.encode_bits:
                print(f'  encode diff:({irow}, {icol})[{ibel}] {iostd_key} {typ_key} {flag_rec.encode_bits ^ ref_flag_rec.encode_bits}')
            for flag_key, opt_rec in flag_rec.flags.items():
                ref_opt_rec = ref_flag_rec.flags[flag_key]
                if set(opt_rec.options.keys()) != set(ref_opt_rec.options.keys()):
                    print(f'   opt diff:{iostd_key} {typ_key} {flag_key} {set(opt_rec.options.keys()) ^ set(ref_opt_rec.options.keys())}')
                    continue
                if opt_rec == ref_opt_rec:
                    continue
                print(f'   {flag_key}')
                for opt_key, bits in opt_rec.options.items():
                    ref_bits = ref_opt_rec.options[opt_key]
                    if bits != ref_bits:
                        print(f'    bits diff:{iostd_key} {typ_key} {flag_key} {opt_key} {bits} vs {ref_bits}')


def tbrl2rc(fse, side, num):
    if side == 'T':
        row = 0
        col = int(num) - 1
    elif side == 'B':
        row = len(fse['header']['grid'][61])-1
        col = int(num) - 1
    elif side == 'L':
        row = int(num) - 1
        col = 0
    elif side == 'R':
        row = int(num) - 1
        col = len(fse['header']['grid'][61][0])-1
    return (row, col)

def attrs2log(attrs, pos):
    for name, p in attrs[0].items():
        if p == pos:
            return f'{pos}:{attrs[1][name]}:{name}'

if __name__ == "__main__":
    with open(f"{gowinhome}/IDE/share/device/{device}/{device}.fse", 'rb') as f:
        fse = fuse_h4x.readFse(f)

    with open(f"{device}.json") as f:
        dat = json.load(f)

    with open(f"{gowinhome}/IDE/share/device/{device}/{device}.tm", 'rb') as f:
        tm = tm_h4x.read_tm(f, device)

    with open(f"/home/rabbit/src/apicula/apycula/{device}.pickle", "rb") as f:
        db = pickle.load(f)
    #with open(f"/home/rabbit/var/fpga/bases-new-ide-site/{device}.pickle", "rb") as f:
    #    ref_db = pickle.load(f)

    import ipdb; ipdb.set_trace()
    img = bslib.read_bitstream(f'{sys.argv[2]}')[0]
    bm = chipdb.tile_bitmap(db, img)

    row = 5
    col = 19
    ttyp = fse['header']['grid'][61][row][col]

    rbits = route_bits(db, row, col)
    r, c = np.where(bm[(row, col)] == 1)
    tile = set(zip(r, c))
    bits = tile - rbits
    for df in bits:
        print(get_fuse_num(ttyp, df[0] * 100 + df[1]), end = ' ')
    print(bits)

    import ipdb; ipdb.set_trace()
