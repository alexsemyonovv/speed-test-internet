import time
from dataclasses import dataclass

import httpx

from utils.logger import logger

USER_AGENT = "SpeedTest/1.0 (https://github.com/alexsemyonovv/speed-test)"


@dataclass
class SpeedTestResult:
    request_count: int
    total_bytes: int
    average_request_time: float
    speed_mbps: float


def fetch_url(client: httpx.Client, url: str) -> tuple[int, float]:
    logger.debug("Отправка запроса к {}", url)
    start = time.perf_counter()
    response = client.get(url, follow_redirects=True)
    elapsed = time.perf_counter() - start
    response.raise_for_status()
    size = len(response.content)
    logger.debug("Получен ответ: {} байт за {:.3f} сек", size, elapsed)
    return size, elapsed


def run_speed_test(url: str, request_count: int = 10) -> SpeedTestResult:
    logger.info("Начало замера скорости: {} запросов к {}", request_count, url)
    total_bytes = 0
    total_time = 0.0

    headers = {"User-Agent": USER_AGENT}
    with httpx.Client(timeout=60.0, headers=headers) as client:
        for i in range(1, request_count + 1):
            logger.info("Запрос {}/{}", i, request_count)
            size, elapsed = fetch_url(client, url)
            total_bytes += size
            total_time += elapsed

    average_request_time = total_time / request_count
    speed_mbps = (total_bytes / total_time) / (1024 * 1024)

    logger.info(
        "Замер завершён: всего {} байт, среднее время запроса {:.3f} сек, скорость {:.2f} МБ/с",
        total_bytes,
        average_request_time,
        speed_mbps,
    )

    return SpeedTestResult(
        request_count=request_count,
        total_bytes=total_bytes,
        average_request_time=average_request_time,
        speed_mbps=speed_mbps,
    )
