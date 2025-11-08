import { test as base, expect } from "@playwright/experimental-ct-react";
import { rest } from "msw";
import type { MockServiceWorker } from "playwright-msw";
import { createWorkerFixture } from "playwright-msw";

// import handlers from "./handlers";

const handlers = [
  rest.get("/api/hello", async (_req, res, ctx) => {
    return res(ctx.status(200), ctx.json<string>("fetch data"));
  }),
];

const test = base.extend<{
  worker: MockServiceWorker;
}>({
  worker: createWorkerFixture(handlers),
});

export { test, expect };
