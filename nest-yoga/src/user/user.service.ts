import { Injectable } from '@nestjs/common';

export interface User {
  id: string;
  name: string;
  email: string;
}

@Injectable()
export class UserService {
  private users: User[] = [];

  findAll(): User[] {
    return this.users;
  }

  findOne(id: string): User | undefined {
    return this.users.find((user) => user.id === id);
  }

  create(input: { name: string; email: string }): User {
    const user = {
      id: Date.now().toString(),
      ...input,
    };
    this.users.push(user);
    return user;
  }
}
