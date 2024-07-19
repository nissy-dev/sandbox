import { db, connection } from "./db";
import { book, user } from "./schema";

async function main() {
  await db.insert(user).values({
    name: "Bob",
    age: 20,
  });
  const data = await db.query.user.findMany().execute();
  console.log(data);
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
