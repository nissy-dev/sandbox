import { int, mysqlTable, text } from "drizzle-orm/mysql-core";

export const user = mysqlTable("user", {
  id: int("id").primaryKey().autoincrement(),
  name: text("name"),
  age: int("age"),
});

export const book = mysqlTable("book", {
  id: int("id").primaryKey().autoincrement(),
  name: text("name"),
  authorId: int("author_id").references(() => user.id),
});
