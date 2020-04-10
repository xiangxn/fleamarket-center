echo $GOPATH

if [ ! -d "./bitsflea/" ];then
    mkdir ./bitsflea
fi
X_PATH="$GOPATH/src/golang.org/x"
X_NET_PATH="$GOPATH/src/golang.org/x/net"
X_TEXT_PATH="$GOPATH/src/golang.org/x/text"
X_SYS_PATH="$GOPATH/src/golang.org/x/sys"

if [ ! -d $X_PATH ];then
    mkdir -p $X_PATH
fi

if [ ! -d $X_NET_PATH ];then
    pushd $X_PATH
    git clone https://github.com/golang/net.git
    popd -1
fi

if [ ! -d $X_TEXT_PATH ];then
    pushd $X_PATH
    git clone https://github.com/golang/text.git
    popd -1
fi

if [ ! -d $X_SYS_PATH ];then
    pushd $X_PATH
    git clone https://github.com/golang/sys.git
    popd -1
fi

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