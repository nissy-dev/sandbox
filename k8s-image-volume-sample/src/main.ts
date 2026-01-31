import { serve } from "@hono/node-server";
import { Hono } from "hono";

const app = new Hono();

app.get("/", (c) =>
  c.json({
    message: "k8s-image-volume-sample",
    path: c.req.path,
    method: c.req.method,
  })
);

app.get("/health", (c) => c.json({ status: "ok" }));

const port = Number(process.env.PORT) || 3000;
console.log(`Server listening on port ${port}`);
serve({ fetch: app.fetch, port });