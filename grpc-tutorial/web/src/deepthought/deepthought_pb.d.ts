import * as jspb from 'google-protobuf'

import * as google_protobuf_timestamp_pb from 'google-protobuf/google/protobuf/timestamp_pb';


export class BootRequest extends jspb.Message {
  getSilent(): boolean;
  setSilent(value: boolean): BootRequest;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): BootRequest.AsObject;
  static toObject(includeInstance: boolean, msg: BootRequest): BootRequest.AsObject;
  static serializeBinaryToWriter(message: BootRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): BootRequest;
  static deserializeBinaryFromReader(message: BootRequest, reader: jspb.BinaryReader): BootRequest;
}

export namespace BootRequest {
  export type AsObject = {
    silent: boolean,
  }
}

export class BootResponse extends jspb.Message {
  getMessage(): string;
  setMessage(value: string): BootResponse;

  getTimestamp(): google_protobuf_timestamp_pb.Timestamp | undefined;
  setTimestamp(value?: google_protobuf_timestamp_pb.Timestamp): BootResponse;
  hasTimestamp(): boolean;
  clearTimestamp(): BootResponse;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): BootResponse.AsObject;
  static toObject(includeInstance: boolean, msg: BootResponse): BootResponse.AsObject;
  static serializeBinaryToWriter(message: BootResponse, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): BootResponse;
  static deserializeBinaryFromReader(message: BootResponse, reader: jspb.BinaryReader): BootResponse;
}

export namespace BootResponse {
  export type AsObject = {
    message: string,
    timestamp?: google_protobuf_timestamp_pb.Timestamp.AsObject,
  }
}

export class InferRequest extends jspb.Message {
  getQuery(): string;
  setQuery(value: string): InferRequest;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): InferRequest.AsObject;
  static toObject(includeInstance: boolean, msg: InferRequest): InferRequest.AsObject;
  static serializeBinaryToWriter(message: InferRequest, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): InferRequest;
  static deserializeBinaryFromReader(message: InferRequest, reader: jspb.BinaryReader): InferRequest;
}

export namespace InferRequest {
  export type AsObject = {
    query: string,
  }
}

export class InferResponse extends jspb.Message {
  getAnswer(): number;
  setAnswer(value: number): InferResponse;

  serializeBinary(): Uint8Array;
  toObject(includeInstance?: boolean): InferResponse.AsObject;
  static toObject(includeInstance: boolean, msg: InferResponse): InferResponse.AsObject;
  static serializeBinaryToWriter(message: InferResponse, writer: jspb.BinaryWriter): void;
  static deserializeBinary(bytes: Uint8Array): InferResponse;
  static deserializeBinaryFromReader(message: InferResponse, reader: jspb.BinaryReader): InferResponse;
}

export namespace InferResponse {
  export type AsObject = {
    answer: number,
  }
}

