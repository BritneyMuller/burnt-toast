# =============================================================================
# LEGAL AI REDDIT ANALYSIS - AI Tools & Sentiment Analysis
# =============================================================================
# Analyzes legal subreddits to surface AI tool discussions, sentiment,
# themes, and positioning insights for legal tech startups
# =============================================================================

# --- Install packages ---
!pip install praw pandas openai matplotlib seaborn wordcloud --quiet

import os
import re
import time
import json
from collections import Counter, defaultdict
from typing import List, Dict, Any, Tuple

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

POST_LIMIT_PER_SUBREDDIT = 100  # Adjust based on needs
COMMENT_LIMIT_PER_POST = 20

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


def collect_reddit_content(reddit, subreddit_name, limit=100):
    """Collect posts and comments from a subreddit with author tracking."""
    print(f"📥 Fetching from r/{subreddit_name} (limit={limit})...")
    content = []

    try:
        sr = reddit.subreddit(subreddit_name)
        for idx, sub in enumerate(sr.hot(limit=limit), 1):
            # Add title
            content.append({
                "type": "title",
                "text": sub.title or "",
                "permalink": f"https://reddit.com{sub.permalink}",
                "score": getattr(sub, "score", 0),
                "author": str(getattr(sub, "author", "deleted")),
                "created_utc": getattr(sub, "created_utc", 0),
                "subreddit": subreddit_name,
                "num_comments": getattr(sub, "num_comments", 0),
            })

            # Add post body if exists
            if getattr(sub, "selftext", None):
                content.append({
                    "type": "post",
                    "text": sub.selftext,
                    "permalink": f"https://reddit.com{sub.permalink}",
                    "score": getattr(sub, "score", 0),
                    "author": str(getattr(sub, "author", "deleted")),
                    "created_utc": getattr(sub, "created_utc", 0),
                    "subreddit": subreddit_name,
                    "num_comments": getattr(sub, "num_comments", 0),
                })

            # Add top comments
            try:
                sub.comments.replace_more(limit=0)
                for c in list(sub.comments)[:COMMENT_LIMIT_PER_POST]:
                    if getattr(c, "body", None):
                        content.append({
                            "type": "comment",
                            "text": c.body,
                            "permalink": f"https://reddit.com{sub.permalink}",
                            "score": getattr(c, "score", 0),
                            "author": str(getattr(c, "author", "deleted")),
                            "created_utc": getattr(c, "created_utc", 0),
                            "subreddit": subreddit_name,
                            "num_comments": 0,
                        })
            except:
                pass

            if idx % 25 == 0:
                print(f"  • {idx} posts processed...")

        print(f"✅ Collected {len(content)} items from r/{subreddit_name}")
        return content
    except Exception as e:
        print(f"❌ Error: {e}")
        return []


def collect_from_all_subreddits(reddit, subreddits, limit_per_sub=100):
    """Collect content from all specified subreddits."""
    print(f"\n{'='*70}")
    print(f"📡 COLLECTING FROM {len(subreddits)} SUBREDDITS")
    print(f"{'='*70}\n")

    all_content = []
    for sub in subreddits:
        content = collect_reddit_content(reddit, sub, limit_per_sub)
        all_content.extend(content)
        time.sleep(1)  # Be nice to Reddit API

    print(f"\n✅ Total collected: {len(all_content)} items from {len(subreddits)} subreddits")
    return all_content


def clean_text(text: str) -> str:
    """Clean text by removing URLs and extra whitespace."""
    text = re.sub(r"http\S+", "", text or "")
    text = re.sub(r"\s+", " ", text).strip()
    return text


# =========================
# OpenAI Analysis - AI Tool Detection
# =========================
def extract_ai_tools_batch(texts: List[str], batch_size: int = 20):
    """Extract AI tools mentioned in Reddit content using OpenAI."""
    if not texts:
        return []

    print(f"🤖 Extracting AI tool mentions from {len(texts)} items...")
    all_tools = []

    for start in range(0, len(texts), batch_size):
        batch = texts[start:start + batch_size]
        numbered = "\n\n".join([f"[{i}] {t[:800]}" for i, t in enumerate(batch)])

        system_prompt = (
            "You are an expert at identifying AI tools, platforms, and services mentioned in legal industry discussions. "
            "Extract all AI tools, software, platforms, and services mentioned. Include specific product names, "
            "company names (if they make AI tools), and generic AI categories (e.g., 'AI legal research', 'contract AI')."
        )

        user_prompt = (
            f"Analyze these legal industry Reddit posts and extract ALL AI tools, platforms, or services mentioned:\n\n{numbered}\n\n"
            'For each post, return JSON with:\n'
            '{"tools": ["tool1", "tool2", ...], "context": "brief context of how AI was discussed"}\n\n'
            "Return a JSON object with key 'results' containing an array of these objects."
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

            # Handle different response formats
            items = data.get("results") or data.get("items") or data.get("analyses") or [data]
            if not isinstance(items, list):
                items = [items]

            for item in items:
                if isinstance(item, dict) and item.get("tools"):
                    all_tools.append({
                        "tools": item.get("tools", []),
                        "context": item.get("context", "")
                    })

            # Pad to match input length
            while len(all_tools) < start + len(batch):
                all_tools.append({"tools": [], "context": ""})

            time.sleep(0.5)  # Rate limiting

            if (start + batch_size) % 100 == 0:
                print(f"  • Processed {min(start + batch_size, len(texts))} items...")

        except Exception as e:
            print(f"  ⚠️ Batch error: {e}")
            # Add empty results for failed batch
            all_tools.extend([{"tools": [], "context": ""} for _ in batch])

    print(f"✅ AI tool extraction complete!")
    return all_tools


def analyze_ai_sentiment_and_themes(content_with_ai: List[Dict], batch_size: int = 15):
    """Analyze sentiment and themes around AI tool discussions."""
    if not content_with_ai:
        return []

    print(f"🤖 Analyzing sentiment and themes for {len(content_with_ai)} AI-related items...")
    results = []

    for start in range(0, len(content_with_ai), batch_size):
        batch = content_with_ai[start:start + batch_size]

        # Create numbered list with tool context
        numbered = "\n\n".join([
            f"[{i}] Tools: {', '.join(item['ai_tools'][:5])}\nText: {item['text'][:600]}"
            for i, item in enumerate(batch)
        ])

        system_prompt = (
            "You analyze legal professional discussions about AI tools. "
            "Identify: (1) sentiment toward AI (positive/negative/neutral/mixed), "
            "(2) key themes (e.g., efficiency, concerns about accuracy, cost, implementation challenges, use cases), "
            "(3) professional role/context if mentioned (e.g., solo practitioner, large firm, in-house counsel), "
            "(4) specific pain points or needs expressed."
        )

        user_prompt = (
            f"Analyze these legal professionals' discussions about AI:\n\n{numbered}\n\n"
            'For each, return JSON with:\n'
            '{"sentiment": "positive/negative/neutral/mixed", '
            '"themes": ["theme1", "theme2"], '
            '"role_context": "professional context if mentioned", '
            '"pain_points": ["pain point 1", "pain point 2"], '
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

            items = data.get("results") or data.get("items") or data.get("analyses") or [data]
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

            # Pad if needed
            while len(results) < start + len(batch):
                results.append({
                    "sentiment": "neutral",
                    "themes": [],
                    "role_context": "",
                    "pain_points": [],
                    "use_case": "",
                    "quote": ""
                })

            time.sleep(0.5)

            if (start + batch_size) % 50 == 0:
                print(f"  • Analyzed {min(start + batch_size, len(content_with_ai))} items...")

        except Exception as e:
            print(f"  ⚠️ Batch error: {e}")
            results.extend([{
                "sentiment": "neutral",
                "themes": [],
                "role_context": "",
                "pain_points": [],
                "use_case": "",
                "quote": ""
            } for _ in batch])

    print(f"✅ Sentiment and theme analysis complete!")
    return results


# =========================
# Analysis & Insights
# =========================
def analyze_legal_ai_landscape(reddit, subreddits, post_limit=100):
    """Main analysis function for legal AI discussions."""

    print(f"\n{'='*70}")
    print(f"🔍 LEGAL AI LANDSCAPE ANALYSIS")
    print(f"{'='*70}\n")

    # Step 1: Collect all content
    all_content = collect_from_all_subreddits(reddit, subreddits, post_limit)

    if not all_content:
        print("❌ No content collected")
        return None

    # Step 2: Extract AI tool mentions
    texts = [clean_text(item["text"]) for item in all_content]
    ai_extractions = extract_ai_tools_batch(texts)

    # Step 3: Filter to only AI-related content
    content_with_ai = []
    for item, extraction in zip(all_content, ai_extractions):
        if extraction["tools"]:
            content_with_ai.append({
                **item,
                "ai_tools": extraction["tools"],
                "ai_context": extraction["context"]
            })

    print(f"\n📊 Found {len(content_with_ai)} items mentioning AI tools (out of {len(all_content)} total)")

    if not content_with_ai:
        print("⚠️ No AI tool mentions found")
        return None

    # Step 4: Analyze sentiment and themes
    sentiment_analysis = analyze_ai_sentiment_and_themes(content_with_ai)

    # Step 5: Combine data
    for item, analysis in zip(content_with_ai, sentiment_analysis):
        item.update(analysis)

    # Step 6: Aggregate insights
    insights = generate_insights(content_with_ai)

    # Step 7: Print results
    print_insights(insights)

    # Step 8: Create visualizations
    create_visualizations(insights, content_with_ai)

    # Step 9: Export to DataFrame
    df = pd.DataFrame(content_with_ai)

    return {
        "insights": insights,
        "data": content_with_ai,
        "dataframe": df
    }


def generate_insights(content_with_ai: List[Dict]) -> Dict:
    """Generate aggregated insights from analyzed content."""

    # AI Tools mentioned
    tool_counter = Counter()
    for item in content_with_ai:
        for tool in item.get("ai_tools", []):
            tool_counter[tool.lower().strip()] += 1

    # Sentiment distribution
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

    # Use cases
    use_case_counter = Counter()
    for item in content_with_ai:
        use_case = item.get("use_case", "")
        if use_case:
            use_case_counter[use_case.lower().strip()] += 1

    # Role contexts
    role_counter = Counter()
    for item in content_with_ai:
        role = item.get("role_context", "")
        if role and role.lower() not in ["not mentioned", "unknown", ""]:
            role_counter[role.lower().strip()] += 1

    # Top contributors (authors)
    author_counter = Counter()
    author_scores = defaultdict(int)
    for item in content_with_ai:
        author = item.get("author", "deleted")
        if author != "deleted":
            author_counter[author] += 1
            author_scores[author] += item.get("score", 0)

    # Subreddit distribution
    subreddit_counter = Counter([item.get("subreddit", "") for item in content_with_ai])

    # Best quotes
    quotes_with_score = [
        (item.get("quote", ""), item.get("score", 0), item.get("permalink", ""))
        for item in content_with_ai
        if item.get("quote") and len(item.get("quote", "")) > 30
    ]
    quotes_with_score.sort(key=lambda x: x[1], reverse=True)

    return {
        "total_ai_mentions": len(content_with_ai),
        "top_tools": tool_counter.most_common(30),
        "sentiment_breakdown": dict(sentiment_counter),
        "top_themes": theme_counter.most_common(20),
        "top_pain_points": pain_counter.most_common(20),
        "top_use_cases": use_case_counter.most_common(20),
        "role_contexts": role_counter.most_common(15),
        "top_contributors": [
            (author, count, author_scores[author])
            for author, count in author_counter.most_common(15)
        ],
        "subreddit_distribution": dict(subreddit_counter),
        "top_quotes": quotes_with_score[:15]
    }


def print_insights(insights: Dict):
    """Print formatted insights."""

    print(f"\n{'='*70}")
    print(f"📊 LEGAL AI INSIGHTS REPORT")
    print(f"{'='*70}\n")

    print(f"📈 TOTAL AI-RELATED DISCUSSIONS: {insights['total_ai_mentions']}\n")

    # Top AI Tools
    print(f"🤖 TOP AI TOOLS MENTIONED:")
    for tool, count in insights['top_tools'][:15]:
        print(f"  • {tool}: {count} mentions")

    # Sentiment
    print(f"\n💭 SENTIMENT BREAKDOWN:")
    total_sent = sum(insights['sentiment_breakdown'].values())
    for sent, count in insights['sentiment_breakdown'].items():
        pct = (count / total_sent * 100) if total_sent > 0 else 0
        emoji = {"positive": "😊", "negative": "😞", "neutral": "😐", "mixed": "🤔"}.get(sent, "")
        print(f"  {emoji} {sent.capitalize()}: {count} ({pct:.1f}%)")

    # Top Themes
    print(f"\n🔑 TOP THEMES DISCUSSED:")
    for theme, count in insights['top_themes'][:15]:
        print(f"  • {theme}: {count} mentions")

    # Pain Points
    print(f"\n⚠️ TOP PAIN POINTS & CONCERNS:")
    for pain, count in insights['top_pain_points'][:12]:
        print(f"  • {pain}: {count} mentions")

    # Use Cases
    print(f"\n💼 TOP USE CASES:")
    for use_case, count in insights['top_use_cases'][:12]:
        print(f"  • {use_case}: {count} mentions")

    # Role Contexts
    if insights['role_contexts']:
        print(f"\n👥 PROFESSIONAL CONTEXTS IDENTIFIED:")
        for role, count in insights['role_contexts']:
            print(f"  • {role}: {count} mentions")

    # Top Contributors
    print(f"\n🌟 TOP CONTRIBUTORS (by activity):")
    for author, count, total_score in insights['top_contributors'][:10]:
        print(f"  • u/{author}: {count} AI-related posts/comments (total score: {total_score})")

    # Subreddit Distribution
    print(f"\n📍 AI DISCUSSIONS BY SUBREDDIT:")
    for sub, count in insights['subreddit_distribution'].items():
        pct = (count / insights['total_ai_mentions'] * 100)
        print(f"  • r/{sub}: {count} items ({pct:.1f}%)")

    # Top Quotes
    print(f"\n💡 MOST INSIGHTFUL QUOTES (by engagement):")
    for quote, score, link in insights['top_quotes'][:8]:
        quote_short = quote[:250] + ("..." if len(quote) > 250 else "")
        print(f'\n  [{score} upvotes] "{quote_short}"')
        print(f"  Link: {link}")


def create_visualizations(insights: Dict, content_with_ai: List[Dict]):
    """Create comprehensive visualizations."""

    print(f"\n📊 Creating visualizations...")

    # Set style
    sns.set_style("whitegrid")
    plt.rcParams['figure.figsize'] = (16, 12)

    fig = plt.figure(figsize=(20, 16))

    # 1. Top AI Tools (Top 15)
    ax1 = plt.subplot(3, 3, 1)
    tools = [t[0] for t in insights['top_tools'][:15]]
    counts = [t[1] for t in insights['top_tools'][:15]]
    ax1.barh(range(len(tools)), counts, color='#0066cc')
    ax1.set_yticks(range(len(tools)))
    ax1.set_yticklabels(tools, fontsize=9)
    ax1.set_xlabel('Mentions')
    ax1.set_title('Top 15 AI Tools Mentioned', fontweight='bold', fontsize=12)
    ax1.invert_yaxis()

    # 2. Sentiment Distribution
    ax2 = plt.subplot(3, 3, 2)
    sentiments = list(insights['sentiment_breakdown'].keys())
    sent_counts = list(insights['sentiment_breakdown'].values())
    colors = {'positive': '#2ecc71', 'negative': '#e74c3c', 'neutral': '#95a5a6', 'mixed': '#f39c12'}
    pie_colors = [colors.get(s, '#95a5a6') for s in sentiments]
    ax2.pie(sent_counts, labels=sentiments, autopct='%1.1f%%', colors=pie_colors, startangle=90)
    ax2.set_title('Sentiment Distribution', fontweight='bold', fontsize=12)

    # 3. Top Themes
    ax3 = plt.subplot(3, 3, 3)
    themes = [t[0] for t in insights['top_themes'][:12]]
    theme_counts = [t[1] for t in insights['top_themes'][:12]]
    ax3.barh(range(len(themes)), theme_counts, color='#9b59b6')
    ax3.set_yticks(range(len(themes)))
    ax3.set_yticklabels(themes, fontsize=9)
    ax3.set_xlabel('Mentions')
    ax3.set_title('Top 12 Discussion Themes', fontweight='bold', fontsize=12)
    ax3.invert_yaxis()

    # 4. Subreddit Distribution
    ax4 = plt.subplot(3, 3, 4)
    subs = list(insights['subreddit_distribution'].keys())
    sub_counts = list(insights['subreddit_distribution'].values())
    ax4.bar(range(len(subs)), sub_counts, color='#e67e22')
    ax4.set_xticks(range(len(subs)))
    ax4.set_xticklabels([f"r/{s}" for s in subs], rotation=45, ha='right', fontsize=9)
    ax4.set_ylabel('AI-Related Items')
    ax4.set_title('AI Discussions by Subreddit', fontweight='bold', fontsize=12)

    # 5. Top Pain Points
    ax5 = plt.subplot(3, 3, 5)
    pains = [p[0][:40] for p in insights['top_pain_points'][:10]]
    pain_counts = [p[1] for p in insights['top_pain_points'][:10]]
    ax5.barh(range(len(pains)), pain_counts, color='#e74c3c')
    ax5.set_yticks(range(len(pains)))
    ax5.set_yticklabels(pains, fontsize=8)
    ax5.set_xlabel('Mentions')
    ax5.set_title('Top 10 Pain Points', fontweight='bold', fontsize=12)
    ax5.invert_yaxis()

    # 6. Top Use Cases
    ax6 = plt.subplot(3, 3, 6)
    use_cases = [u[0][:40] for u in insights['top_use_cases'][:10]]
    use_counts = [u[1] for u in insights['top_use_cases'][:10]]
    ax6.barh(range(len(use_cases)), use_counts, color='#27ae60')
    ax6.set_yticks(range(len(use_cases)))
    ax6.set_yticklabels(use_cases, fontsize=8)
    ax6.set_xlabel('Mentions')
    ax6.set_title('Top 10 Use Cases', fontweight='bold', fontsize=12)
    ax6.invert_yaxis()

    # 7. Top Contributors
    ax7 = plt.subplot(3, 3, 7)
    contributors = [f"u/{c[0]}" for c in insights['top_contributors'][:10]]
    contrib_counts = [c[1] for c in insights['top_contributors'][:10]]
    ax7.barh(range(len(contributors)), contrib_counts, color='#3498db')
    ax7.set_yticks(range(len(contributors)))
    ax7.set_yticklabels(contributors, fontsize=9)
    ax7.set_xlabel('AI-Related Posts/Comments')
    ax7.set_title('Top 10 Contributors', fontweight='bold', fontsize=12)
    ax7.invert_yaxis()

    # 8. Sentiment by Subreddit
    ax8 = plt.subplot(3, 3, 8)
    df = pd.DataFrame(content_with_ai)
    if not df.empty and 'subreddit' in df.columns and 'sentiment' in df.columns:
        sentiment_by_sub = df.groupby(['subreddit', 'sentiment']).size().unstack(fill_value=0)
        sentiment_by_sub.plot(kind='bar', stacked=True, ax=ax8,
                             color=[colors.get(s, '#95a5a6') for s in sentiment_by_sub.columns])
        ax8.set_xlabel('Subreddit')
        ax8.set_ylabel('Count')
        ax8.set_title('Sentiment by Subreddit', fontweight='bold', fontsize=12)
        ax8.legend(title='Sentiment', fontsize=8)
        ax8.set_xticklabels(ax8.get_xticklabels(), rotation=45, ha='right')

    # 9. Word Cloud of Themes
    ax9 = plt.subplot(3, 3, 9)
    theme_text = " ".join([theme for theme, count in insights['top_themes'] for _ in range(count)])
    if theme_text.strip():
        wordcloud = WordCloud(width=400, height=300, background_color='white',
                             colormap='viridis').generate(theme_text)
        ax9.imshow(wordcloud, interpolation='bilinear')
        ax9.axis('off')
        ax9.set_title('Theme Word Cloud', fontweight='bold', fontsize=12)

    plt.tight_layout()
    plt.show()

    print("✅ Visualizations complete!")


# =========================
# STRATEGIC INSIGHTS
# =========================
def generate_strategic_recommendations(insights: Dict):
    """Generate strategic recommendations for positioning."""

    print(f"\n{'='*70}")
    print(f"🎯 STRATEGIC POSITIONING INSIGHTS")
    print(f"{'='*70}\n")

    print("📌 KEY TAKEAWAYS FOR YOUR AI STARTUP:\n")

    # Competitive landscape
    print("1️⃣ COMPETITIVE LANDSCAPE:")
    print(f"   • {len(insights['top_tools'])} different AI tools mentioned in discussions")
    print(f"   • Top 3 most-discussed: {', '.join([t[0] for t in insights['top_tools'][:3]])}")
    print("   • Action: Analyze these tools' positioning and differentiate your offering\n")

    # Sentiment analysis
    total_sent = sum(insights['sentiment_breakdown'].values())
    positive_pct = (insights['sentiment_breakdown'].get('positive', 0) / total_sent * 100) if total_sent > 0 else 0
    negative_pct = (insights['sentiment_breakdown'].get('negative', 0) / total_sent * 100) if total_sent > 0 else 0

    print("2️⃣ MARKET SENTIMENT:")
    print(f"   • {positive_pct:.1f}% positive sentiment - legal professionals are open to AI")
    print(f"   • {negative_pct:.1f}% negative sentiment - address concerns in messaging")
    print("   • Action: Emphasize benefits while proactively addressing top concerns\n")

    # Pain points to address
    print("3️⃣ TOP PAIN POINTS TO ADDRESS IN YOUR MESSAGING:")
    for i, (pain, count) in enumerate(insights['top_pain_points'][:5], 1):
        print(f"   {i}. {pain}")
    print("   • Action: Create content/features that directly solve these pain points\n")

    # Use cases to target
    print("4️⃣ HIGHEST-VALUE USE CASES:")
    for i, (use_case, count) in enumerate(insights['top_use_cases'][:5], 1):
        print(f"   {i}. {use_case} ({count} mentions)")
    print("   • Action: Prioritize these use cases in product roadmap and marketing\n")

    # Target personas
    print("5️⃣ TARGET PERSONAS IDENTIFIED:")
    if insights['role_contexts']:
        for i, (role, count) in enumerate(insights['role_contexts'][:5], 1):
            print(f"   {i}. {role} ({count} mentions)")
        print("   • Action: Create persona-specific messaging and case studies\n")
    else:
        print("   • Limited role-specific data - consider direct outreach for persona research\n")

    # Channel strategy
    print("6️⃣ CHANNEL STRATEGY:")
    top_sub = max(insights['subreddit_distribution'].items(), key=lambda x: x[1])
    print(f"   • Most active: r/{top_sub[0]} ({top_sub[1]} AI discussions)")
    print("   • Action: Engage authentically in these communities (no spam!)\n")

    # Influencers to engage
    print("7️⃣ KEY INFLUENCERS TO ENGAGE:")
    for i, (author, count, score) in enumerate(insights['top_contributors'][:5], 1):
        print(f"   {i}. u/{author} - {count} posts, {score} total engagement")
    print("   • Action: Build relationships, seek testimonials/case studies\n")

    print("="*70)


# =========================
# EXPORT FUNCTIONS
# =========================
def export_results(results: Dict, filename_prefix: str = "legal_ai_analysis"):
    """Export results to CSV files."""

    print(f"\n💾 Exporting results...")

    df = results['dataframe']

    # Main dataset
    df.to_csv(f"{filename_prefix}_full_data.csv", index=False)
    print(f"✅ Exported: {filename_prefix}_full_data.csv")

    # Tool summary
    tool_df = pd.DataFrame(results['insights']['top_tools'], columns=['Tool', 'Mentions'])
    tool_df.to_csv(f"{filename_prefix}_tools.csv", index=False)
    print(f"✅ Exported: {filename_prefix}_tools.csv")

    # Theme summary
    theme_df = pd.DataFrame(results['insights']['top_themes'], columns=['Theme', 'Mentions'])
    theme_df.to_csv(f"{filename_prefix}_themes.csv", index=False)
    print(f"✅ Exported: {filename_prefix}_themes.csv")

    # Pain points
    pain_df = pd.DataFrame(results['insights']['top_pain_points'], columns=['Pain Point', 'Mentions'])
    pain_df.to_csv(f"{filename_prefix}_pain_points.csv", index=False)
    print(f"✅ Exported: {filename_prefix}_pain_points.csv")

    print("✅ Export complete!")


# =========================
# RUN ANALYSIS
# =========================
print("\n" + "="*70)
print("🚀 LEGAL AI REDDIT ANALYSIS SCRIPT")
print("="*70 + "\n")

reddit = setup_reddit()

if reddit:
    # Run the analysis
    results = analyze_legal_ai_landscape(
        reddit=reddit,
        subreddits=SUBREDDITS,
        post_limit=POST_LIMIT_PER_SUBREDDIT
    )

    if results:
        # Generate strategic recommendations
        generate_strategic_recommendations(results['insights'])

        # Export results
        export_results(results)

        print("\n✅ ANALYSIS COMPLETE!")
        print("\n💡 TIP: Access the data with:")
        print("   • results['dataframe'] - Full pandas DataFrame")
        print("   • results['insights'] - Aggregated insights dict")
        print("   • results['data'] - Raw list of dicts")
    else:
        print("\n⚠️ Analysis failed - check error messages above")
else:
    print("\n❌ Could not connect to Reddit API")
