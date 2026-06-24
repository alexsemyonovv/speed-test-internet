from unittest.mock import MagicMock

import httpx
import pytest

from utils.speed_test import SpeedTestResult, fetch_url, run_speed_test

FAKE_URL = "https://example.com/image.jpg"
FAKE_CONTENT = b"x" * (1024 * 1024)


def make_response(content: bytes = FAKE_CONTENT, status_code: int = 200) -> MagicMock:
    response = MagicMock(spec=httpx.Response)
    response.content = content
    response.status_code = status_code
    if status_code >= 400:
        response.raise_for_status.side_effect = httpx.HTTPStatusError(
            message=f"HTTP {status_code}",
            request=MagicMock(),
            response=response,
        )
    else:
        response.raise_for_status.return_value = None
    return response


class TestFetchUrl:
    def test_returns_size_and_elapsed(self, mocker) -> None:
        client = mocker.MagicMock(spec=httpx.Client)
        client.get.return_value = make_response(FAKE_CONTENT)

        size, elapsed = fetch_url(client, FAKE_URL)

        assert size == len(FAKE_CONTENT)
        assert elapsed >= 0.0

    def test_raises_on_http_error(self, mocker) -> None:
        client = mocker.MagicMock(spec=httpx.Client)
        client.get.return_value = make_response(b"not found", status_code=404)

        with pytest.raises(httpx.HTTPStatusError):
            fetch_url(client, FAKE_URL)

    @pytest.mark.parametrize(
        "content",
        [
            b"small",
            b"x" * 512,
            b"x" * (2 * 1024 * 1024),
        ],
    )
    def test_various_content_sizes(self, mocker, content: bytes) -> None:
        client = mocker.MagicMock(spec=httpx.Client)
        client.get.return_value = make_response(content)

        size, elapsed = fetch_url(client, FAKE_URL)

        assert size == len(content)
        assert elapsed >= 0.0


class TestRunSpeedTest:
    def test_result_structure(self, mocker) -> None:
        mocker.patch(
            "utils.speed_test.fetch_url",
            return_value=(len(FAKE_CONTENT), 0.5),
        )

        result = run_speed_test(FAKE_URL, request_count=10)

        assert isinstance(result, SpeedTestResult)
        assert result.request_count == 10
        assert result.total_bytes == len(FAKE_CONTENT) * 10
        assert abs(result.average_request_time - 0.5) < 1e-9

    @pytest.mark.parametrize(
        "request_count, bytes_per_request, time_per_request",
        [
            (5, 1024, 1.0),
            (10, 2048, 0.5),
            (3, 4096, 2.0),
        ],
    )
    def test_speed_calculation(
        self,
        mocker,
        request_count: int,
        bytes_per_request: int,
        time_per_request: float,
    ) -> None:
        mocker.patch(
            "utils.speed_test.fetch_url",
            return_value=(bytes_per_request, time_per_request),
        )

        result = run_speed_test(FAKE_URL, request_count=request_count)

        expected_total_bytes = bytes_per_request * request_count
        expected_total_time = time_per_request * request_count
        expected_speed = (expected_total_bytes / expected_total_time) / (1024 * 1024)

        assert result.total_bytes == expected_total_bytes
        assert abs(result.average_request_time - time_per_request) < 1e-9
        assert abs(result.speed_mbps - expected_speed) < 1e-9

    def test_fetch_called_correct_number_of_times(self, mocker) -> None:
        mock_fetch = mocker.patch(
            "utils.speed_test.fetch_url",
            return_value=(1024, 0.1),
        )

        run_speed_test(FAKE_URL, request_count=7)

        assert mock_fetch.call_count == 7
