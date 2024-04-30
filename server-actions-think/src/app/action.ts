"use server";

import { redirect } from "next/navigation";

const sleep = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

export const createTodo = async () => {
  await sleep(2000);
  throw new Error("Server action failed");
  // return "Todo created";
  // redirect("/todo");
};
