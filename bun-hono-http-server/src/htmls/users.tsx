import { User } from "../handlers/users";

type Props = {
  users: User[];
};

export const Users = ({ users }: Props) => {
  return (
    <html lang="ja">
      <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>users</title>
      </head>
      <body>
        <ul>
          {users.map((user) => (
            <li class="user">{user.name}</li>
          ))}
        </ul>
      </body>
      <script src="/static/index.js" defer />
    </html>
  );
};
