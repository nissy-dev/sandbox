/**
 * @fileoverview gRPC-Web generated client stub for deepthought
 * @enhanceable
 * @public
 */

// GENERATED CODE -- DO NOT EDIT!

/* eslint-disable */
// @ts-nocheck

import * as grpcWeb from "grpc-web";

import * as deepthought_pb from "./deepthought_pb";

export class ComputeClient {
  client_: grpcWeb.AbstractClientBase;
  hostname_: string;
  credentials_: null | { [index: string]: string };
  options_: null | { [index: string]: any };

  constructor(
    hostname: string,
    credentials?: null | { [index: string]: string },
    options?: null | { [index: string]: any }
  ) {
    if (!options) options = {};
    if (!credentials) credentials = {};
    options["format"] = "text";

    this.client_ = new grpcWeb.GrpcWebClientBase(options);
    this.hostname_ = hostname;
    this.credentials_ = credentials;
    this.options_ = options;
  }

  methodInfoBoot = new grpcWeb.MethodDescriptor(
    "/deepthought.Compute/Boot",
    grpcWeb.MethodType.SERVER_STREAMING,
    deepthought_pb.BootRequest,
    deepthought_pb.BootResponse,
    (request: deepthought_pb.BootRequest) => {
      return request.serializeBinary();
    },
    deepthought_pb.BootResponse.deserializeBinary
  );

  boot(request: deepthought_pb.BootRequest, metadata?: grpcWeb.Metadata) {
    return this.client_.serverStreaming(
      this.hostname_ + "/deepthought.Compute/Boot",
      request,
      metadata || {},
      this.methodInfoBoot
    );
  }

  methodInfoInfer = new grpcWeb.MethodDescriptor(
    "/deepthought.Compute/Infer",
    grpcWeb.MethodType.UNARY,
    deepthought_pb.InferRequest,
    deepthought_pb.InferResponse,
    (request: deepthought_pb.InferRequest) => {
      return request.serializeBinary();
    },
    deepthought_pb.InferResponse.deserializeBinary
  );

  infer(
    request: deepthought_pb.InferRequest,
    metadata: grpcWeb.Metadata | null
  ): Promise<deepthought_pb.InferResponse>;

  infer(
    request: deepthought_pb.InferRequest,
    metadata: grpcWeb.Metadata | null,
    callback: (
      err: grpcWeb.RpcError,
      response: deepthought_pb.InferResponse
    ) => void
  ): grpcWeb.ClientReadableStream<deepthought_pb.InferResponse>;

  infer(
    request: deepthought_pb.InferRequest,
    metadata: grpcWeb.Metadata | null,
    callback?: (
      err: grpcWeb.RpcError,
      response: deepthought_pb.InferResponse
    ) => void
  ) {
    if (callback !== undefined) {
      return this.client_.rpcCall(
        this.hostname_ + "/deepthought.Compute/Infer",
        request,
        metadata || {},
        this.methodInfoInfer,
        callback
      );
    }
    return this.client_.unaryCall(
      this.hostname_ + "/deepthought.Compute/Infer",
      request,
      metadata || {},
      this.methodInfoInfer
    );
  }
}
