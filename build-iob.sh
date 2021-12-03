#!/bin/sh
if [ $# -lt 1 ] ; then
	echo "Usage: biod-iob.sh TOP-DIR"
	exit 1
fi
TOP_DIR=$1
ORIG_PWD=${PWD}
for DIR in $(find ${TOP_DIR} -type d -depth 1); do
	# extract the partnumber
	PARTNUMBER=$(sed -n -e 's/[[:space:]]*set_device[[:space:]]*//p' <${DIR}/run.tcl)
	# device
	DEVICE=$(echo ${PARTNUMBER} | sed -n -e 's/\(GW[[:digit:]]N.*-\)[[:alpha:]][[:alpha:]]\([[:digit:]]\).*/\1\2/p')
	cd ${DIR}
	${YOSYS=yosys} -p "synth_gowin -json synth.json" top.v 
	${NEXTPNR=nextpnr-gowin} --json synth.json --write pnr.json --device ${PARTNUMBER} --cst top.cst
	gowin_pack -d ${DEVICE} -o top.fs pnr.json
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
