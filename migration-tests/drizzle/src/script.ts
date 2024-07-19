import { db, connection } from "./db";
import { book, user } from "./schema";

async function main() {
  await db.insert(user).values({
    name: "Bob",
  });
  const data1 = await db.query.user.findFirst().execute();
  console.log(data1);
  await db.insert(book).values({
    name: "book1",
    authorId: data1?.id,
  });
  const data2 = await db.query.book.findFirst().execute();
  console.log(data2);
}

main()
  .then(async () => {
    await connection.end();
  })
  .catch(async (e) => {
    console.error(e);
    await connection.end();
    process.exit(1);
  });
