import argparse

from utils.logger import logger
from utils.speed_test import SpeedTestResult, run_speed_test

DEFAULT_URL = "https://upload.wikimedia.org/wikipedia/commons/0/0b/Cat_poster_1.jpg"
DEFAULT_REQUEST_COUNT = 10


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Измеритель скорости интернета")
    parser.add_argument(
        "--url",
        type=str,
        default=DEFAULT_URL,
        help="URL ресурса для замера скорости (по умолчанию: тяжёлое изображение Wikimedia)",
    )
    parser.add_argument(
        "--count",
        type=int,
        default=DEFAULT_REQUEST_COUNT,
        help=f"Количество запросов (по умолчанию: {DEFAULT_REQUEST_COUNT})",
    )
    return parser.parse_args()


def print_results(result: SpeedTestResult) -> None:
    print("\n" + "=" * 50)
    print("       РЕЗУЛЬТАТЫ ЗАМЕРА СКОРОСТИ")
    print("=" * 50)
    print(f"  Количество запросов : {result.request_count}")
    print(f"  Скачано данных      : {result.total_bytes / (1024 * 1024):.2f} МБ")
    print(f"  Среднее время запроса : {result.average_request_time:.3f} сек")
    print(f"  Скорость            : {result.speed_mbps:.2f} МБ/с")
    print("=" * 50 + "\n")


def main() -> None:
    args = parse_args()
    logger.info("Запуск замера скорости: url={}, count={}", args.url, args.count)
    result = run_speed_test(url=args.url, request_count=args.count)
    print_results(result)


if __name__ == "__main__":
    main()
