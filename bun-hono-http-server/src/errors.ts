export class BadRequest extends Error {
  readonly status: number;

  constructor(message: string) {
    super("Bad Request");
    this.status = 400;
    this.message = message;
  }
}
