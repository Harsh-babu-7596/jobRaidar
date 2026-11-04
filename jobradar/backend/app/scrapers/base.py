from abc import ABC, abstractmethod

class BaseScraper(ABC):
    @abstractmethod
    def fetch_jobs(self, company) -> list[dict]:
        """Return normalized job dictionaries."""
        raise NotImplementedError
