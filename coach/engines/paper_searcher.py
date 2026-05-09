"""
Academic Paper Searcher
Free search using arXiv and OpenReview APIs
"""

from typing import List, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class AcademicPaper:
    """Represents an academic paper"""
    title: str
    authors: List[str]
    abstract: str
    url: str
    source: str  # "arxiv" or "openreview"
    published_date: str
    pdf_url: Optional[str] = None
    citation_count: int = 0


class PaperSearcher:
    """
    Free academic paper search using arXiv and OpenReview
    No API keys required
    """

    def __init__(self):
        try:
            import arxiv
            self.arxiv = arxiv
            self.arxiv_available = True
        except ImportError:
            logger.warning("arxiv library not installed, paper search disabled")
            self.arxiv_available = False

    def search_papers(
        self,
        query: str,
        max_results: int = 10,
        sources: Optional[List[str]] = None,
    ) -> List[AcademicPaper]:
        """
        Search for academic papers
        """
        if sources is None:
            sources = ["arxiv", "openreview"]

        papers = []

        if "arxiv" in sources and self.arxiv_available:
            arxiv_papers = self._search_arxiv(query, max_results=max_results)
            papers.extend(arxiv_papers)

        if "openreview" in sources:
            openreview_papers = self._search_openreview(query, max_results=max_results)
            papers.extend(openreview_papers)

        return papers

    def _search_arxiv(
        self,
        query: str,
        max_results: int = 10,
    ) -> List[AcademicPaper]:
        """Search arXiv"""
        papers = []

        if not self.arxiv_available:
            return papers

        try:
            client = self.arxiv.Client()
            search = self.arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=self.arxiv.SortCriterion.SubmittedDate,
                sort_order=self.arxiv.SortOrder.Descending,
            )

            for result in client.results(search):
                paper = AcademicPaper(
                    title=result.title,
                    authors=[author.name for author in result.authors],
                    abstract=result.summary,
                    url=result.entry_id,
                    pdf_url=result.pdf_url,
                    source="arxiv",
                    published_date=result.published.isoformat(),
                )
                papers.append(paper)

        except Exception as e:
            logger.error(f"Error searching arXiv: {str(e)}")

        return papers

    def _search_openreview(
        self,
        query: str,
        max_results: int = 10,
    ) -> List[AcademicPaper]:
        """Search OpenReview"""
        papers = []

        try:
            import requests

            # OpenReview API endpoint
            url = "https://api.openreview.net/notes"
            params = {
                "content.title": query,
                "limit": max_results,
            }

            response = requests.get(url, params=params, timeout=5)

            if response.status_code == 200:
                data = response.json()

                for note in data.get("notes", []):
                    paper = AcademicPaper(
                        title=note.get("content", {}).get("title", "Unknown"),
                        authors=note.get("content", {}).get("authors", []),
                        abstract=note.get("content", {}).get("abstract", ""),
                        url=f"https://openreview.net/forum?id={note.get('forum')}",
                        source="openreview",
                        published_date=note.get("tmdate", ""),
                    )
                    papers.append(paper)

        except Exception as e:
            logger.error(f"Error searching OpenReview: {str(e)}")

        return papers

    @staticmethod
    def format_paper(paper: AcademicPaper) -> str:
        """Format paper for display"""
        authors_str = ", ".join(paper.authors[:3])
        if len(paper.authors) > 3:
            authors_str += f" et al."

        return f"""
**{paper.title}**

Authors: {authors_str}
Source: {paper.source.upper()} ({paper.published_date})

Abstract: {paper.abstract[:200]}...

[Read Paper]({paper.url})
"""


def search_papers_for_domain(
    domain: str,
    max_results: int = 10,
) -> List[AcademicPaper]:
    """
    Convenience function to search papers relevant to a domain
    """
    searcher = PaperSearcher()

    domain_queries = {
        "machine_learning": "machine learning tutorial",
        "deep_learning": "deep learning neural networks",
        "nlp": "natural language processing",
        "computer_vision": "computer vision image",
        "reinforcement_learning": "reinforcement learning",
        "ai": "artificial intelligence",
        "data_science": "data science analysis",
        "python": "Python programming",
    }

    query = domain_queries.get(domain, domain)
    return searcher.search_papers(query, max_results=max_results)
