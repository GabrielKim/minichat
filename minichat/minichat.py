#-*- coding: utf-8 -*-

from etc.mcArgParse import mcArgParser

from mcServer import mcServer
from mcClient import mcClient

def main() -> None:
    _mcArgParseHelper = mcArgParser()
    _optList = _mcArgParseHelper.getOpt()

    if _optList[0] == 'Server':
        # Activate Server
        _mcServer = mcServer()
        _mcServer.start(_optList)
        
    elif _optList[0] == 'Client':
        # Activate Client
        _mcClient = mcClient()
        _mcClient.start(_optList)
        
    else:
        # error
        print("Error Occored.")

if __name__ == '__main__':
    main()