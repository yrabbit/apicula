YOSYS ?= yosys
NEXTPNR ?= nextpnr-himbaechel

.DEFAULT_GOAL := all

all: \
	attosoc-tangnano9k.fs

unpacked:\
	attosoc-tangnano9k-unpacked.v

clean: 
	rm -f *.json *.fs *-unpacked.v
	
.PHONY: unpacked clean

# ============================================================
# Tangnano20k
%-tangnano20k.fs: %-tangnano20k.json
	gowin_pack -d GW2A-18C -o $@ $<

%-tangnano20k.json: %-tangnano20k-synth.json tangnano20k.cst
	$(NEXTPNR) --json $< --write $@ --device GW2AR-LV18QN88C8/I7 --vopt family=GW2A-18C --vopt cst=tangnano20k.cst

%-tangnano20k-synth.json: %.v
	$(YOSYS) -D LEDS_NR=6 -D OSC_TYPE_OSC -D INV_BTN=1 -D CPU_FREQ=27 -D BAUD_RATE=115200 -D NUM_HCLK=5 -p "read_verilog $^; synth_gowin -json $@ -family gw2a"

pll-nanolcd-tangnano20k-synth.json: pll/GW2A-18-dyn.vh pll-nanolcd/TOP.v pll-nanolcd/VGAMod.v
	$(YOSYS) -D INV_BTN=1 -p "read_verilog $^; synth_gowin -json $@ -family gw2a"

bsram-%-tangnano20k-synth.json: pll/GW2A-18-dyn.vh %-image-rom.v %-video-ram.v %.v
	$(YOSYS) -D INV_BTN=1 -p "read_verilog $^; synth_gowin -json $@ -family gw2a"

attosoc-tangnano20k-synth.json: attosoc/attosoc.v attosoc/picorv32.v
	$(YOSYS) -D INV_BTN=1 -p "read_verilog $^; synth_gowin -json $@ -family gw2a"

dvi-example-tangnano20k-synth.json: DVI/dvi-example.v DVI/pll480.v DVI/tmds-channel.v
	$(YOSYS) -D INV_BTN=1 -D IS_ELVDS=0 -p "read_verilog -sv $^; synth_gowin -json $@ -family gw2a"

# ============================================================
# TangPrimer20k
%-primer20k.fs: %-primer20k.json
	gowin_pack -d GW2A-18 -o $@ $<

%-primer20k.json: %-primer20k-synth.json primer20k.cst
	$(NEXTPNR) --json $< --write $@ --device GW2A-LV18PG256C8/I7 --vopt family=GW2A-18 --vopt cst=primer20k.cst

%-primer20k-synth.json: %.v
	$(YOSYS) -D LEDS_NR=6 -D OSC_TYPE_OSC -D INV_BTN=0 -D CPU_FREQ=27 -D BAUD_RATE=115200 -D NUM_HCLK=5 -p "read_verilog $^; synth_gowin -json $@ -family gw2a"

pll-nanolcd-primer20k-synth.json: pll/GW2A-18-dyn.vh pll-nanolcd/TOP.v pll-nanolcd/VGAMod.v
	$(YOSYS) -D INV_BTN=0 -p "read_verilog $^; synth_gowin -json $@ -family gw2a"

bsram-%-primer20k-synth.json: pll/GW2A-18-dyn.vh %-image-rom.v %-video-ram.v %.v
	$(YOSYS) -D INV_BTN=0 -p "read_verilog $^; synth_gowin -json $@ -family gw2a"

attosoc-%-synth.json: attosoc/attosoc.v attosoc/picorv32.v
	$(YOSYS) -D INV_BTN=0 -p "read_verilog $^; synth_gowin -json $@ -family gw2a"

dvi-example-primer20k-synth.json: DVI/dvi-example.v DVI/pll480.v DVI/tmds-channel.v
	$(YOSYS) -D INV_BTN=0 -D IS_ELVDS=0 -p "read_verilog -sv $^; synth_gowin -json $@ -family gw2a"

# ============================================================
# Tangnano (GW1N-1)
%-tangnano.fs: %-tangnano.json
	gowin_pack -d GW1N-1 -o $@ $^

%-tangnano.json: %-tangnano-synth.json tangnano.cst
	$(NEXTPNR) --json $< --write $@ --device GW1N-LV1QN48C6/I5 --vopt cst=tangnano.cst

%-tangnano-synth.json: %.v
	$(YOSYS) -D LEDS_NR=3 -D OSC_TYPE_OSCH -D INV_BTN=0 -D NUM_HCLK=2 -p "read_verilog $^; synth_gowin -json $@"

pll-nanolcd-tangnano-synth.json: pll/GW1N-1-dyn.vh pll-nanolcd/TOP.v pll-nanolcd/VGAMod.v
	$(YOSYS) -D INV_BTN=0 -p "read_verilog $^; synth_gowin -noalu -json $@"

bsram-%-tangnano-synth.json: pll/GW1N-1-dyn.vh %-image-rom.v %-video-ram.v %.v
	$(YOSYS) -D INV_BTN=0 -p "read_verilog $^; synth_gowin -json $@"

# ============================================================
# Tangnano1k (GW1NZ-1)
%-tangnano1k.fs: %-tangnano1k.json
	gowin_pack -d GW1NZ-1 -o $@ $^

%-tangnano1k.json: %-tangnano1k-synth.json tangnano1k.cst
	$(NEXTPNR) --json $< --write $@ --device GW1NZ-LV1QN48C6/I5 --vopt cst=tangnano1k.cst

%-tangnano1k-synth.json: %.v
	$(YOSYS) -D LEDS_NR=3 -D OSC_TYPE_OSCZ -D INV_BTN=0 -D NUM_HCLK=4 -p "read_verilog $^; synth_gowin -json $@"

pll-nanolcd-tangnano1k.fs: pll-nanolcd-tangnano1k.json
	gowin_pack -d GW1NZ-1 --sspi_as_gpio --mspi_as_gpio -o $@ $^

pll-nanolcd-tangnano1k-synth.json: pll/GW1NZ-1-dyn.vh pll-nanolcd/TOP.v pll-nanolcd/VGAMod.v
	$(YOSYS) -D INV_BTN=0 -p "read_verilog $^; synth_gowin -noalu -json $@"
	
bsram-%-tangnano1k-synth.json: pll/GW1NZ-1-dyn.vh %-image-rom.v %-video-ram.v %.v
	$(YOSYS) -D INV_BTN=0 -p "read_verilog $^; synth_gowin -json $@"

# ============================================================
# Tangnano4k (GW1NS-4)
%-tangnano4k.fs: %-tangnano4k.json
	gowin_pack -d GW1NS-4 --mspi_as_gpio -o $@ $^

%-tangnano4k.json: %-tangnano4k-synth.json tangnano4k.cst
	$(NEXTPNR) --json $< --write $@ --device GW1NSR-LV4CQN48PC7/I6 --vopt cst=tangnano4k.cst

%-tangnano4k-synth.json: %.v
	$(YOSYS) -D LEDS_NR=6 -D OSC_TYPE_OSCZ -D INV_BTN=0 -D FORCE_BRAM -D CPU_FREQ=27 -D BAUD_RATE=115200 -D NUM_HCLK=2 -p "read_verilog $^; synth_gowin -json $@"

%-pll-tangnano4k-synth.json: pll/GW1NS-4-dyn.vh %-pll-vr.v
	$(YOSYS) -D INV_BTN=0 -D LEDS_NR=6 -p "read_verilog $^; synth_gowin -json $@"
	

# ============================================================
# Tangnano9k (GW1N-9C)
%-tangnano9k.fs: %-tangnano9k.json
	gowin_pack -d GW1N-9C -o $@ $^

%-tangnano9k.json: %-tangnano9k-synth.json tangnano9k.cst
	$(NEXTPNR) --json $< --write $@ --device GW1NR-LV9QN88PC6/I5 --vopt family=GW1N-9C --vopt cst=tangnano9k.cst

%-tangnano9k-synth.json: %.v
	$(YOSYS) -D LEDS_NR=6 -D OSC_TYPE_OSC -D INV_BTN=0 -D CPU_FREQ=27 -D BAUD_RATE=115200 -D NUM_HCLK=5 -D HAS_FLASH608K -p "read_verilog $^; synth_gowin -json $@"

pll-nanolcd-tangnano9k-synth.json: pll/GW1N-9C-dyn.vh pll-nanolcd/TOP.v pll-nanolcd/VGAMod.v
	$(YOSYS) -D INV_BTN=0 -p "read_verilog $^; synth_gowin -json $@"

pll-nanolcd-tangnano9k.fs: pll-nanolcd-tangnano9k.json
	gowin_pack -d GW1N-9C --sspi_as_gpio --mspi_as_gpio -o $@ $^

bsram-%-tangnano9k-synth.json: pll/GW1N-9C-dyn.vh %-image-rom.v %-video-ram.v %.v
	$(YOSYS) -D INV_BTN=0 -p "read_verilog $^; synth_gowin -json $@"

dvi-example-tangnano9k-synth.json: DVI/dvi-example.v DVI/pll480.v DVI/tmds-channel.v
	$(YOSYS) -D INV_BTN=0 -D IS_ELVDS=1 -p "read_verilog -sv $^; synth_gowin -json $@"

# ============================================================
# szfpga miniboard (GW1N-9)
%-miniszfpga.fs: %-miniszfpga.json
	gowin_pack -d GW1N-9 -o $@ $<
 
%-miniszfpga.json: %-miniszfpga-synth.json miniszfpga.cst
	$(NEXTPNR) --json $< --write $@ --device GW1N-LV9QN48C6/I5 --vopt family=GW1N-9 --vopt cst=miniszfpga.cst

%-miniszfpga-synth.json: %.v
	$(YOSYS) -D LEDS_NR=4 -D OSC_TYPE_OSC -D INV_BTN=0 -D CPU_FREQ=50 -D BAUD_RATE=115200 -D NUM_HCLK=5 -p "read_verilog $^; synth_gowin -json $@"

blinky-pll-miniszfpga-synth.json: pll/GW1N-9-dyn.vh blinky-pll.v
	$(YOSYS) -D INV_BTN=0 -D LEDS_NR=4 -p "read_verilog $^; synth_gowin -json $@"

bsram-%-miniszfpga-synth.json: pll/GW1N-9-dyn.vh %-image-rom.v %-video-ram.v %.v
	$(YOSYS) -D INV_BTN=0 -p "read_verilog $^; synth_gowin -json $@"

# ============================================================
# szfpga (GW1N-9)
%-szfpga.fs: %-szfpga.json
	gowin_pack -d GW1N-9 -o $@ $<
 
%-szfpga.json: %-szfpga-synth.json szfpga.cst
	$(NEXTPNR) --json $< --write $@ --device GW1NR-LV9LQ144PC6/I5 --vopt family=GW1N-9 --vopt cst=szfpga.cst

%-szfpga-synth.json: %.v
	$(YOSYS) -D LEDS_NR=4 -D OSC_TYPE_OSC -D INV_BTN=0 -D CPU_FREQ=50 -D BAUD_RATE=115200 -D NUM_HCLK=5 -p "read_verilog $^; synth_gowin -json $@"

blinky-pll-szfpga-synth.json: pll/GW1N-9-dyn.vh blinky-pll.v
	$(YOSYS) -D INV_BTN=0 -D LEDS_NR=4 -p "read_verilog $^; synth_gowin -json $@"

bsram-%-szfpga-synth.json: pll/GW1N-9-dyn.vh %-image-rom.v %-video-ram.v %.v
	$(YOSYS) -D INV_BTN=0 -p "read_verilog $^; synth_gowin -json $@"

# ============================================================
# tec0117 (GW1N-9)
%-tec0117.fs: %-tec0117.json
	gowin_pack -d GW1N-9 -o $@ $<

%-tec0117.json: %-tec0117-synth.json tec0117.cst
	$(NEXTPNR) --json $< --write $@ --device GW1NR-LV9QN88C6/I5 --vopt family=GW1N-9 --vopt cst=tec0117.cst

%-tec0117-synth.json: %.v
	$(YOSYS) -D LEDS_NR=8 -D OSC_TYPE_OSC -D INV_BTN=0 -D CPU_FREQ=12 -D BAUD_RATE=115200 -D NUM_HCLK=5 -p "read_verilog $^; synth_gowin -json $@"

blinky-pll-tec0117-synth.json: pll/GW1N-9-dyn.vh blinky-pll.v
	$(YOSYS) -D INV_BTN=0 -D LEDS_NR=8 -p "read_verilog $^; synth_gowin -json $@"

# ============================================================
# runber (GW1N-4)
%-runber.fs: %-runber.json
	gowin_pack -d GW1N-4 -o $@ $<

%-runber.json: %-runber-synth.json runber.cst
	$(NEXTPNR) --json $< --write $@ --device GW1N-UV4LQ144C6/I5 --vopt cst=runber.cst

%-runber-synth.json: %.v
	$(YOSYS) -D LEDS_NR=8 -D OSC_TYPE_OSC -D INV_BTN=0 -D FORCE_BRAM -D CPU_FREQ=12 -D BAUD_RATE=115200 -D NUM_HCLK=5 -p "read_verilog $^; synth_gowin -json $@"

blinky-pll-runber-synth.json: pll/GW1N-4-dyn.vh blinky-pll.v
	$(YOSYS) -D INV_BTN=0 -D LEDS_NR=8 -p "read_verilog $^; synth_gowin -json $@"

# ============================================================
#  Upack
%-tangnano-unpacked.v: %-tangnano.fs
	gowin_unpack -d GW1N-1 -o $@ $^

%-tangnano1k-unpacked.v: %-tangnano1k.fs
	gowin_unpack -d GW1NZ-1 -o $@ $^
	
%-tangnano4k-unpacked.v: %-tangnano4k.fs
	gowin_unpack -d GW1NS-4 -o $@ $^

%-tangnano9k-unpacked.v: %-tangnano9k.fs
	gowin_unpack -d GW1N-9C -o $@ $^

%-tangnano20k-unpacked.v: %-tangnano20k.fs
	gowin_unpack -d GW2A-18C -o $@ $^

%-runber-unpacked.v: %-runber.fs
	gowin_unpack -d GW1N-4 -o $@ $^

%-tec0117-unpacked.v: %-tec0117.fs
	gowin_unpack -d GW1N-9 -o $@ $^

%-szfpga-unpacked.v: %-szfpga.fs
	gowin_unpack -d GW1N-9 -o $@ $^

%-primer20k-unpacked.v: %-primer20k.fs
	gowin_unpack -d GW2A-18 -o $@ $^

