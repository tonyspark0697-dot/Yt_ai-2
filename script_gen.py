"""Step 2: turn the trend report into a script + title + description + hashtags with Claude."""
import json

import anthropic

import config

CATEGORIES = "22 People&Blogs, 24 Entertainment, 27 Education, 28 Science&Tech, 26 Howto&Style, 25 News, 17 Sports, 20 Gaming, 10 Music"


def _extract_json(text: str) -> dict:
    return json.loads(text[text.find("{"): text.rfind("}") + 1])


def generate(report: dict, past_topics: list[str]) -> dict:
    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
    length = "35-45 seconds (about 95-115 words in total, 6-8 scenes)" if config.SHORTS \
        else "4-5 minutes (about 600-750 words in total, 10-14 scenes)"
    niche = f"Stay inside this niche: {config.NICHE_HINT}." if config.NICHE_HINT else \
        "Pick the niche and topic that the trend data suggests has the most momentum."

    prompt = f"""You are a YouTube growth strategist and scriptwriter.

Today's trending data (region {config.REGION}):
- Top hashtags: {report['top_hashtags']}
- Top tags: {report['top_tags']}
- Top trending titles: {report['top_titles']}

{niche}
Do NOT repeat these earlier topics: {past_topics[-30:]}

Write ONE original, factually accurate video in {config.LANGUAGE}. Length: {length}.
Rules:
- Strong hook in the first sentence, clear payoff, a short call to action at the end.
- No invented statistics, no fake quotes, no claims about real people you cannot back up.
- Title under 70 characters, curiosity-driven but not misleading.
- Use 3-5 hashtags taken from or inspired by the trend data, relevant to the topic.
- visual_query = 2-3 English words describing stock footage for that scene.
- category_id must be one of: {CATEGORIES}

Return ONLY JSON:
{{"topic": "...", "title": "...", "description": "2-3 sentence description",
 "hashtags": ["tag1", "tag2"], "tags": ["keyword1", "keyword2"], "category_id": "27",
 "scenes": [{{"narration": "...", "visual_query": "..."}}]}}"""

    msg = client.messages.create(
        model=config.MODEL,
        max_tokens=3000,
        messages=[{"role": "user", "content": prompt}],
    )
    data = _extract_json(msg.content[0].text)
    if not data.get("scenes"):
        raise ValueError("Claude returned no scenes")
    return data
