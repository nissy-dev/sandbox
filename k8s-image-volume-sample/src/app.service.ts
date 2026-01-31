import { Injectable } from '@nestjs/common';

@Injectable()
export class AppService {
  getInfo() {
    return {
      message: 'k8s-image-volume-sample',
      stack: 'NestJS',
    };
  }

  getHealth() {
    return { status: 'ok' };
  }
}
