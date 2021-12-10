import re
import os
import sys
import tempfile
import subprocess
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
from shutil import copytree

from apycula import codegen
from apycula import bslib
from apycula import pindef
from apycula import tiled_fuzzer
from apycula import fuse_h4x
#TODO proper API
#from apycula import dat19_h4x
from apycula import tm_h4x
from apycula import chipdb

gowinhome = os.getenv("GOWINHOME")
if not gowinhome:
    raise Exception("GOWINHOME not set")

AttrValues = namedtuple('ModeAttr', [
    'allowed_modes',    # allowed modes for the attribute
    'values',           # values of the attribute
    'table',            # special values table
    ])

drive_iostd = {
        "":          ["4", "8", "12"],
        "LVCMOS33":  ["4", "8", "12", "16", "24"],
        "LVCMOS25":  ["4", "8", "12", "16"],
        "LVCMOS18":  ["4", "8", "12"],
        "LVCMOS15":  ["4", "8"],
        "HSTL15_I":  ["8"],
        "HSTL18_I":  ["8"],
        "HSTL18_II": ["8"],
        "SSTL15":    ["8"],
        "SSTL18_I":  ["8"],
        "SSTL18_II": ["8"],
        "SSTL25_I":  ["8"],
        "SSTL25_II": ["8"],
        "SSTL33_I":  ["8"],
        "SSTL33_II": ["8"],
        "PCI33":     ["4", "8"],
        }

open_drain_iostd = {
            "",
            "LVCMOS15",
            "LVCMOS18",
            "LVCMOS25",
            "LVCMOS33",
        }

hysteresis_iostd = {
            "",
            "LVCMOS15",
            "LVCMOS18",
            "LVCMOS25",
            "LVCMOS33",
            "PCI33",
        }

iobattrs_0 = ("DRIVE",      AttrValues(["OBUF", "IOBUF"], None, drive_iostd))
iobattrs_1 = ("HYSTERESIS", AttrValues(["IBUF", "IOBUF"], ["NONE", "L2H", "H2L", "HIGH"], hysteresis_iostd))
iobattrs_2 = ("OPEN_DRAIN", AttrValues(["OBUF", "IOBUF"], ["ON", "OFF"], open_drain_iostd))

def make_test(locations):
    for iostd in tiled_fuzzer.iostandards:
        for ttyp, tiles in locations.items(): # for each tile of this type
            locs = tiles.copy()
            mod = codegen.Module()
            cst = codegen.Constraints()
            # get bels in this ttyp
            bels = {name[-1] for loc in tiles.values() for name in loc}
            for pin in bels: # [A, B, C, D, ...]
                # level 0
                attr_0, attr_values_0 = iobattrs_0
                if iostd not in attr_values_0.table:
                    continue
                attr_vals_0 = attr_values_0.values
                if attr_vals_0 == None:
                    attr_vals_0 = attr_values_0.table[iostd]
                for attr_val_0 in attr_vals_0:   # each value of the attribute
                    attr_1, attr_values_1 = iobattrs_1
                    attr_vals_1 = [None]
                    if iostd in attr_values_1.table:
                        attr_vals_1 = attr_values_1.values
                        if not attr_vals_1:
                            attr_vals_1 = attr_values_1.table[iostd]
                    for attr_val_1 in attr_vals_1:   # each value of the attribute
                        attr_2, attr_values_2 = iobattrs_2
                        attr_vals_2 = [None]
                        if iostd in attr_values_2.table:
                            attr_vals_2 = attr_values_2.values
                            if not attr_vals_2:
                                attr_vals_2 = attr_values_2.table[iostd]
                        for attr_val_2 in attr_vals_2:   # each value of the attribute
                            for typ, conn in tiled_fuzzer.iobmap.items():
                                val_0 = attr_val_0
                                val_1 = attr_val_1
                                val_2 = attr_val_2

                                # skip illegal atributesa for mode
                                if typ not in attr_values_0.allowed_modes:
                                    val_0 = None
                                if typ not in attr_values_1.allowed_modes:
                                    val_1 = None
                                if typ not in attr_values_2.allowed_modes:
                                    val_2 = None
                                if not val_0 and not val_1 and not val_2:
                                    continue

                                # find the next location that has pin
                                # or make a new module
                                loc = tiled_fuzzer.find_next_loc(pin, locs)
                                if (loc == None):
                                    yield tiled_fuzzer.Fuzzer(ttyp, mod, cst, {}, iostd)
                                    locs = tiles.copy()
                                    mod = codegen.Module()
                                    cst = codegen.Constraints()
                                    loc = tiled_fuzzer.find_next_loc(pin, locs)

                                name = tiled_fuzzer.make_name("IOB", typ)
                                iob = codegen.Primitive(typ, name)
                                for port in chain.from_iterable(conn.values()):
                                    iob.portmap[port] = name+"_"+port

                                for direction, wires in conn.items():
                                    wnames = [name+"_"+w for w in wires]
                                    getattr(mod, direction).update(wnames)
                                    if direction in ["inputs", "outputs", "inouts"]:
                                        cst_name = wnames[0]
                                mod.primitives[name] = iob
                                # complex iob. connect OEN and O
                                if typ == "IOBUF":
                                    iob.portmap["OEN"] = name + "_O"
                                # port attribute value
                                cst.ports[cst_name] = loc
                                cst.attrs[cst_name] = {}
                                if val_0:
                                    cst.attrs[cst_name].update({attr_0: val_0})
                                if val_1:
                                    cst.attrs[cst_name].update({attr_1: val_1})
                                if val_2:
                                    cst.attrs[cst_name].update({attr_2: val_2})
                                if iostd:
                                    cst.attrs[cst_name].update({"IO_TYPE": iostd})
            yield tiled_fuzzer.Fuzzer(ttyp, mod, cst, {}, iostd)

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

# Result of the vendor router-packer run
PnrResult = namedtuple('PnrResult', [
    'constrs',          # port constraints
    'dir'               # test directory
    ])

def run_pnr(mod, constr, config):
    cfg = codegen.DeviceConfig({
        "use_jtag_as_gpio"      : "1",
        "use_sspi_as_gpio"      : "1",
        "use_mspi_as_gpio"      : "1",
        "use_ready_as_gpio"     : "1",
        "use_done_as_gpio"      : "1",
        "use_reconfign_as_gpio" : "1",
        "use_mode_as_gpio"      : "1",
        "use_i2c_as_gpio"       : "1",
        "bit_crc_check"         : "1",
        "bit_compress"          : "0",
        "bit_encrypt"           : "0",
        "bit_security"          : "1",
        "bit_incl_bsram_init"   : "0",
        "loading_rate"          : "250/100",
        "spi_flash_addr"        : "0x00FFF000",
        "bit_format"            : "txt",
        "bg_programming"        : "off",
        "secure_mode"           : "0"})

    opt = codegen.PnrOptions({
        "gen_posp"          : "1",
        "gen_io_cst"        : "1",
        "gen_ibis"          : "1",
        "ireg_in_iob"       : "0",
        "oreg_in_iob"       : "0",
        "ioreg_in_iob"      : "0",
        "timing_driven"     : "0",
        "cst_warn_to_error" : "0"})
    pnr = codegen.Pnr()
    pnr.device = tiled_fuzzer.device
    pnr.partnumber = tiled_fuzzer.params['partnumber']
    pnr.opt = opt
    pnr.cfg = cfg

    try:
        os.mkdir(f'/home/rabbit/tmp/bench-{tiled_fuzzer.device}')
    except FileExistsError:
        pass
    tmpdir = tempfile.mkdtemp(dir = f'/home/rabbit/tmp/bench-{tiled_fuzzer.device}')
    pnr.outdir = tmpdir
    with open(tmpdir+"/top.v", "w") as f:
        mod.write(f)
    pnr.netlist = tmpdir+"/top.v"
    with open(tmpdir+"/top.cst", "w") as f:
        constr.write(f)
    pnr.cst = tmpdir+"/top.cst"
    with open(tmpdir+"/run.tcl", "w") as f:
        pnr.write(f)

    subprocess.run([gowinhome + "/IDE/bin/gw_sh", tmpdir+"/run.tcl"], cwd = tmpdir)
    try:
        return PnrResult(constr, tmpdir)
    except FileNotFoundError:
        print(tmpdir)
        input()
        return None


# module + constraints + config
DataForPnr = namedtuple('DataForPnr', ['modmap', 'cstmap', 'cfgmap'])

if __name__ == "__main__":
    with open(f"{gowinhome}/IDE/share/device/{tiled_fuzzer.device}/{tiled_fuzzer.device}.fse", 'rb') as f:
        fse = fuse_h4x.readFse(f)

    with open(f"{tiled_fuzzer.device}.json") as f:
        dat = json.load(f)

    with open(f"{gowinhome}/IDE/share/device/{tiled_fuzzer.device}/{tiled_fuzzer.device}.tm", 'rb') as f:
        tm = tm_h4x.read_tm(f, tiled_fuzzer.device)

    db = chipdb.from_fse(fse)
    db.timing = tm
    db.packages, db.pinout, db.pin_bank = chipdb.json_pinout(tiled_fuzzer.device)

    locations = {}
    for row, row_dat in enumerate(fse['header']['grid'][61]):
        for col, typ in enumerate(row_dat):
            locations.setdefault(typ, []).append((row, col))

    pin_names = pindef.get_locs(tiled_fuzzer.device, tiled_fuzzer.params['package'], True)
    edges = {'T': fse['header']['grid'][61][0],
             'B': fse['header']['grid'][61][-1],
             'L': [row[0] for row in fse['header']['grid'][61]],
             'R': [row[-1] for row in fse['header']['grid'][61]]}
    pin_locations = {}
    pin_re = re.compile(r"IO([TBRL])(\d+)([A-Z])")
    for name in pin_names:
        side, num, pin = pin_re.match(name).groups()
        ttyp = edges[side][int(num)-1]
        ttyp_pins = pin_locations.setdefault(ttyp, {})
        ttyp_pins.setdefault(name[:-1], set()).add(name)

    # Add fuzzers here
    fuzzers = chain(
        make_test(pin_locations),
    )

    # Only combine modules with the same IO standard
    pnr_data = {}
    for fuzzer in fuzzers:
        pnr_data.setdefault(fuzzer.iostd, DataForPnr({}, {}, {}))
        pnr_data[fuzzer.iostd].modmap.setdefault(fuzzer.ttyp, []).append(fuzzer.mod)
        pnr_data[fuzzer.iostd].cstmap.setdefault(fuzzer.ttyp, []).append(fuzzer.cst)
        pnr_data[fuzzer.iostd].cfgmap.setdefault(fuzzer.ttyp, []).append(fuzzer.cfg)

    modules = []
    constrs = []
    configs = []
    for data in pnr_data.values():
        modules += [reduce(lambda a, b: a+b, m, codegen.Module())
                    for m in zip_longest(*data.modmap.values(), fillvalue=codegen.Module())]
        constrs += [reduce(lambda a, b: a+b, c, codegen.Constraints())
                    for c in zip_longest(*data.cstmap.values(), fillvalue=codegen.Constraints())]
        configs += [reduce(lambda a, b: {**a, **b}, c, {})
                    for c in zip_longest(*data.cfgmap.values(), fillvalue={})]

    p = Pool()
    pnr_res = p.imap_unordered(lambda param: run_pnr(*param), zip(modules, constrs, configs), 4)
    for pnr in pnr_res:
        dval = (pnr.constrs.ports, pnr.constrs.attrs)
        with open(f'{pnr.dir}/attrs.json', 'w') as f:
            json.dump(dval, f)

