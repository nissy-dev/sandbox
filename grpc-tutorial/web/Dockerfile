FROM ubuntu:20.04

ENV DEBIAN_FRONTEND=noninteractive

ARG PROTO_VERSION=3.19.1
ARG GRPCWEB_VERSION=1.3.0
ARG PROTO_RELEASES_URL=https://github.com/protocolbuffers/protobuf/releases/download
ARG GRPCWEB_RELEASE_URL=https://github.com/grpc/grpc-web/releases/download

WORKDIR /

RUN apt-get -qq update && apt-get -qq install -y unzip curl

RUN curl -ssL ${PROTO_RELEASES_URL}/v${PROTO_VERSION}/protoc-${PROTO_VERSION}-linux-x86_64.zip \
  -o protoc.zip && \
  unzip -qq protoc.zip && \
  cp ./bin/protoc /usr/local/bin/protoc && \
  cp -r ./include /usr/local

RUN curl -sSL ${GRPCWEB_RELEASE_URL}/${GRPCWEB_VERSION}/protoc-gen-grpc-web-${GRPCWEB_VERSION}-linux-x86_64 \
  -o /usr/local/bin/protoc-gen-grpc-web && \
  chmod +x /usr/local/bin/protoc-gen-grpc-web

VOLUME ["/deepthought", "/protos"]
