import { ComputeClient } from "./deepthought/DeepthoughtServiceClientPb";

export type GRPCClients = {
  computeClient: ComputeClient;
};

export const gRPCClients = {
  computeClient: new ComputeClient(`http://localhost:9000`),
};
