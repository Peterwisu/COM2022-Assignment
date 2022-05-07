# COM2022 Computer Networking Assignment
## About this project

This is an COM2022 Computer Networking Assignment 2021/2022 by Wish Suharitdamrong in Group 19.

# Real time Video Broadcasting (RTVB)

RTVB is a protocol created on top of User Datagram protocol on Application layers.

## Requirement 
- Python version 3
- Source of Video 
  - WebCam
  - MP4 file

## Installation

To run a this script 

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install required libraries.

```bash
pip install numpy
pip install opencv-python
pip install imutils
```

## For MacOS 
To maximize a buffer size of UDP in MacOs 
```bash
sudo sysctl -w net.inet.udp.maxdgram=65535
```

## Usage

To run a Server
```bash
python3 UDPServer.py 
```

To run a Client
```bash
python3 UDPClient.py 
```


## Acknowledgement




## License
Wish Suharitdamrong 
