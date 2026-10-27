import os
import re
from dataclasses import dataclass
from typing import Optional

import anthropic
from pydantic import BaseModel

from app.news.feeds import TOPIC_LABELS
from app.news.ranker import StoryCluster

MODEL = os.getenv("NEWS_MODEL", "claude-haiku-5-5")
CANDIDATES_PER_TOPIC = 30
HIGHLIGHTS_PER_TOPIC = 6

SYSTEM_PROMPT = f"""You are the editor of Tap In, a daily news briefing for people who don't use social media.
Readers want to know what everyone is talking about without scrolling a feed.

You receive candidate stories for one section, each with an id, how many outlets covered it, the
headlines they used, and a short snippet. Pick the {HIGHLIGHTS_PER_TOPIC} most important stories
(fewer if there aren't that many worth it), most important first, and write each one up:

- headline: plain words, at most 12 words, no clickbait, no puns.
- gist: two short sentences, at most 45 words. Assume the reader has missed everything: say who
  people are ("Taylor Swift, the pop star") and what happened.
- why_it_matters: one sentence, at most 25 words, on why a normal person might care.
- story_ids: every candidate id that is about this same story.

Prefer stories covered by more outlets. Skip quizzes, listicles, shopping deals, horoscopes and ads.
Use only facts in the provided material; never invent details. For the culture section, a meme or
slang term counts as a story: explain what it is and where it came from."""


class HighlightDraft(BaseModel):
    story_ids: list[int]
    headline: str
    gist: str
    why_it_matters: str


class TopicEdition(BaseModel):
    highlights: list[HighlightDraft]


@dataclass
class WrittenHighlight:
    title: str
    gist: str
    why_it_matters: Optional[str]
    sources: list[dict]
    coverage: int


def _sources(clusters: list[StoryCluster]) -> list[dict]:
    seen, sources = set(), []
    for cluster in clusters:
        for article in cluster.articles:
            if article.source not in seen:
                seen.add(article.source)
                sources.append({"name": article.source, "url": article.url})
    return sources


def _describe(idx: int, cluster: StoryCluster) -> str:
    outlets = ", ".join(sorted(cluster.sources))
    headlines = "\n".join(f'  - "{a.title}"' for a in cluster.articles[:3])
    snippet = next((a.summary for a in cluster.articles if a.summary), "")
    return f"[{idx}] covered by {cluster.coverage} outlet(s): {outlets}\n{headlines}\n  snippet: {snippet}"


LISTICLE = re.compile(
    r"^\d+\s|\b\d+\s+(?:\w+\s+)?(?:things|products|times|photos|tweets|ways|reasons|ideas|costumes|details|people)\b"
    r"|\bquiz\b|\bdeals?\b|\bhoroscope|people are sharing",
    re.IGNORECASE,
)


def _fallback(clusters: list[StoryCluster]) -> list[WrittenHighlight]:
    """Without Claude, use the top-ranked stories as-is so the site still has content."""
    highlights = []
    for cluster in clusters:
        if len(highlights) == HIGHLIGHTS_PER_TOPIC:
            break
        lead = cluster.articles[0]
        if LISTICLE.search(lead.title):
            continue
        highlights.append(
            WrittenHighlight(
                title=lead.title,
                gist=lead.summary or lead.title,
                why_it_matters=None,
                sources=_sources([cluster]),
                coverage=cluster.coverage,
            )
        )
    return highlights


class Summarizer:
    def __init__(self):
        self.client: Optional[anthropic.Anthropic] = None
        # The SDK only notices missing credentials when a request is sent, so check up front.
        if not (os.getenv("ANTHROPIC_API_KEY") or os.getenv("ANTHROPIC_AUTH_TOKEN")):
            print("⚠️  ANTHROPIC_API_KEY not set; using unsummarized headlines")
            return
        try:
            self.client = anthropic.Anthropic()
        except anthropic.AnthropicError as e:
            print(f"⚠️  Claude unavailable ({e}); using unsummarized headlines")

    def write_topic(self, topic: str, clusters: list[StoryCluster]) -> list[WrittenHighlight]:
        candidates = clusters[:CANDIDATES_PER_TOPIC]
        if not candidates:
            return []
        if self.client is None:
            return _fallback(candidates)

        stories = "\n\n".join(_describe(i, c) for i, c in enumerate(candidates))
        try:
            response = self.client.messages.parse(
                model=MODEL,
                max_tokens=16000,
                system=SYSTEM_PROMPT,
                output_config={"effort": "medium"},
                output_format=TopicEdition,
                messages=[
                    {
                        "role": "user",
                        "content": f"Section: {TOPIC_LABELS[topic]}\n\nCandidate stories:\n\n{stories}",
                    }
                ],
            )
        except anthropic.AuthenticationError:
            print("⚠️  Claude rejected the API key; using unsummarized headlines from now on")
            self.client = None
            return _fallback(candidates)
        except (anthropic.APIStatusError, anthropic.APIConnectionError) as e:
            print(f"⚠️  Claude request for {topic} failed ({e}); using unsummarized headlines")
            return _fallback(candidates)

        if response.stop_reason == "refusal" or response.parsed_output is None:
            print(f"⚠️  Claude returned no edition for {topic} ({response.stop_reason})")
            return _fallback(candidates)

        highlights = []
        for draft in response.parsed_output.highlights[:HIGHLIGHTS_PER_TOPIC]:
            picked = [candidates[i] for i in dict.fromkeys(draft.story_ids) if 0 <= i < len(candidates)]
            if not picked:
                continue
            sources = _sources(picked)
            highlights.append(
                WrittenHighlight(
                    title=draft.headline,
                    gist=draft.gist,
                    why_it_matters=draft.why_it_matters,
                    sources=sources,
                    coverage=len(sources),
                )
            )
        return highlights
