#!/bin/bash

# generate proto for minichat
python -m grpc_tools.protoc -I=minichat/protobuf/ --python_out=minichat/ --grpc_python_out=minichat/ minichat/protobuf/minichat.proto