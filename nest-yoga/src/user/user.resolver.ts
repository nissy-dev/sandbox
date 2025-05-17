import { Args, Mutation, Query, Resolver } from '@nestjs/graphql';
import { UserService } from './user.service';
import { trace, context, SpanStatusCode } from '@opentelemetry/api';

// トレーサーを取得
const tracer = trace.getTracer('graphql-resolver');

@Resolver('User')
export class UserResolver {
  constructor(private readonly userService: UserService) {}

  @Query('hello')
  hello(): string {
    // 手動計装のスパンを作成
    return tracer.startActiveSpan('resolver.hello', (span) => {
      try {
        // スパンに属性を追加
        span.setAttribute('query', 'hello');
        span.setAttribute('resolver.type', 'Query');

        // ビジネスロジックを実行
        const result = 'Hello World!';

        // スパンを正常に終了
        span.setStatus({ code: SpanStatusCode.OK });
        span.end();
        return result;
      } catch (error) {
        // エラーが発生した場合、スパンにエラー情報を記録
        span.setStatus({
          code: SpanStatusCode.ERROR,
          message: error instanceof Error ? error.message : String(error),
        });
        span.end();
        throw error;
      }
    });
  }

  @Query('users')
  users() {
    return this.userService.findAll();
  }

  @Query('user')
  user(@Args('id') id: string) {
    return this.userService.findOne(id);
  }

  @Mutation('createUser')
  createUser(@Args('input') input: { name: string; email: string }) {
    return this.userService.create(input);
  }
}
