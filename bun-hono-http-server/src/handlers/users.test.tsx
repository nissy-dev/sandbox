import { beforeEach, expect, test, vi } from "vitest";
import { getUser, getUsers } from "./users";

const mockRedisGet = vi.fn(); // getのmock
const mockRedisScanStream = vi.fn(); // scanStreamのmock

vi.mock("../lib/redis", () => {
  return {
    getClient: vi.fn().mockImplementation(() => {
      return {
        get: mockRedisGet,
        scanStream: mockRedisScanStream,
      };
    }),
  };
});

beforeEach(() => {
  mockRedisGet.mockClear();
  mockRedisScanStream.mockClear();
});

test("getUser", async () => {
  mockRedisGet.mockResolvedValue(JSON.stringify({ id: 1, name: "alpha" }));
  const userId = "1";
  const res = await getUser(userId);
  // 返り値のテスト
  expect(res?.id).toStrictEqual(1);
  expect(res?.name).toStrictEqual("alpha");
  // mockの呼び出し回数のテスト
  expect(mockRedisGet).toHaveBeenCalledTimes(1);
  // mockの引数のテスト
  const [arg1] = mockRedisGet.mock.calls[0];
  expect(arg1).toStrictEqual("users:1");
});

test("getUsers", async () => {
  const streamMock = {
    async *[Symbol.asyncIterator]() {
      yield ["users:1", "users:2"];
      yield ["users:3", "users:4"];
    },
  };
  mockRedisScanStream.mockReturnValueOnce(streamMock);
  mockRedisGet.mockImplementation((key: string) => {
    switch (key) {
      case "users:1":
        return Promise.resolve(JSON.stringify({ id: 1, name: "alpha" }));
      case "users:2":
        return Promise.resolve(JSON.stringify({ id: 2, name: "bravo" }));
      case "users:3":
        return Promise.resolve(JSON.stringify({ id: 3, name: "charlie" }));
      case "users:4":
        return Promise.resolve(JSON.stringify({ id: 4, name: "delta" }));
    }
    return Promise.resolve(null);
  });

  const res = await getUsers();
  expect(mockRedisGet).toHaveBeenCalledTimes(4);
  expect(res.length).toStrictEqual(4);
  expect(res).toStrictEqual([
    { id: 1, name: "alpha" },
    { id: 2, name: "bravo" },
    { id: 3, name: "charlie" },
    { id: 4, name: "delta" },
  ]);
});

test("getUser 失敗", async () => {
  expect.assertions(2);
  mockRedisGet.mockRejectedValue(new Error("something error"));
  try {
    const userId = "1";
    const res = await getUser(userId);
  } catch (err) {
    // @ts-ignore
    expect(err.message).toStrictEqual("something error");
    expect(err instanceof Error).toStrictEqual(true);
  }
});
