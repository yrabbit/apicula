YOSYS ?= yosys
NEXTPNR ?= nextpnr-himbaechel

.DEFAULT_GOAL := all

all: \
	in-out-primer25k.fs

clean: 
	rm -f *.json *.fs *-unpacked.v
	
.PHONY: unpacked clean

# ============================================================
# TangPrimer25k
%-primer25k.fs: %-primer25k.json
	gowin_pack -e used-cells.pickle -d GW5A-25A -o $@ $<

%-primer25k.json: %-primer25k-synth.json primer25k.cst
	$(NEXTPNR) -v --debug --json $< --write $@ --device GW5A-LV25MG121NES --vopt cst=primer25k.cst

%-primer25k-synth.json: %.v
	$(YOSYS) -D LEDS_NR=6 -D OSC_TYPE_OSC -D INV_BTN=0 -D CPU_FREQ=27 -D BAUD_RATE=115200 -D NUM_HCLK=5 -p "read_verilog $^; synth_gowin -json $@ -family gw5a"

pll-nanolcd-primer25k-synth.json: pll/GW2A-18-dyn.vh pll-nanolcd/TOP.v pll-nanolcd/VGAMod.v
	$(YOSYS) -D INV_BTN=0 -p "read_verilog $^; synth_gowin -json $@ -family gw5a"

bsram-%-primer25k-synth.json: pll/GW2A-18-dyn.vh %-image-rom.v %-video-ram.v %.v
	$(YOSYS) -D INV_BTN=0 -p "read_verilog $^; synth_gowin -json $@ -family gw5a"

attosoc-%-synth.json: attosoc/attosoc.v attosoc/picorv32.v
	$(YOSYS) -D INV_BTN=0 -p "read_verilog $^; synth_gowin -json $@ -family gw5a"

dvi-example-primer25k-synth.json: DVI/dvi-example.v DVI/pll480.v DVI/tmds-channel.v
	$(YOSYS) -D INV_BTN=0 -D IS_ELVDS=0 -p "read_verilog -sv $^; synth_gowin -json $@ -family gw5a"

