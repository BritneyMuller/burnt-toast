# =============================================================================
# ENHANCED LEGAL AI REDDIT ANALYSIS - Complete Engagement & Insights Analysis
# =============================================================================
# Analyzes legal subreddits with focus on:
# - AI tool concerns, questions, onboarding hurdles
# - Post type performance (questions, advice, discussions)
# - Best posting times and days
# - Engagement triggers
# - Trending topics
# - Formatted ASCII visualizations
# =============================================================================

# --- Install packages ---
!pip install praw pandas openai matplotlib seaborn wordcloud pytz --quiet

import os
import re
import time
import json
from collections import Counter, defaultdict
from typing import List, Dict, Any, Tuple
from datetime import datetime
import pytz

import praw
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from google.colab import userdata

# =========================
# SETUP
# =========================
os.environ['OPENAI_API_KEY'] = userdata.get('OPENAI_API_KEY')

from openai import OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

print("✅ API keys loaded from Colab secrets!")

# Configure analysis parameters
SUBREDDITS = [
    "legaltech",
    "Lawyertalk",
    "LawyersUsefulThings",
    "LawFirm",
    "AIForSmallBusiness"
]

POST_LIMIT_PER_SUBREDDIT = 100
COMMENT_LIMIT_PER_POST = 20

# Optional: Enable database logging
ENABLE_DATABASE = False  # Set to True to enable SQLite logging
DB_PATH = "legal_ai_analysis.db"

# =========================
# Reddit: Setup & Collection
# =========================
def setup_reddit():
    """Set up Reddit API connection using Colab secrets."""
    print("🔄 Setting up Reddit API connection...")
    try:
        reddit = praw.Reddit(
            client_id=userdata.get('REDDIT_CLIENT_ID'),
            client_secret=userdata.get('REDDIT_CLIENT_SECRET'),
            user_agent=userdata.get('REDDIT_USER_AGENT'),
            check_for_async=False,
        )
        reddit.read_only = True
        print("✅ Reddit connection successful")
        return reddit
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        return None


def collect_reddit_content_enhanced(reddit, subreddit_name, limit=100):
    """Collect posts and comments with enhanced metadata."""
    print(f"📥 Fetching from r/{subreddit_name} (limit={limit})...")
    content = []
    posts_data = []

    try:
        sr = reddit.subreddit(subreddit_name)
        for idx, sub in enumerate(sr.hot(limit=limit), 1):

            # Store post-level data
            post_data = {
                "post_id": sub.id,
                "title": sub.title or "",
                "permalink": f"https://reddit.com{sub.permalink}",
                "score": getattr(sub, "score", 0),
                "author": str(getattr(sub, "author", "deleted")),
                "created_utc": getattr(sub, "created_utc", 0),
                "subreddit": subreddit_name,
                "num_comments": getattr(sub, "num_comments", 0),
                "upvote_ratio": getattr(sub, "upvote_ratio", 0),
                "is_self": getattr(sub, "is_self", False),
                "link_flair_text": getattr(sub, "link_flair_text", ""),
            }
            posts_data.append(post_data)

            # Add title
            content.append({
                "type": "title",
                "text": sub.title or "",
                "post_id": sub.id,
                **post_data
            })

            # Add post body if exists
            if getattr(sub, "selftext", None):
                content.append({
                    "type": "post",
                    "text": sub.selftext,
                    "post_id": sub.id,
                    **post_data
                })

            # Add top comments
            try:
                sub.comments.replace_more(limit=0)
                for c in list(sub.comments)[:COMMENT_LIMIT_PER_POST]:
                    if getattr(c, "body", None):
                        content.append({
                            "type": "comment",
                            "text": c.body,
                            "post_id": sub.id,
                            "score": getattr(c, "score", 0),
                            "author": str(getattr(c, "author", "deleted")),
                            "created_utc": getattr(c, "created_utc", 0),
                            "subreddit": subreddit_name,
                            "num_comments": 0,
                            "permalink": f"https://reddit.com{sub.permalink}",
                        })
            except:
                pass

            if idx % 25 == 0:
                print(f"  • {idx} posts processed...")

        print(f"✅ Collected {len(content)} items from r/{subreddit_name}")
        return content, posts_data
    except Exception as e:
        print(f"❌ Error: {e}")
        return [], []


def collect_from_all_subreddits_enhanced(reddit, subreddits, limit_per_sub=100):
    """Collect content from all specified subreddits."""
    print(f"\n{'='*70}")
    print(f"📡 COLLECTING FROM {len(subreddits)} SUBREDDITS")
    print(f"{'='*70}\n")

    all_content = []
    all_posts = []

    for sub in subreddits:
        content, posts = collect_reddit_content_enhanced(reddit, sub, limit_per_sub)
        all_content.extend(content)
        all_posts.extend(posts)
        time.sleep(1)

    print(f"\n✅ Total: {len(all_content)} items, {len(all_posts)} posts from {len(subreddits)} subreddits")
    return all_content, all_posts


def clean_text(text: str) -> str:
    """Clean text by removing URLs and extra whitespace."""
    text = re.sub(r"http\S+", "", text or "")
    text = re.sub(r"\s+", " ", text).strip()
    return text


# =========================
# OpenAI Analysis - Enhanced
# =========================
def classify_post_types_batch(posts: List[Dict], batch_size: int = 20):
    """Classify post types using OpenAI."""
    if not posts:
        return []

    print(f"🤖 Classifying post types for {len(posts)} posts...")
    results = []

    for start in range(0, len(posts), batch_size):
        batch = posts[start:start + batch_size]
        numbered = "\n\n".join([
            f"[{i}] Title: {post['title'][:200]}"
            for i, post in enumerate(batch)
        ])

        system_prompt = (
            "You classify Reddit posts into categories based on their title and intent. "
            "Categories: QUESTION, ADVICE_REQUEST, DISCUSSION, SHOWCASE, NEWS, SEEKING_HELP, "
            "INFORMATIONAL, RECOMMENDATION, COMPLAINT, OTHER"
        )

        user_prompt = (
            f"Classify these Reddit post titles:\n\n{numbered}\n\n"
            'For each, return JSON with:\n'
            '{"post_type": "CATEGORY", "confidence": "high/medium/low"}\n\n'
            "Return a JSON object with key 'results' containing an array."
        )

        try:
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                temperature=0,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )

            raw = resp.choices[0].message.content
            data = json.loads(raw)
            items = data.get("results") or data.get("items") or [data]
            if not isinstance(items, list):
                items = [items]

            for item in items:
                if isinstance(item, dict):
                    results.append({
                        "post_type": item.get("post_type", "OTHER"),
                        "confidence": item.get("confidence", "low")
                    })

            while len(results) < start + len(batch):
                results.append({"post_type": "OTHER", "confidence": "low"})

            time.sleep(0.5)

        except Exception as e:
            print(f"  ⚠️ Batch error: {e}")
            results.extend([{"post_type": "OTHER", "confidence": "low"} for _ in batch])

    print(f"✅ Post type classification complete!")
    return results


def extract_ai_tools_and_concerns_batch(texts: List[str], batch_size: int = 15):
    """Extract AI tools WITH specific concerns, questions, and hurdles."""
    if not texts:
        return []

    print(f"🤖 Extracting AI tools and concerns from {len(texts)} items...")
    all_results = []

    for start in range(0, len(texts), batch_size):
        batch = texts[start:start + batch_size]
        numbered = "\n\n".join([f"[{i}] {t[:800]}" for i, t in enumerate(batch)])

        system_prompt = (
            "You analyze legal industry discussions about AI tools. Extract: "
            "(1) AI tool names, (2) specific concerns mentioned, (3) questions asked, "
            "(4) onboarding/implementation hurdles, (5) what they want to know or achieve."
        )

        user_prompt = (
            f"Analyze these legal industry posts:\n\n{numbered}\n\n"
            'For each, return JSON with:\n'
            '{"tools": ["tool1", "tool2"], '
            '"concerns": ["specific concern 1", "concern 2"], '
            '"questions": ["question 1", "question 2"], '
            '"hurdles": ["implementation challenge 1", "challenge 2"], '
            '"needs": ["what they want to achieve"]}\n\n'
            "Return a JSON object with key 'results' containing an array."
        )

        try:
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                temperature=0,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )

            raw = resp.choices[0].message.content
            data = json.loads(raw)
            items = data.get("results") or data.get("items") or [data]
            if not isinstance(items, list):
                items = [items]

            for item in items:
                if isinstance(item, dict):
                    all_results.append({
                        "tools": item.get("tools", []),
                        "concerns": item.get("concerns", []),
                        "questions": item.get("questions", []),
                        "hurdles": item.get("hurdles", []),
                        "needs": item.get("needs", [])
                    })

            while len(all_results) < start + len(batch):
                all_results.append({
                    "tools": [], "concerns": [], "questions": [],
                    "hurdles": [], "needs": []
                })

            time.sleep(0.5)

            if (start + batch_size) % 50 == 0:
                print(f"  • Processed {min(start + batch_size, len(texts))} items...")

        except Exception as e:
            print(f"  ⚠️ Batch error: {e}")
            all_results.extend([{
                "tools": [], "concerns": [], "questions": [],
                "hurdles": [], "needs": []
            } for _ in batch])

    print(f"✅ AI tool and concern extraction complete!")
    return all_results


def analyze_engagement_triggers_batch(high_engagement_posts: List[Dict], batch_size: int = 15):
    """Analyze what triggers high engagement."""
    if not high_engagement_posts:
        return []

    print(f"🤖 Analyzing engagement triggers for {len(high_engagement_posts)} posts...")
    results = []

    for start in range(0, len(high_engagement_posts), batch_size):
        batch = high_engagement_posts[start:start + batch_size]
        numbered = "\n\n".join([
            f"[{i}] Title: {post.get('title', '')[:300]} (Score: {post.get('score', 0)}, Comments: {post.get('num_comments', 0)})"
            for i, post in enumerate(batch)
        ])

        system_prompt = (
            "You analyze why certain Reddit posts get high engagement. "
            "Identify psychological triggers, content patterns, and topics that drive engagement."
        )

        user_prompt = (
            f"Analyze these high-engagement legal/AI posts:\n\n{numbered}\n\n"
            'For each, return JSON with:\n'
            '{"triggers": ["trigger1", "trigger2"], '
            '"appeal_factors": ["why this resonates"], '
            '"topic_angle": "how topic is framed"}\n\n'
            "Return a JSON object with key 'results' containing an array."
        )

        try:
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                temperature=0,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )

            raw = resp.choices[0].message.content
            data = json.loads(raw)
            items = data.get("results") or data.get("items") or [data]
            if not isinstance(items, list):
                items = [items]

            for item in items:
                if isinstance(item, dict):
                    results.append({
                        "triggers": item.get("triggers", []),
                        "appeal_factors": item.get("appeal_factors", []),
                        "topic_angle": item.get("topic_angle", "")
                    })

            while len(results) < start + len(batch):
                results.append({"triggers": [], "appeal_factors": [], "topic_angle": ""})

            time.sleep(0.5)

        except Exception as e:
            print(f"  ⚠️ Batch error: {e}")
            results.extend([{
                "triggers": [], "appeal_factors": [], "topic_angle": ""
            } for _ in batch])

    print(f"✅ Engagement trigger analysis complete!")
    return results


def analyze_sentiment_and_themes_enhanced(content_with_ai: List[Dict], batch_size: int = 15):
    """Enhanced sentiment and theme analysis."""
    if not content_with_ai:
        return []

    print(f"🤖 Analyzing sentiment, themes, and context for {len(content_with_ai)} items...")
    results = []

    for start in range(0, len(content_with_ai), batch_size):
        batch = content_with_ai[start:start + batch_size]
        numbered = "\n\n".join([
            f"[{i}] Tools: {', '.join(item.get('tools', [])[:5])}\nText: {item['text'][:600]}"
            for i, item in enumerate(batch)
        ])

        system_prompt = (
            "You analyze legal professional discussions about AI. Extract: "
            "sentiment, themes, professional role/context, pain points, use cases, and insightful quotes."
        )

        user_prompt = (
            f"Analyze these discussions:\n\n{numbered}\n\n"
            'For each, return JSON with:\n'
            '{"sentiment": "positive/negative/neutral/mixed", '
            '"themes": ["theme1", "theme2"], '
            '"role_context": "professional context", '
            '"pain_points": ["pain point 1"], '
            '"use_case": "what they want to use AI for", '
            '"quote": "most insightful quote"}\n\n'
            "Return a JSON object with key 'results' containing an array."
        )

        try:
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                temperature=0,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )

            raw = resp.choices[0].message.content
            data = json.loads(raw)
            items = data.get("results") or data.get("items") or [data]
            if not isinstance(items, list):
                items = [items]

            for item in items:
                if isinstance(item, dict):
                    results.append({
                        "sentiment": item.get("sentiment", "neutral"),
                        "themes": item.get("themes", []),
                        "role_context": item.get("role_context", ""),
                        "pain_points": item.get("pain_points", []),
                        "use_case": item.get("use_case", ""),
                        "quote": item.get("quote", "")
                    })

            while len(results) < start + len(batch):
                results.append({
                    "sentiment": "neutral", "themes": [], "role_context": "",
                    "pain_points": [], "use_case": "", "quote": ""
                })

            time.sleep(0.5)

        except Exception as e:
            print(f"  ⚠️ Batch error: {e}")
            results.extend([{
                "sentiment": "neutral", "themes": [], "role_context": "",
                "pain_points": [], "use_case": "", "quote": ""
            } for _ in batch])

    print(f"✅ Enhanced analysis complete!")
    return results


# =========================
# Temporal Analysis
# =========================
def analyze_temporal_patterns(posts: List[Dict]) -> Dict:
    """Analyze best posting times and days."""
    print(f"⏰ Analyzing temporal patterns...")

    # Convert UTC timestamps to readable times
    hour_performance = defaultdict(lambda: {"count": 0, "total_score": 0, "total_comments": 0})
    day_performance = defaultdict(lambda: {"count": 0, "total_score": 0, "total_comments": 0})

    day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    for post in posts:
        timestamp = post.get("created_utc", 0)
        if timestamp:
            dt = datetime.fromtimestamp(timestamp, tz=pytz.UTC)

            # Hour analysis (0-23)
            hour = dt.hour
            hour_performance[hour]["count"] += 1
            hour_performance[hour]["total_score"] += post.get("score", 0)
            hour_performance[hour]["total_comments"] += post.get("num_comments", 0)

            # Day analysis
            day = day_names[dt.weekday()]
            day_performance[day]["count"] += 1
            day_performance[day]["total_score"] += post.get("score", 0)
            day_performance[day]["total_comments"] += post.get("num_comments", 0)

    # Calculate averages and sort
    hour_stats = []
    for hour, stats in hour_performance.items():
        if stats["count"] > 0:
            hour_stats.append({
                "hour": hour,
                "count": stats["count"],
                "avg_score": stats["total_score"] / stats["count"],
                "avg_comments": stats["total_comments"] / stats["count"]
            })

    day_stats = []
    for day, stats in day_performance.items():
        if stats["count"] > 0:
            day_stats.append({
                "day": day,
                "count": stats["count"],
                "avg_score": stats["total_score"] / stats["count"],
                "avg_comments": stats["total_comments"] / stats["count"]
            })

    # Sort by count
    hour_stats.sort(key=lambda x: x["count"], reverse=True)
    day_stats.sort(key=lambda x: x["count"], reverse=True)

    print(f"✅ Temporal analysis complete!")
    return {
        "hours": hour_stats,
        "days": day_stats
    }


# =========================
# Main Analysis Function
# =========================
def analyze_legal_ai_enhanced(reddit, subreddits, post_limit=100):
    """Main enhanced analysis function."""

    print(f"\n{'='*70}")
    print(f"🔍 ENHANCED LEGAL AI ANALYSIS")
    print(f"{'='*70}\n")

    # Step 1: Collect all content
    all_content, all_posts = collect_from_all_subreddits_enhanced(reddit, subreddits, post_limit)

    if not all_content or not all_posts:
        print("❌ No content collected")
        return None

    # Step 2: Classify post types
    post_classifications = classify_post_types_batch(all_posts)
    for post, classification in zip(all_posts, post_classifications):
        post.update(classification)

    # Step 3: Extract AI tools and concerns
    texts = [clean_text(item["text"]) for item in all_content]
    ai_extractions = extract_ai_tools_and_concerns_batch(texts)

    # Step 4: Filter to AI-related content
    content_with_ai = []
    for item, extraction in zip(all_content, ai_extractions):
        if extraction["tools"] or extraction["concerns"] or extraction["questions"]:
            content_with_ai.append({
                **item,
                **extraction
            })

    print(f"\n📊 Found {len(content_with_ai)} AI-related items (out of {len(all_content)} total)")

    if not content_with_ai:
        print("⚠️ No AI mentions found")
        return None

    # Step 5: Analyze sentiment and themes
    sentiment_analysis = analyze_sentiment_and_themes_enhanced(content_with_ai)
    for item, analysis in zip(content_with_ai, sentiment_analysis):
        item.update(analysis)

    # Step 6: Analyze engagement triggers (top 20% posts by score)
    posts_with_ai = [item for item in content_with_ai if item.get("type") in ["title", "post"]]
    posts_with_ai.sort(key=lambda x: x.get("score", 0), reverse=True)
    top_posts = posts_with_ai[:max(10, len(posts_with_ai) // 5)]
    engagement_triggers = analyze_engagement_triggers_batch(top_posts)

    # Step 7: Temporal analysis
    ai_posts = [p for p in all_posts if p["post_id"] in [item.get("post_id") for item in content_with_ai]]
    temporal_patterns = analyze_temporal_patterns(ai_posts)

    # Step 8: Generate insights
    insights = generate_enhanced_insights(content_with_ai, all_posts, engagement_triggers, temporal_patterns)

    # Step 9: Print formatted results
    print_enhanced_insights(insights)

    # Step 10: Create visualizations
    create_enhanced_visualizations(insights, content_with_ai, all_posts)

    # Step 11: Optional database logging
    if ENABLE_DATABASE:
        save_to_database(content_with_ai, all_posts, insights)

    # Step 12: Export
    df_content = pd.DataFrame(content_with_ai)
    df_posts = pd.DataFrame(all_posts)

    return {
        "insights": insights,
        "content_data": content_with_ai,
        "posts_data": all_posts,
        "df_content": df_content,
        "df_posts": df_posts,
        "temporal": temporal_patterns
    }


# =========================
# Enhanced Insights Generation
# =========================
def generate_enhanced_insights(content_with_ai: List[Dict], all_posts: List[Dict],
                               engagement_triggers: List[Dict], temporal: Dict) -> Dict:
    """Generate comprehensive insights."""

    # AI Tools
    tool_counter = Counter()
    for item in content_with_ai:
        for tool in item.get("tools", []):
            tool_counter[tool.lower().strip()] += 1

    # Tool-specific concerns
    tool_concerns = defaultdict(list)
    for item in content_with_ai:
        for tool in item.get("tools", []):
            tool_key = tool.lower().strip()
            for concern in item.get("concerns", []):
                if concern:
                    tool_concerns[tool_key].append(concern)

    # All concerns
    concern_counter = Counter()
    for item in content_with_ai:
        for concern in item.get("concerns", []):
            if concern:
                concern_counter[concern.lower().strip()] += 1

    # Questions
    question_counter = Counter()
    for item in content_with_ai:
        for question in item.get("questions", []):
            if question:
                question_counter[question.lower().strip()] += 1

    # Onboarding hurdles
    hurdle_counter = Counter()
    for item in content_with_ai:
        for hurdle in item.get("hurdles", []):
            if hurdle:
                hurdle_counter[hurdle.lower().strip()] += 1

    # Audience needs
    need_counter = Counter()
    for item in content_with_ai:
        for need in item.get("needs", []):
            if need:
                need_counter[need.lower().strip()] += 1

    # Sentiment
    sentiment_counter = Counter([item.get("sentiment", "neutral") for item in content_with_ai])

    # Themes
    theme_counter = Counter()
    for item in content_with_ai:
        for theme in item.get("themes", []):
            theme_counter[theme.lower().strip()] += 1

    # Pain points
    pain_counter = Counter()
    for item in content_with_ai:
        for pain in item.get("pain_points", []):
            if pain:
                pain_counter[pain.lower().strip()] += 1

    # Subreddit distribution
    subreddit_counter = Counter([item.get("subreddit", "") for item in content_with_ai])

    # Post type performance
    post_type_stats = defaultdict(lambda: {"count": 0, "total_score": 0, "total_comments": 0})
    for post in all_posts:
        ptype = post.get("post_type", "OTHER")
        post_type_stats[ptype]["count"] += 1
        post_type_stats[ptype]["total_score"] += post.get("score", 0)
        post_type_stats[ptype]["total_comments"] += post.get("num_comments", 0)

    post_type_performance = []
    for ptype, stats in post_type_stats.items():
        if stats["count"] > 0:
            post_type_performance.append({
                "type": ptype,
                "count": stats["count"],
                "avg_score": stats["total_score"] / stats["count"],
                "avg_comments": stats["total_comments"] / stats["count"]
            })
    post_type_performance.sort(key=lambda x: x["count"], reverse=True)

    # Engagement triggers
    trigger_counter = Counter()
    for item in engagement_triggers:
        for trigger in item.get("triggers", []):
            if trigger:
                trigger_counter[trigger.lower().strip()] += 1

    return {
        "total_ai_mentions": len(content_with_ai),
        "top_tools": tool_counter.most_common(30),
        "tool_concerns": dict(tool_concerns),
        "top_concerns": concern_counter.most_common(20),
        "top_questions": question_counter.most_common(20),
        "top_hurdles": hurdle_counter.most_common(20),
        "audience_needs": need_counter.most_common(20),
        "sentiment_breakdown": dict(sentiment_counter),
        "top_themes": theme_counter.most_common(20),
        "top_pain_points": pain_counter.most_common(20),
        "subreddit_distribution": subreddit_counter.most_common(10),
        "post_type_performance": post_type_performance,
        "engagement_triggers": trigger_counter.most_common(20),
        "temporal": temporal
    }


# =========================
# ASCII Formatted Output
# =========================
def print_enhanced_insights(insights: Dict):
    """Print insights with beautiful ASCII formatting."""

    def create_bar(count, max_count, width=30):
        """Create an ASCII bar."""
        if max_count == 0:
            return ""
        filled = int((count / max_count) * width)
        return "█" * filled + "░" * (width - filled)

    print(f"\n{'='*70}")
    print(f"📊 ENHANCED LEGAL AI INSIGHTS REPORT")
    print(f"{'='*70}\n")

    # Most Active Subreddits
    print(f"🏆 MOST ACTIVE SUBREDDITS")
    print("-" * 70)
    max_count = insights['subreddit_distribution'][0][1] if insights['subreddit_distribution'] else 1
    for i, (sub, count) in enumerate(insights['subreddit_distribution'][:10], 1):
        bar = create_bar(count, max_count, 20)
        print(f"   {i}. r/{sub:<25} {bar} ({count} posts)")

    # Post Type Performance
    print(f"\n📝 POST TYPE PERFORMANCE")
    print("-" * 70)
    for post_type in insights['post_type_performance'][:10]:
        ptype = post_type['type'].replace('_', ' ')
        count = post_type['count']
        avg_score = int(post_type['avg_score'])
        avg_comments = int(post_type['avg_comments'])
        print(f"\n   {ptype.upper()}")
        print(f"      Count: {count} | Avg Score: {avg_score} | Avg Comments: {avg_comments}")

    # Best Posting Times
    print(f"\n⏰ BEST POSTING TIMES (UTC)")
    print("-" * 70)
    hours = insights['temporal']['hours'][:10]
    max_hour = hours[0]['count'] if hours else 1
    for hour_data in hours[:10]:
        hour = hour_data['hour']
        count = hour_data['count']
        bar = create_bar(count, max_hour, 15)
        time_str = f"{hour:02d}:00"
        print(f"   {time_str:<8} {bar}  ({count} posts)")

    # Most Active Days
    print(f"\n📅 MOST ACTIVE DAYS")
    print("-" * 70)
    days = insights['temporal']['days']
    max_day = days[0]['count'] if days else 1
    for day_data in days:
        day = day_data['day']
        count = day_data['count']
        bar = create_bar(count, max_day, 15)
        print(f"   {day:<12} {bar}  ({count} posts)")

    # Top AI Tools
    print(f"\n🤖 TOP AI TOOLS MENTIONED")
    print("-" * 70)
    max_tools = insights['top_tools'][0][1] if insights['top_tools'] else 1
    for i, (tool, count) in enumerate(insights['top_tools'][:15], 1):
        bar = create_bar(count, max_tools, 12)
        print(f"   {i:2d}. {tool:<35} {bar} ({count}x)")

    # Top Themes
    print(f"\n💡 TOP THEMES & TOPICS")
    print("-" * 70)
    max_themes = insights['top_themes'][0][1] if insights['top_themes'] else 1
    for i, (theme, count) in enumerate(insights['top_themes'][:15], 1):
        bar = create_bar(count, max_themes, 12)
        print(f"   {i:2d}. {theme:<40} {bar} ({count}x)")

    # AI Tool Concerns
    print(f"\n⚠️  TOP AI TOOL CONCERNS")
    print("-" * 70)
    for i, (concern, count) in enumerate(insights['top_concerns'][:15], 1):
        print(f"   {i:2d}. {concern} ({count}x mentions)")

    # Common Questions
    print(f"\n❓ COMMON QUESTIONS ABOUT AI")
    print("-" * 70)
    for i, (question, count) in enumerate(insights['top_questions'][:12], 1):
        print(f"   {i:2d}. {question} ({count}x mentions)")

    # Onboarding Hurdles
    print(f"\n🚧 ONBOARDING & IMPLEMENTATION HURDLES")
    print("-" * 70)
    for i, (hurdle, count) in enumerate(insights['top_hurdles'][:12], 1):
        print(f"   {i:2d}. {hurdle} ({count}x mentions)")

    # Pain Points
    print(f"\n⚠️  COMMON PAIN POINTS")
    print("-" * 70)
    for i, (pain, count) in enumerate(insights['top_pain_points'][:12], 1):
        print(f"   {i:2d}. {pain} ({count}x mentions)")

    # Audience Needs
    print(f"\n🎯 AUDIENCE NEEDS")
    print("-" * 70)
    for i, (need, count) in enumerate(insights['audience_needs'][:15], 1):
        print(f"   {i:2d}. {need} ({count}x mentions)")

    # Engagement Triggers
    print(f"\n🚀 ENGAGEMENT TRIGGERS")
    print("-" * 70)
    for i, (trigger, count) in enumerate(insights['engagement_triggers'][:15], 1):
        print(f"   {i:2d}. {trigger} ({count}x mentions)")

    # Sentiment
    print(f"\n💭 SENTIMENT BREAKDOWN")
    print("-" * 70)
    total_sent = sum(insights['sentiment_breakdown'].values())
    for sent, count in insights['sentiment_breakdown'].items():
        pct = (count / total_sent * 100) if total_sent > 0 else 0
        emoji = {"positive": "😊", "negative": "😞", "neutral": "😐", "mixed": "🤔"}.get(sent, "")
        bar = create_bar(count, total_sent, 20)
        print(f"  {emoji} {sent.capitalize():<10} {bar} {count} ({pct:.1f}%)")

    print(f"\n{'='*70}\n")


# =========================
# Enhanced Visualizations
# =========================
def create_enhanced_visualizations(insights: Dict, content_with_ai: List[Dict], all_posts: List[Dict]):
    """Create comprehensive visualizations."""

    print(f"\n📊 Creating enhanced visualizations...")

    sns.set_style("whitegrid")
    fig = plt.figure(figsize=(24, 18))

    # 1. Subreddit Distribution
    ax1 = plt.subplot(4, 4, 1)
    subs = [s[0] for s in insights['subreddit_distribution'][:8]]
    counts = [s[1] for s in insights['subreddit_distribution'][:8]]
    ax1.bar(range(len(subs)), counts, color='#3498db')
    ax1.set_xticks(range(len(subs)))
    ax1.set_xticklabels([f"r/{s}" for s in subs], rotation=45, ha='right', fontsize=9)
    ax1.set_title('Most Active Subreddits', fontweight='bold')
    ax1.set_ylabel('AI-Related Posts')

    # 2. Post Type Performance (by count)
    ax2 = plt.subplot(4, 4, 2)
    ptypes = [p['type'].replace('_', ' ') for p in insights['post_type_performance'][:8]]
    pcounts = [p['count'] for p in insights['post_type_performance'][:8]]
    ax2.barh(range(len(ptypes)), pcounts, color='#e74c3c')
    ax2.set_yticks(range(len(ptypes)))
    ax2.set_yticklabels(ptypes, fontsize=9)
    ax2.set_title('Post Types by Count', fontweight='bold')
    ax2.set_xlabel('Number of Posts')
    ax2.invert_yaxis()

    # 3. Post Type Avg Score
    ax3 = plt.subplot(4, 4, 3)
    avg_scores = [p['avg_score'] for p in insights['post_type_performance'][:8]]
    ax3.barh(range(len(ptypes)), avg_scores, color='#2ecc71')
    ax3.set_yticks(range(len(ptypes)))
    ax3.set_yticklabels(ptypes, fontsize=9)
    ax3.set_title('Avg Score by Post Type', fontweight='bold')
    ax3.set_xlabel('Average Score')
    ax3.invert_yaxis()

    # 4. Posting Time Distribution
    ax4 = plt.subplot(4, 4, 4)
    hours = [h['hour'] for h in insights['temporal']['hours']]
    hour_counts = [h['count'] for h in insights['temporal']['hours']]
    ax4.bar(hours, hour_counts, color='#9b59b6')
    ax4.set_title('Posting Time Distribution (UTC)', fontweight='bold')
    ax4.set_xlabel('Hour of Day')
    ax4.set_ylabel('Number of Posts')
    ax4.set_xticks(range(0, 24, 2))

    # 5. Day of Week
    ax5 = plt.subplot(4, 4, 5)
    days = [d['day'] for d in insights['temporal']['days']]
    day_counts = [d['count'] for d in insights['temporal']['days']]
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    days_sorted = sorted(zip(days, day_counts), key=lambda x: day_order.index(x[0]))
    days, day_counts = zip(*days_sorted) if days_sorted else ([], [])
    ax5.bar(range(len(days)), day_counts, color='#e67e22')
    ax5.set_xticks(range(len(days)))
    ax5.set_xticklabels([d[:3] for d in days], fontsize=9)
    ax5.set_title('Most Active Days', fontweight='bold')
    ax5.set_ylabel('Number of Posts')

    # 6. Top AI Tools
    ax6 = plt.subplot(4, 4, 6)
    tools = [t[0] for t in insights['top_tools'][:12]]
    tool_counts = [t[1] for t in insights['top_tools'][:12]]
    ax6.barh(range(len(tools)), tool_counts, color='#1abc9c')
    ax6.set_yticks(range(len(tools)))
    ax6.set_yticklabels(tools, fontsize=8)
    ax6.set_title('Top 12 AI Tools Mentioned', fontweight='bold')
    ax6.set_xlabel('Mentions')
    ax6.invert_yaxis()

    # 7. Sentiment Distribution
    ax7 = plt.subplot(4, 4, 7)
    sentiments = list(insights['sentiment_breakdown'].keys())
    sent_counts = list(insights['sentiment_breakdown'].values())
    colors_sent = {'positive': '#2ecc71', 'negative': '#e74c3c', 'neutral': '#95a5a6', 'mixed': '#f39c12'}
    pie_colors = [colors_sent.get(s, '#95a5a6') for s in sentiments]
    ax7.pie(sent_counts, labels=sentiments, autopct='%1.1f%%', colors=pie_colors, startangle=90)
    ax7.set_title('Sentiment Distribution', fontweight='bold')

    # 8. Top Themes
    ax8 = plt.subplot(4, 4, 8)
    themes = [t[0][:30] for t in insights['top_themes'][:12]]
    theme_counts = [t[1] for t in insights['top_themes'][:12]]
    ax8.barh(range(len(themes)), theme_counts, color='#3498db')
    ax8.set_yticks(range(len(themes)))
    ax8.set_yticklabels(themes, fontsize=8)
    ax8.set_title('Top 12 Themes', fontweight='bold')
    ax8.set_xlabel('Mentions')
    ax8.invert_yaxis()

    # 9. Top Concerns
    ax9 = plt.subplot(4, 4, 9)
    concerns = [c[0][:35] for c in insights['top_concerns'][:10]]
    concern_counts = [c[1] for c in insights['top_concerns'][:10]]
    ax9.barh(range(len(concerns)), concern_counts, color='#e74c3c')
    ax9.set_yticks(range(len(concerns)))
    ax9.set_yticklabels(concerns, fontsize=7)
    ax9.set_title('Top 10 AI Concerns', fontweight='bold')
    ax9.set_xlabel('Mentions')
    ax9.invert_yaxis()

    # 10. Onboarding Hurdles
    ax10 = plt.subplot(4, 4, 10)
    hurdles = [h[0][:35] for h in insights['top_hurdles'][:10]]
    hurdle_counts = [h[1] for h in insights['top_hurdles'][:10]]
    ax10.barh(range(len(hurdles)), hurdle_counts, color='#f39c12')
    ax10.set_yticks(range(len(hurdles)))
    ax10.set_yticklabels(hurdles, fontsize=7)
    ax10.set_title('Top 10 Onboarding Hurdles', fontweight='bold')
    ax10.set_xlabel('Mentions')
    ax10.invert_yaxis()

    # 11. Audience Needs
    ax11 = plt.subplot(4, 4, 11)
    needs = [n[0][:35] for n in insights['audience_needs'][:10]]
    need_counts = [n[1] for n in insights['audience_needs'][:10]]
    ax11.barh(range(len(needs)), need_counts, color='#27ae60')
    ax11.set_yticks(range(len(needs)))
    ax11.set_yticklabels(needs, fontsize=7)
    ax11.set_title('Top 10 Audience Needs', fontweight='bold')
    ax11.set_xlabel('Mentions')
    ax11.invert_yaxis()

    # 12. Engagement Triggers
    ax12 = plt.subplot(4, 4, 12)
    triggers = [t[0][:35] for t in insights['engagement_triggers'][:10]]
    trigger_counts = [t[1] for t in insights['engagement_triggers'][:10]]
    ax12.barh(range(len(triggers)), trigger_counts, color='#9b59b6')
    ax12.set_yticks(range(len(triggers)))
    ax12.set_yticklabels(triggers, fontsize=7)
    ax12.set_title('Top 10 Engagement Triggers', fontweight='bold')
    ax12.set_xlabel('Mentions')
    ax12.invert_yaxis()

    # 13. Questions Word Cloud
    ax13 = plt.subplot(4, 4, 13)
    question_text = " ".join([q for q, count in insights['top_questions'] for _ in range(count)])
    if question_text.strip():
        wordcloud = WordCloud(width=400, height=300, background_color='white',
                             colormap='Reds').generate(question_text)
        ax13.imshow(wordcloud, interpolation='bilinear')
    ax13.axis('off')
    ax13.set_title('Common Questions (Word Cloud)', fontweight='bold')

    # 14. Theme Word Cloud
    ax14 = plt.subplot(4, 4, 14)
    theme_text = " ".join([theme for theme, count in insights['top_themes'] for _ in range(count)])
    if theme_text.strip():
        wordcloud = WordCloud(width=400, height=300, background_color='white',
                             colormap='viridis').generate(theme_text)
        ax14.imshow(wordcloud, interpolation='bilinear')
    ax14.axis('off')
    ax14.set_title('Themes (Word Cloud)', fontweight='bold')

    # 15. Avg Comments by Post Type
    ax15 = plt.subplot(4, 4, 15)
    avg_comments = [p['avg_comments'] for p in insights['post_type_performance'][:8]]
    ax15.barh(range(len(ptypes)), avg_comments, color='#16a085')
    ax15.set_yticks(range(len(ptypes)))
    ax15.set_yticklabels(ptypes, fontsize=9)
    ax15.set_title('Avg Comments by Post Type', fontweight='bold')
    ax15.set_xlabel('Average Comments')
    ax15.invert_yaxis()

    # 16. Pain Points
    ax16 = plt.subplot(4, 4, 16)
    pains = [p[0][:35] for p in insights['top_pain_points'][:10]]
    pain_counts = [p[1] for p in insights['top_pain_points'][:10]]
    ax16.barh(range(len(pains)), pain_counts, color='#c0392b')
    ax16.set_yticks(range(len(pains)))
    ax16.set_yticklabels(pains, fontsize=7)
    ax16.set_title('Top 10 Pain Points', fontweight='bold')
    ax16.set_xlabel('Mentions')
    ax16.invert_yaxis()

    plt.tight_layout()
    plt.show()

    print("✅ Visualizations complete!")


# =========================
# Database Logging (Optional)
# =========================
def save_to_database(content_with_ai: List[Dict], all_posts: List[Dict], insights: Dict):
    """Save results to SQLite database."""
    import sqlite3
    from datetime import datetime

    print(f"\n💾 Saving to database: {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analysis_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_date TIMESTAMP,
            total_items INTEGER,
            total_posts INTEGER,
            ai_items INTEGER
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ai_content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER,
            type TEXT,
            text TEXT,
            score INTEGER,
            author TEXT,
            subreddit TEXT,
            sentiment TEXT,
            created_utc INTEGER,
            permalink TEXT,
            FOREIGN KEY (run_id) REFERENCES analysis_runs(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ai_tools (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER,
            tool_name TEXT,
            mention_count INTEGER,
            FOREIGN KEY (run_id) REFERENCES analysis_runs(id)
        )
    ''')

    # Insert run
    cursor.execute('''
        INSERT INTO analysis_runs (run_date, total_items, total_posts, ai_items)
        VALUES (?, ?, ?, ?)
    ''', (datetime.now(), len(content_with_ai), len(all_posts), insights['total_ai_mentions']))

    run_id = cursor.lastrowid

    # Insert content
    for item in content_with_ai[:1000]:  # Limit to prevent huge DB
        cursor.execute('''
            INSERT INTO ai_content (run_id, type, text, score, author, subreddit, sentiment, created_utc, permalink)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            run_id,
            item.get('type', ''),
            item.get('text', '')[:5000],  # Truncate long text
            item.get('score', 0),
            item.get('author', ''),
            item.get('subreddit', ''),
            item.get('sentiment', ''),
            item.get('created_utc', 0),
            item.get('permalink', '')
        ))

    # Insert tools
    for tool, count in insights['top_tools']:
        cursor.execute('''
            INSERT INTO ai_tools (run_id, tool_name, mention_count)
            VALUES (?, ?, ?)
        ''', (run_id, tool, count))

    conn.commit()
    conn.close()

    print(f"✅ Saved to database (Run ID: {run_id})")


# =========================
# Export Enhanced Results
# =========================
def export_enhanced_results(results: Dict, prefix: str = "legal_ai_enhanced"):
    """Export all results to CSV files."""

    print(f"\n💾 Exporting results...")

    # Main datasets
    results['df_content'].to_csv(f"{prefix}_content.csv", index=False)
    results['df_posts'].to_csv(f"{prefix}_posts.csv", index=False)

    # Insights
    insights = results['insights']

    pd.DataFrame(insights['top_tools'], columns=['Tool', 'Mentions']).to_csv(
        f"{prefix}_tools.csv", index=False)

    pd.DataFrame(insights['top_concerns'], columns=['Concern', 'Mentions']).to_csv(
        f"{prefix}_concerns.csv", index=False)

    pd.DataFrame(insights['top_questions'], columns=['Question', 'Mentions']).to_csv(
        f"{prefix}_questions.csv", index=False)

    pd.DataFrame(insights['top_hurdles'], columns=['Hurdle', 'Mentions']).to_csv(
        f"{prefix}_hurdles.csv", index=False)

    pd.DataFrame(insights['audience_needs'], columns=['Need', 'Mentions']).to_csv(
        f"{prefix}_needs.csv", index=False)

    pd.DataFrame(insights['post_type_performance']).to_csv(
        f"{prefix}_post_types.csv", index=False)

    pd.DataFrame(insights['engagement_triggers'], columns=['Trigger', 'Mentions']).to_csv(
        f"{prefix}_engagement_triggers.csv", index=False)

    # Temporal
    pd.DataFrame(insights['temporal']['hours']).to_csv(
        f"{prefix}_posting_hours.csv", index=False)

    pd.DataFrame(insights['temporal']['days']).to_csv(
        f"{prefix}_posting_days.csv", index=False)

    print(f"✅ Exported {9} CSV files!")


# =========================
# RUN ENHANCED ANALYSIS
# =========================
print("\n" + "="*70)
print("🚀 ENHANCED LEGAL AI REDDIT ANALYSIS")
print("="*70 + "\n")

reddit = setup_reddit()

if reddit:
    results = analyze_legal_ai_enhanced(
        reddit=reddit,
        subreddits=SUBREDDITS,
        post_limit=POST_LIMIT_PER_SUBREDDIT
    )

    if results:
        # Export results
        export_enhanced_results(results)

        print("\n✅ ENHANCED ANALYSIS COMPLETE!")
        print("\n💡 Access data with:")
        print("   • results['df_content'] - Content DataFrame")
        print("   • results['df_posts'] - Posts DataFrame")
        print("   • results['insights'] - All insights dict")
        print("   • results['temporal'] - Temporal patterns")
    else:
        print("\n⚠️ Analysis failed")
else:
    print("\n❌ Could not connect to Reddit")
