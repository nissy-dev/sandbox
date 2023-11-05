import Redis from "ioredis";

let redis: Redis | null = null;

export const connect = () => {
  if (!redis) {
    redis = new Redis({
      port: 6379,
      host: "localhost",
      password: process.env.REDIS_PASSWORD,
      enableOfflineQueue: false,
    });
  }
  return redis;
};

export const init = async () => {
  if (!redis) {
    throw new Error("Redis is not connected");
  }
  await Promise.all([
    redis.set("users:1", JSON.stringify({ id: 1, name: "alpha" })),
    redis.set("users:2", JSON.stringify({ id: 2, name: "bravo" })),
    redis.set("users:3", JSON.stringify({ id: 3, name: "charlie" })),
    redis.set("users:4", JSON.stringify({ id: 4, name: "delta" })),
  ]);
};

export const getClient = () => {
  return redis;
};
