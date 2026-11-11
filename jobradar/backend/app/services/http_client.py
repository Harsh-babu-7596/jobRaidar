import requests

DEFAULT_HEADERS = {
    "User-Agent": "JobRadar/0.1 (personal job discovery tool)",
    "Accept": "text/html,application/json;q=0.9,*/*;q=0.8",
}


def get(url: str, *, timeout: int, headers: dict | None = None, **kwargs):
    merged = {**DEFAULT_HEADERS, **(headers or {})}
    return requests.get(url, timeout=timeout, headers=merged, **kwargs)


def post(url: str, *, timeout: int, headers: dict | None = None, **kwargs):
    merged = {**DEFAULT_HEADERS, **(headers or {})}
    return requests.post(url, timeout=timeout, headers=merged, **kwargs)
