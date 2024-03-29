package main

import (
  "context"  // Use "golang.org/x/net/context" for Golang version <= 1.6
  "flag"
  "net/http"

  "github.com/golang/glog"
  "github.com/grpc-ecosystem/grpc-gateway/runtime"
  "google.golang.org/grpc"

  gw "./bitsflea"  // Update
)

var (
  // command-line options:
  // gRPC server endpoint
  grpcServerEndpoint = flag.String("bitsflea-endpoint",  "localhost:50000", "gRPC server endpoint")
)

func CustomMatcher(key string) (string, bool) {
  switch key {
  case "Token":
      return key, true
  default:
      return runtime.DefaultHeaderMatcher(key)
  }
}

func run() error {
  ctx := context.Background()
  ctx, cancel := context.WithCancel(ctx)
  defer cancel()

  // Register gRPC server endpoint
  // Note: Make sure the gRPC server is running properly and accessible
  mux := runtime.NewServeMux(runtime.WithIncomingHeaderMatcher(CustomMatcher))
  opts := []grpc.DialOption{grpc.WithInsecure()}
  err := gw.RegisterBitsFleaHandlerFromEndpoint(ctx, mux,  *grpcServerEndpoint, opts)
  if err != nil {
    return err
  }

  // Start HTTP server (and proxy calls to gRPC server endpoint)
  return http.ListenAndServe(":8081", mux)
}

func main() {
  flag.Parse()
  defer glog.Flush()

  if err := run(); err != nil {
    glog.Fatal(err)
  }
}