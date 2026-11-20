default: launch

launch: image
	mkdir -p ha-config
	podman run \
		--replace \
		--name ha-dev \
		-p 127.0.0.1:8123:8123 \
		-v $$(pwd)/ha-config:/config:Z \
		-v $$(pwd)/custom_components/serial_transceiver:/config/custom_components/serial_transceiver \
		-d ha-dev
	podman exec -ti ha-dev bash -c "socat -d -d PTY,link=/dev/ttyACM0,raw,echo=0 STDIO"

image:
	podman build -t ha-dev .

diff:
	giff origin/main

logs:
	while true; do podman logs -f ha-dev; done