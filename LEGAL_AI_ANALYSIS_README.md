# Legal AI Reddit Analysis - User Guide

## Overview

This Google Colab script analyzes AI tool discussions across legal industry subreddits to provide actionable insights for positioning your AI startup in the legal tech market.

## Subreddits Analyzed

- r/legaltech
- r/Lawyertalk
- r/LawyersUsefulThings
- r/LawFirm
- r/AIForSmallBusiness

## What This Script Does

### 1. **AI Tool Discovery**
- Identifies all AI tools, platforms, and services mentioned
- Tracks frequency of mentions
- Ranks tools by popularity

### 2. **Sentiment Analysis**
- Analyzes sentiment toward AI tools (positive/negative/neutral/mixed)
- Breaks down sentiment by subreddit
- Identifies what drives positive vs. negative sentiment

### 3. **Theme Extraction**
- Surfaces key discussion themes (e.g., efficiency, accuracy concerns, cost)
- Identifies recurring topics across conversations
- Highlights emerging trends

### 4. **Pain Point Identification**
- Extracts specific challenges and concerns mentioned
- Ranks pain points by frequency
- Provides direct insight into what to solve

### 5. **Use Case Analysis**
- Identifies what legal professionals want to use AI for
- Ranks use cases by popularity
- Helps prioritize product roadmap

### 6. **User Analysis**
- Tracks top contributors to AI discussions
- Identifies potential influencers and early adopters
- Helps with community engagement strategy

### 7. **Strategic Insights**
- Generates positioning recommendations
- Identifies competitive landscape
- Suggests messaging strategies

## Setup Instructions

### Step 1: Get API Keys

#### Reddit API:
1. Go to https://www.reddit.com/prefs/apps
2. Click "Create App" or "Create Another App"
3. Select "script"
4. Fill in:
   - **name**: Any name (e.g., "Legal AI Analysis")
   - **redirect uri**: http://localhost:8080
5. Click "Create app"
6. Save these values:
   - **Client ID**: The string under "personal use script"
   - **Client Secret**: The "secret" value
   - **User Agent**: Format as "python:legalAIanalysis:v1.0 (by /u/YOUR_USERNAME)"

#### OpenAI API:
1. Go to https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Copy and save the key (starts with "sk-")

### Step 2: Add Secrets to Google Colab

1. Open Google Colab: https://colab.research.google.com/
2. Upload `legal_ai_reddit_analysis.py`
3. Click the 🔑 key icon in the left sidebar (Secrets)
4. Add these secrets:

   | Name | Value |
   |------|-------|
   | `REDDIT_CLIENT_ID` | Your Reddit client ID |
   | `REDDIT_CLIENT_SECRET` | Your Reddit secret |
   | `REDDIT_USER_AGENT` | Your user agent string |
   | `OPENAI_API_KEY` | Your OpenAI API key |

5. Toggle "Notebook access" ON for each secret

### Step 3: Run the Script

1. In Colab, click **Runtime** > **Run all**
2. Wait for analysis to complete (10-30 minutes depending on settings)
3. Review results in the notebook output

## Configuration Options

Edit these variables at the top of the script to customize:

```python
# Subreddits to analyze
SUBREDDITS = [
    "legaltech",
    "Lawyertalk",
    "LawyersUsefulThings",
    "LawFirm",
    "AIForSmallBusiness"
]

# Number of posts to fetch per subreddit
POST_LIMIT_PER_SUBREDDIT = 100  # Increase for more data (costs more API calls)

# Comments per post
COMMENT_LIMIT_PER_POST = 20
```

### Recommendations:
- **Quick test**: 50 posts per subreddit (~10 min, lower cost)
- **Standard analysis**: 100 posts per subreddit (~20 min, moderate cost)
- **Deep dive**: 200+ posts per subreddit (30+ min, higher cost)

## Output Files

The script generates several CSV exports:

1. **legal_ai_analysis_full_data.csv**
   - Complete dataset with all posts/comments
   - Columns: text, score, author, sentiment, themes, AI tools, pain points, etc.

2. **legal_ai_analysis_tools.csv**
   - AI tools ranked by mentions
   - Use for competitive analysis

3. **legal_ai_analysis_themes.csv**
   - Discussion themes ranked by frequency
   - Use for content strategy

4. **legal_ai_analysis_pain_points.csv**
   - Pain points ranked by mentions
   - Use for product positioning

## Understanding the Outputs

### 1. Top AI Tools Mentioned
**What it tells you:**
- Who your competitors are
- Which tools have mindshare in legal community
- Gaps in the market

**Action items:**
- Research top 5-10 tools in depth
- Identify their strengths/weaknesses from discussions
- Find differentiation opportunities

### 2. Sentiment Breakdown
**What it tells you:**
- Overall receptiveness to AI in legal field
- Whether to lean into enthusiasm or address skepticism

**Action items:**
- If positive > 60%: Emphasize benefits and ROI
- If negative > 30%: Address concerns head-on in messaging
- If mixed: Create balanced messaging that acknowledges challenges

### 3. Top Themes
**What it tells you:**
- What matters most to legal professionals when evaluating AI
- Common discussion topics

**Action items:**
- Create content around top 5-10 themes
- Position your product around these themes
- Use this language in marketing copy

### 4. Pain Points
**What it tells you:**
- Specific problems legal professionals face with AI
- Unmet needs in the market

**Action items:**
- Build features that solve top pain points
- Create messaging that addresses these directly
- Develop case studies showing how you solve them

### 5. Use Cases
**What it tells you:**
- What legal professionals want to use AI for
- Where to focus product development

**Action items:**
- Prioritize top use cases in roadmap
- Create demos/trials focused on these use cases
- Develop case studies for each major use case

### 6. Top Contributors
**What it tells you:**
- Who the influencers/active users are in the community
- Potential early adopters and advocates

**Action items:**
- Follow these users on Reddit
- Engage authentically with their content
- Consider reaching out for feedback/beta testing
- Potential testimonials/case studies

## Strategic Positioning Framework

Based on the analysis, develop your positioning:

### 1. Target Persona
- Use "Role Context" data to identify primary personas
- Create messaging specific to: general counsel, managing partners, solo practitioners, etc.

### 2. Value Proposition
- Lead with solutions to top 3 pain points
- Emphasize top 3 use cases in your messaging
- Use language from actual discussions (themes)

### 3. Competitive Differentiation
- Analyze what people say about top competitors
- Identify gaps and weaknesses
- Position against these

### 4. Messaging Strategy
- **If sentiment is mostly positive**: "Join forward-thinking firms already using AI"
- **If sentiment is mixed**: "AI that addresses your concerns about [top pain points]"
- **If sentiment is negative**: "We built this because existing AI tools don't understand legal work"

### 5. Channel Strategy
- Engage in the most active subreddits
- Build relationships with top contributors
- Share valuable content (not promotional) to build trust

## Tips for Maximum Value

### 1. Run Regularly
- Run monthly to track trends
- See how competitor mentions change
- Identify emerging tools/concerns

### 2. Combine with Other Data
- Cross-reference with:
  - LinkedIn discussions
  - Legal tech conferences
  - Customer interviews
  - Sales call notes

### 3. Segment Analysis
- Run separately for each subreddit to see differences
- Compare r/legaltech (tech-forward) vs r/Lawyertalk (general practitioners)

### 4. Deeper Analysis
- Read the full quotes - they contain the richest insights
- Export the CSV and filter by specific tools/themes
- Look at high-scoring posts for quality discussions

### 5. Validation
- Use insights to create hypotheses
- Test with customer interviews
- A/B test messaging based on pain points/themes

## Common Issues & Solutions

### Issue: "No AI tool mentions found"
**Solutions:**
- Increase POST_LIMIT_PER_SUBREDDIT
- Try different subreddits
- Check date range (recent vs. top of all time)

### Issue: OpenAI rate limits
**Solutions:**
- Reduce batch_size in functions
- Add longer sleep() delays
- Upgrade OpenAI API tier

### Issue: Reddit API errors
**Solutions:**
- Check API credentials
- Ensure you're not hitting rate limits (600 requests per 10 min)
- Try reducing POST_LIMIT

### Issue: Low quality insights
**Solutions:**
- Increase sample size (more posts)
- Try "top" posts instead of "hot" posts
- Adjust time filter to past month/year

## Cost Estimates

### Reddit API: FREE
- 600 requests per 10 minutes
- This script stays well under limits

### OpenAI API: ~$0.50-$3.00 per run
- Depends on POST_LIMIT_PER_SUBREDDIT
- Uses GPT-4o-mini (very cost-effective)
- 100 posts per subreddit ≈ $1-2
- 200 posts per subreddit ≈ $2-4

## Advanced Customization

### Analyze Specific AI Tools
Add this code after setup to focus on specific tools:

```python
TARGET_TOOLS = ["ChatGPT", "Harvey AI", "Casetext", "Ross Intelligence"]

# After collecting content, filter:
filtered_content = []
for item in content_with_ai:
    item_tools = [t.lower() for t in item.get('ai_tools', [])]
    if any(target.lower() in item_tools for target in TARGET_TOOLS):
        filtered_content.append(item)

# Continue analysis with filtered_content
```

### Change Time Period
Modify the collection function to fetch from different time periods:

```python
# Instead of sr.hot(limit=limit), use:
sr.top(time_filter='month', limit=limit)  # Options: hour, day, week, month, year, all
```

### Add More Subreddits
```python
ADDITIONAL_SUBS = [
    "law",
    "LawSchool",
    "paralegal",
    "AskLawyers"
]
SUBREDDITS.extend(ADDITIONAL_SUBS)
```

## Contact & Support

For issues with this script:
1. Check the error message carefully
2. Verify API keys are correct
3. Try reducing POST_LIMIT first
4. Check OpenAI API has credits

## Next Steps After Analysis

1. **Immediate Actions** (Week 1)
   - Update website copy with pain points and use cases
   - Create comparison page vs. top 3 competitors
   - Draft outreach messages to top contributors

2. **Short-term** (Month 1)
   - Create content addressing top themes
   - Develop case studies for top use cases
   - Build features solving top pain points

3. **Medium-term** (Quarter 1)
   - Launch community engagement strategy
   - Conduct interviews with target personas
   - A/B test messaging based on insights

4. **Ongoing**
   - Run analysis monthly
   - Track changes in sentiment and tools
   - Adjust positioning based on trends

---

**Good luck with your legal AI startup! 🚀**
