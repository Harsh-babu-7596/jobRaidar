from app.scrapers.base import BaseScraper

class CustomScraper(BaseScraper):
    def fetch_jobs(self, company) -> list[dict]:
        """Custom sites need site-specific selectors or an approved public endpoint.

        Add a dedicated adapter for each site rather than assuming one HTML layout
        works for every career page.
        """
        raise NotImplementedError(
            f"No custom scraper configured for {company.name}. "
            "Implement a site-specific adapter before enabling this company."
        )
