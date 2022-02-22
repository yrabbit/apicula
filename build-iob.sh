#!/bin/sh
if [ $# -lt 1 ]; then
	echo "Usage: biod-iob.sh TOP-DIR [force-rebuild]"
	exit 1
fi
FORCE_REBUILD=0
if [ $# -ge 2 ]; then
	FORCE_REBUILD=1
fi
TOP_DIR=$1
ORIG_PWD=${PWD}
for DIR in $(find ${TOP_DIR} -type d -depth 1); do
	# extract the partnumber
	PNUMBER=$(sed -n -e 's/[[:space:]]*set_device[[:space:]]*//p' <${DIR}/run.tcl)
	PNUMBER_1=$(echo ${PNUMBER}|sed -n -e 's/-name[[:space:]].*[[:space:]]//p')
	FAMILY=$(echo ${PNUMBER}|sed -n -e 's/.*-name[[:space:]]\(.*\)[[:space:]].*/\1/p')
	if [ "x${PNUMBER_1}" != "x" ]; then
		PNUMBER=${PNUMBER_1}
	fi
	# device
	DEVICE=$(echo ${PNUMBER} | sed -n -e 's/\(GW[[:digit:]]N.*-\)[[:alpha:]][[:alpha:]]\([[:digit:]]\).*/\1\2/p')
	DEVICE=$(echo ${DEVICE}|sed -e 's/R//')
	cd ${DIR}
	FAMILY_KEY=""
	if [ "x${FAMILY}" != "x" ]; then
		FAMILY_KEY="--family ${FAMILY}"
	fi
	if [ ! -r pnr.json -o ${FORCE_REBUILD} -eq 1 ]; then
		${YOSYS=yosys} -p "read_verilog top.v; synth_gowin -json synth.json"  
		${NEXTPNR=nextpnr-gowin} --json synth.json --write pnr.json ${FAMILY_KEY} --device ${PNUMBER} --cst top.cst
	fi
	echo ${DIR} ${DEVICE} ${PNUMBER} gowin_pack
	if [ "x${FAMILY}" != "x" ]; then
		gowin_pack -d ${FAMILY} -o top.fs pnr.json
	else
		gowin_pack -d ${DEVICE} -o top.fs pnr.json
	fi
	if [ ! -f top.fs ]; then
		exit 3
	fi
done
cd ${ORIG_PWD}

echo 'Sanity check...'
for DIR in $(find ${TOP_DIR} -type d -depth 1); do
	if [ ! -f ${DIR}/top.fs ]; then
		echo "No image in ${DIR}!"
	fi
done
