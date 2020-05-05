My project for McPit to bridge tablet running pygame (and this code) to DCS-BIOS running on another computer.



Installation:

Edit  BIOSConfig.lua, add:
```
BIOS.protocol_io.UDPSender:create({ port = 7779, host = "127.0.0.1" }) // Insert IP address of tablet here
```

Run McPitCDU.py in python.

