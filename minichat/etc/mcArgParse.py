#-*- coding: utf-8 -*-

from argparse import Namespace, RawTextHelpFormatter
import argparse

import re

class mcArgParser(object):
    def __init__(self) -> None:
        super().__init__()

        self.__host = 'localhost'
        self.__port = '12345'
        self.__address = '{}:'.format(self.__host) + self.__port

    def _checkVaildIPAddress(self, ipaddr: str) -> bool:
        # references : 
        # https://somjang.tistory.com/entry/leetCode-468-Validate-IP-Address-Python
        # https://www.geeksforgeeks.org/python-program-to-find-the-type-of-ip-address-using-regex/
        # https://gist.github.com/mnordhoff/2213179
        # for ipv4
        _ipv4re = '^(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\\.){3}(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$'

        if re.search(_ipv4re, ipaddr) is None:
            print("Invalid IPv4 format. \'{}\'".format(ipaddr))
            return False
        return True

    def argParse(self) -> Namespace:
        _argParser = argparse.ArgumentParser(description='An options for minichat.', formatter_class=RawTextHelpFormatter)

        _argParser.add_argument('--type', required=True, type=str,
        help="This option is either \'Server\' or \'Client\'.\n"
                "e.g> --type=Server")
        _argParser.add_argument('--target', required=False, type=str, default=self.__address, 
        help="Enter IP and Port.\n"
                "This option default value is \'localhost:0\'.\n"
                "The format is: <IP_Address>:<Port>")
        
        return _argParser.parse_args()

    def checkOpt(self, args: Namespace) -> list:
        if args.target != self.__address:
            # Check if ipv4 is correct or not.
            if len(args.target.split(':')) > 2:
                print("Invalid IP format. \'{}\'".format(args.target))
                args.type = "err"
            else:
                _split_str = args.target.split(':')
                # check ip address 
                if self._checkVaildIPAddress(_split_str[0]) and _split_str[1].isdigit() is True:
                    self.__address = _split_str[0] + ":" +_split_str[1]
                else:
                    args.type = "err"
            
        return [args.type, self.__address]

    def getOpt(self) -> list:
        return self.checkOpt(self.argParse())
