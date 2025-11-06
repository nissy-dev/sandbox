import grpc from "k6/net/grpc";
import { check, sleep } from "k6";

const client = new grpc.Client();

export const options = {
  vus: 1,
  duration: "2s",
};

export default function () {
  client.connect("host.docker.internal:8080", {
    plaintext: true,
    reflect: true,
  });
  const response = client.invoke("sample.SampleService/CreateUser", {
    name: "user-" + Math.random().toString(36).substring(7),
  });
  check(response, {
    "status is OK": (r) => r && r.status === grpc.StatusOK,
  });
  client.close();
}
