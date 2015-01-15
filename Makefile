all: addons

design/sipreco.xmi: design/sipreco.zargo
	-echo "REBUILD sipreco.xmi from sipreco.zargo. I cant do it"

addons: sipreco

sipreco: design/sipreco.uml
	xmi2odoo -r -i $< -t addons -v 2 -V 8.0

clean:
	sleep 1
	touch design/sipreco.uml
