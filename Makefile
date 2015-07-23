all: addons

sipreco.xmi: sipreco.zargo
	-echo "REBUILD sipreco.xmi from sipreco.zargo. I cant do it"

addons: sipreco

sipreco: sipreco.uml
	xmi2odoo -r -i $< -t . -v 2 -V 8.0

clean:
	sleep 1
	touch sipreco.uml
