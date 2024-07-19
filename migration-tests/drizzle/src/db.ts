import dotenv from "dotenv";
import { drizzle } from "drizzle-orm/mysql2";
import mysql from "mysql2/promise";

import * as schema from "./schema";

dotenv.config();

export const connection = await mysql.createConnection({
  uri: process.env.DATABASE_URL || "",
  multipleStatements: true,
});

export const db = drizzle(connection, { schema, mode: "default" });
