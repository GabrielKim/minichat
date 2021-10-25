# Minichat

CLI Based Chatting Server/Client with only very basic features.

## Installations

1. Clone
```
$ git clone https://github.com/gabrielkim/minichat.git
$ cd minichat
```

2. (Optional) venv activate
```
$ pip install virtualenv (or) pip3 install virtualenv
$ virtualenv venv
$ source venv/bin/activate
```

3. Installing Requiments.txt
```
$ pip install -r requirements.txt
```

4. (Optional) Protobuf Build
```
$ chmod 755 setup_proto.sh
$ ./setup_proto.sh
```

## Running Guide

1. Run(Help mode)
```
$ cd minichat
$ python minichat.py -h
usage: minichat.py [-h] --type TYPE [--target TARGET]

An options for minichat.

optional arguments:
  -h, --help       show this help message and exit
  --type TYPE      This option is either 'Server' or 'Client'.
                   e.g> --type=Server
  --target TARGET  Enter IP and Port.
                   This option default value is 'localhost:0'.
                   The format is: <IP_Address>:<Port>
```

2. Run with Options
```
$ python minichat.py --type Server # with Server Mode
$ python minichat.py --type Client # with Client Mode
$ python minichat.py --type Server --target localhost:0 # with IP Address
```

3. Options details
```
Options:
	--type <TYPE> : This option to differentiate between Server and Client. Required option.
	--target <TARGET> : It means the connection IP address and port of Server and Client. Only IPv4 is supported, default is localhost:0 . The format is "<ipadress>:<port>".
```

## Short User Guide

### Options for client

-  /all : Message for all.
-  /chanlist : View All channel list.
-  /join (channel) : Join the channel. e.g> /join dhkim
-  /leave (channel) : Leave the channel. e.g> /leave dhkim
-  /userlist : Get a list of users of the currently connected channel.
