import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 50, // 가상 사용자 수 (동시 요청 수)
  duration: '30s', // 테스트 지속 시간
};

const BASE_URL = 'http://localhost:8000';

export default function () {
  const itemId = Math.floor(Math.random() * 10) + 1; // 1~10번 아이템 조회
  const res = http.get(`${BASE_URL}/items/${itemId}`);

  check(res, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
  });

  sleep(0.5); // 사용자별 대기 시간
}
