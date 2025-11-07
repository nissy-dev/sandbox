import grpc from "k6/net/grpc";
import { check, sleep } from "k6";

const client = new grpc.Client();

export const options = {
  vus: 2,
  duration: "300s",
};

export function setup() {
  const setupClient = new grpc.Client();
  setupClient.connect("host.docker.internal:8080", {
    plaintext: true,
    reflect: true,
  });

  const userIds = [];

  // 初期ユーザーを100人作成
  for (let i = 0; i < 100; i++) {
    const createResponse = setupClient.invoke(
      "sample.SampleService/CreateUser",
      {
        name: `initial-user-${i}`,
      }
    );

    if (
      createResponse.status === grpc.StatusOK &&
      createResponse.message.user
    ) {
      userIds.push(createResponse.message.user.id);
    }
  }

  setupClient.close();
  return { userIds };
}

export default function (data) {
  client.connect("host.docker.internal:8080", {
    plaintext: true,
    reflect: true,
  });
  // 20%の確率で新しいユーザーを作成、80%の確率で既存ユーザーを取得
  if (Math.random() < 0.2) {
    // CreateUser
    const createResponse = client.invoke("sample.SampleService/CreateUser", {
      name: "user-" + Math.random().toString(36).substring(7),
    });

    check(createResponse, {
      "CreateUser status is OK": (r) => r && r.status === grpc.StatusOK,
      "CreateUser has user": (r) => r && r.message && r.message.user,
    });

    // 作成されたユーザーIDを既存リストに追加
    if (
      createResponse.status === grpc.StatusOK &&
      createResponse.message.user
    ) {
      data.userIds.push(createResponse.message.user.id);
    }
  } else if (data.userIds.length > 0) {
    // ランダムにGetUser
    const randomUserId =
      data.userIds[Math.floor(Math.random() * data.userIds.length)];

    const getUserResponse = client.invoke("sample.SampleService/GetUser", {
      id: randomUserId,
    });

    check(getUserResponse, {
      "GetUser status is OK": (r) => r && r.status === grpc.StatusOK,
      "GetUser has user": (r) => r && r.message && r.message.user,
      "GetUser correct ID": (r) =>
        r && r.message && r.message.user && r.message.user.id === randomUserId,
    });
  }

  client.close();
}
