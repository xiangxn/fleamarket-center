python -m grpc_tools.protoc -I=./center/protos \
    -I$GOPATH/src/github.com/grpc-ecosystem/grpc-gateway/third_party/googleapis \
    --python_out=./center/rpc \
    --grpc_python_out=./center/rpc \
    ./center/protos/bitsflea.proto

python -m grpc_tools.protoc -I=./center/protos \
    -I/usr/local/include \
    -I$GOPATH/src \
    -I$GOPATH/src/github.com/grpc-ecosystem/grpc-gateway/third_party/googleapis \
    --go_out=plugins=grpc:./bitsflea \
    ./center/protos/bitsflea.proto

python -m grpc_tools.protoc -I=./center/protos \
    -I/usr/local/include \
    -I$GOPATH/src \
    -I$GOPATH/src/github.com/grpc-ecosystem/grpc-gateway/third_party/googleapis \
    --grpc-gateway_out=logtostderr=true:./bitsflea \
    ./center/protos/bitsflea.proto

go build -o restful_proxy .