import * as redis from "../lib/redis";

export type User = {
  id: number;
  name: string;
};

export const getUser = async (userId: string) => {
  const key = `users:${userId}`;
  const client = redis.getClient();

  if (client === null) {
    throw new Error("Redis client is not initialized");
  }

  const val = await client.get(key);

  if (!val) {
    return null;
  }

  const user = JSON.parse(val) as User;
  return user;
};

export const getUsers = async () => {
  const client = redis.getClient();

  if (client === null) {
    throw new Error("Redis client is not initialized");
  }

  const stream = client.scanStream({
    match: "users:*",
    count: 2,
  });
  const users = [];
  for await (const resultKeys of stream) {
    for (const key of resultKeys) {
      const value = await client.get(key);
      if (value) {
        const user = JSON.parse(value) as User;
        users.push(user);
      }
    }
  }

  return users;
};
