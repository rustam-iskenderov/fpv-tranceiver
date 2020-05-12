# fpv-tranceiver
Ultra low latency video streaming for FPV drones via 3G/4G network

## Basic setup:

Clone sources to each machine by running the command in terminal
```shell
$ git clone https://github.com/rustam-iskenderov/fpv-tranceiver.git
```
### Server (Windows / Linux)
	* Verify that your server has public IP address and can be accessible from the internet
	* Create port forwarding for the ports: 20000, 20001, 20005, 20006 UDP
	* Run server.py

### Drone ( Raspberry Pi )
	* Verify that camera is working ( https://www.raspberrypi.org/documentation/configuration/camera.md )
	* Open globals.py and replace the server_ip value with public ip of your server
	* Run clientDrone.py
	
### Operator ( Windows only )
	* Install gstreamer with ALL plugins(https://gstreamer.freedesktop.org/)
	* Open clientOperator.py and replace the gstreamer_bin_path value with a path to gstreamer bin folder
	* Open globals.py and replace the server_ip value with public ip of your server
	* Run clientOperator.py
	* Type 'start' and press Enter to start live streaming
	* Live video stream should show up
	* Type 'stop' and press Enter to stop live streaming
	
## Setup #2, Operator has public IP address:	
	* Open globals.py and replace the server_ip value with a local ip of your server
	* Run server.py and clientOperator.py on the same machine
