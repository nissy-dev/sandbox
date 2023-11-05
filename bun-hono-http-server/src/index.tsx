import { serve } from "@hono/node-server";
import { serveStatic } from "@hono/node-server/serve-static";
import { Hono } from "hono";
import { BadRequest } from "./errors";
import { getUser, getUsers } from "./handlers/users";
import { Users } from "./htmls/users";
import * as redis from "./lib/redis";

const app = new Hono();

app.use("/static/*", serveStatic({ root: "./" }));

const validation = (userId: string) => {
  if (userId === "") {
    throw new BadRequest("idがありません");
  }
};

app.get("/user/:id", async (c) => {
  const id = c.req.param("id");
  validation(id);
  const user = await getUser(id);

  if (user === null) {
    return c.text(`The user with user_id=${id} was not found`, 404);
  }

  return c.json(user);
});

app.get("/users", async (c) => {
  const users = await getUsers();
  return c.html(<Users users={users} />);
});

app.onError((err, c) => {
  if (err instanceof BadRequest) {
    return c.text(err.message, err.status);
  }
  console.error(`${err}`);
  return c.text("Internal Server Error", 500);
});

redis
  .connect()
  .once("ready", async () => {
    try {
      await redis.init();
      serve(app);
    } catch (err) {
      console.error(err);
      process.exit(1);
    }
  })
  .on("error", (err) => {
    console.error(err);
    process.exit(1);
  });
