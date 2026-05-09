"""
Multi-dimensional search engine for finding real human experiences
"""

import requests
import feedparser
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """A single search result"""
    title: str
    url: str
    source: str  # "reddit", "github", "blog", "forum", "paper"
    summary: str
    author: Optional[str] = None
    date: Optional[str] = None
    upvotes: int = 0
    relevance_score: float = 0.5  # 0-1


class SearchEngine:
    """
    Multi-dimensional search engine for finding proven strategies
    Searches across Reddit, forums, blogs, GitHub, arXiv, etc.
    """

    def __init__(self):
        self.headers = {
            'User-Agent': 'CoachEverything/1.0 (+https://github.com/yourusername/coach-everything)'
        }
        self.platforms = {
            'reddit': self._search_reddit,
            'github': self._search_github,
            'blogs': self._search_blogs,
            'forums': self._search_forums,
            'papers': self._search_papers,
        }

    def search(
        self,
        query: str,
        platforms: Optional[List[str]] = None,
        include_papers: bool = True,
        recency_weight: float = 0.7,
        max_results: int = 30,
    ) -> List[SearchResult]:
        """
        Search across multiple platforms
        """
        if platforms is None:
            platforms = ['reddit', 'github', 'forums', 'blogs']
            if include_papers:
                platforms.append('papers')

        all_results = []

        for platform in platforms:
            if platform in self.platforms:
                try:
                    results = self.platforms[platform](
                        query,
                        max_results=max_results // len(platforms)
                    )
                    all_results.extend(results)
                except Exception as e:
                    logger.warning(f"Error searching {platform}: {str(e)}")

        # Score by recency and relevance
        self._score_results(all_results, recency_weight)

        # Return top results
        return sorted(
            all_results,
            key=lambda x: x.relevance_score,
            reverse=True
        )[:max_results]

    def _search_reddit(
        self,
        query: str,
        max_results: int = 10
    ) -> List[SearchResult]:
        """Search Reddit via RSS feeds"""
        results = []
        subreddits = self._suggest_subreddits(query)

        for subreddit in subreddits[:3]:
            try:
                url = f"https://www.reddit.com/r/{subreddit}/search.json"
                params = {'q': query, 'restrict_sr': 'on', 'limit': max_results}

                response = requests.get(
                    url,
                    params=params,
                    headers=self.headers,
                    timeout=5
                )

                if response.status_code == 200:
                    data = response.json()
                    for post in data['data']['children']:
                        post_data = post['data']
                        results.append(SearchResult(
                            title=post_data['title'],
                            url=f"https://reddit.com{post_data['permalink']}",
                            source='reddit',
                            summary=post_data.get('selftext', '')[:200],
                            author=post_data['author'],
                            date=datetime.fromtimestamp(
                                post_data['created_utc']
                            ).isoformat(),
                            upvotes=post_data['score'],
                        ))
            except Exception as e:
                logger.warning(f"Error searching r/{subreddit}: {str(e)}")

        return results

    def _search_github(
        self,
        query: str,
        max_results: int = 10
    ) -> List[SearchResult]:
        """Search GitHub repositories"""
        results = []
        try:
            url = "https://api.github.com/search/repositories"
            params = {
                'q': f"{query} in:readme,description",
                'sort': 'stars',
                'order': 'desc',
                'per_page': max_results,
            }

            response = requests.get(
                url,
                params=params,
                headers=self.headers,
                timeout=5
            )

            if response.status_code == 200:
                data = response.json()
                for repo in data.get('items', []):
                    results.append(SearchResult(
                        title=repo['full_name'],
                        url=repo['html_url'],
                        source='github',
                        summary=repo.get('description', '')[:200],
                        author=repo['owner']['login'],
                        date=repo['created_at'],
                        upvotes=repo['stargazers_count'],
                    ))
        except Exception as e:
            logger.warning(f"Error searching GitHub: {str(e)}")

        return results

    def _search_blogs(
        self,
        query: str,
        max_results: int = 10
    ) -> List[SearchResult]:
        """Search blog platforms (Medium, Dev.to, etc.)"""
        results = []

        # Dev.to API
        try:
            url = "https://dev.to/api/articles"
            params = {'q': query, 'per_page': max_results}

            response = requests.get(
                url,
                params=params,
                timeout=5
            )

            if response.status_code == 200:
                for article in response.json():
                    results.append(SearchResult(
                        title=article['title'],
                        url=article['url'],
                        source='blogs',
                        summary=article['description'][:200],
                        author=article['user']['name'],
                        date=article['created_at'],
                        upvotes=article['comments_count'],
                    ))
        except Exception as e:
            logger.warning(f"Error searching Dev.to: {str(e)}")

        return results

    def _search_forums(
        self,
        query: str,
        max_results: int = 10
    ) -> List[SearchResult]:
        """Search forums (Stack Overflow, etc.)"""
        results = []

        try:
            url = "https://api.stackexchange.com/2.3/search/advanced"
            params = {
                'q': query,
                'site': 'stackoverflow',
                'pagesize': max_results,
            }

            response = requests.get(
                url,
                params=params,
                timeout=5
            )

            if response.status_code == 200:
                for item in response.json().get('items', []):
                    results.append(SearchResult(
                        title=item['title'],
                        url=item['link'],
                        source='forums',
                        summary=f"Answers: {item['answer_count']}",
                        date=datetime.fromtimestamp(
                            item['creation_date']
                        ).isoformat(),
                        upvotes=item['score'],
                    ))
        except Exception as e:
            logger.warning(f"Error searching Stack Overflow: {str(e)}")

        return results

    def _search_papers(
        self,
        query: str,
        max_results: int = 10
    ) -> List[SearchResult]:
        """Search academic papers (arXiv, OpenReview)"""
        results = []

        # arXiv
        try:
            import arxiv
            client = arxiv.Client()

            for paper in client.results(
                arxiv.Search(query=query, max_results=max_results)
            ):
                results.append(SearchResult(
                    title=paper.title,
                    url=paper.pdf_url,
                    source='papers',
                    summary=paper.summary[:200],
                    author=paper.authors[0].name if paper.authors else None,
                    date=paper.published.isoformat(),
                    upvotes=0,
                ))
        except Exception as e:
            logger.warning(f"Error searching arXiv: {str(e)}")

        return results

    def _score_results(
        self,
        results: List[SearchResult],
        recency_weight: float
    ) -> None:
        """Score results by recency and platform authority"""
        now = datetime.now()

        for result in results:
            # Base relevance
            relevance = 0.5

            # Platform authority
            platform_scores = {
                'papers': 0.9,
                'github': 0.8,
                'forums': 0.7,
                'blogs': 0.7,
                'reddit': 0.6,
            }
            relevance = platform_scores.get(result.source, 0.5)

            # Upvotes/popularity
            popularity_boost = min(result.upvotes / 100, 0.2)
            relevance += popularity_boost

            # Recency
            if result.date:
                try:
                    pub_date = datetime.fromisoformat(
                        result.date.replace('Z', '+00:00')
                    )
                    days_old = (now - pub_date).days
                    recency_score = 1.0 if days_old < 90 else 0.5
                    relevance += recency_score * recency_weight * 0.2
                except:
                    pass

            result.relevance_score = min(relevance, 1.0)

    @staticmethod
    def _suggest_subreddits(query: str) -> List[str]:
        """Suggest relevant subreddits for a query"""
        keyword_to_subs = {
            'python': ['learnprogramming', 'Python', 'Python_beginner'],
            'machine learning': ['MachineLearning', 'learnmachinelearning'],
            'web dev': ['webdev', 'frontend', 'node'],
            'job': ['jobs', 'careerguidance', 'findajob'],
            'adhd': ['ADHD', 'ADHD_Help', 'productivity'],
            'learning': ['learnprogramming', 'IWantToLearn', 'languagelearning'],
        }

        suggested = set()
        query_lower = query.lower()

        for keyword, subs in keyword_to_subs.items():
            if keyword in query_lower:
                suggested.update(subs)

        # Default subreddits
        if not suggested:
            suggested = {'learnprogramming', 'IWantToLearn', 'ADHD_Help'}

        return list(suggested)[:5]
