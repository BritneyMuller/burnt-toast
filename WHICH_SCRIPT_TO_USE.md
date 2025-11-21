# Which Script Should I Use?

You now have TWO powerful Reddit analysis scripts. Here's how to choose:

---

## 📊 Quick Comparison

| Use Case | Basic Script | Enhanced Script |
|----------|-------------|-----------------|
| **First-time analysis** | ✅ Start here | Maybe too much |
| **AI tool landscape overview** | ✅ Perfect | ✅ Even better |
| **Content strategy** | ❌ Limited | ✅ Perfect |
| **Posting optimization** | ❌ No | ✅ Yes |
| **Competitive intelligence** | ✅ Good | ✅ Excellent |
| **Quick insights (< 30 min)** | ✅ Yes | ⚠️ Takes longer |
| **Monthly tracking** | ✅ Good | ✅ Best with DB |
| **Engagement analysis** | ❌ No | ✅ Yes |

---

## 🎯 Use the **BASIC** Script When:

### ✅ You Want To:
- Get a quick overview of the AI legal landscape
- Identify top AI tools being discussed
- Understand general sentiment toward AI
- Find top themes and pain points
- Identify influencers and top contributors
- Export basic data for manual analysis

### ⏱️ Time Investment:
- Setup: 5 minutes
- Run time: 10-20 minutes
- Analysis: Quick, straightforward output

### 💰 Cost:
- $1-2 per run (100 posts/subreddit)

### 📁 File:
`legal_ai_reddit_analysis.py`

### 📖 Documentation:
`LEGAL_AI_ANALYSIS_README.md`

---

## 🚀 Use the **ENHANCED** Script When:

### ✅ You Want To:
- **Optimize your content strategy** (when/what to post)
- **Understand specific concerns** about AI tools
- **See common questions** people ask
- **Identify onboarding hurdles** you can solve
- **Analyze engagement patterns** (what makes posts viral)
- **Track trends over time** (with database)
- **Get posting time recommendations**
- **Understand post type performance**
- **Extract specific audience needs**
- **Create data-driven content calendars**

### ⏱️ Time Investment:
- Setup: 5 minutes (same as basic)
- Run time: 20-40 minutes (more AI analysis)
- Analysis: Rich, detailed insights with ASCII viz

### 💰 Cost:
- $2-4 per run (100 posts/subreddit)
- ~50% more than basic due to extra analysis

### 📁 File:
`legal_ai_enhanced_analysis.py`

### 📖 Documentation:
`ENHANCED_ANALYSIS_README.md`

---

## 💡 Recommended Workflow

### For Most People: START → ENHANCE

**Month 1: Use Basic Script**
1. Run basic script to understand the landscape
2. Get familiar with the data structure
3. Identify if there's enough AI discussion to warrant deeper analysis
4. Review outputs, see what insights you need

**Month 2+: Upgrade to Enhanced**
1. Once you understand the landscape, run enhanced script
2. Use posting time recommendations
3. Create content based on engagement triggers
4. Track changes month-over-month with database

### For Advanced Users: GO STRAIGHT TO ENHANCED

If you're comfortable with data analysis and want maximum value immediately, just use the enhanced script from day 1.

---

## 🎯 Specific Scenarios

### Scenario 1: "I want to understand the competitive landscape"
**Use:** Basic Script
**Why:** Gets you tool mentions, sentiment, themes quickly
**Then:** Deep-dive into top 3 competitors manually

### Scenario 2: "I want to know when to post on Reddit for max engagement"
**Use:** Enhanced Script
**Why:** Only enhanced has temporal analysis
**Output:** Best hours and days to post

### Scenario 3: "I want to create a content calendar"
**Use:** Enhanced Script
**Why:** Gives you questions to answer, post types that work, engagement triggers
**Output:** Content ideas + timing + format

### Scenario 4: "I want to position against competitors"
**Use:** Enhanced Script
**Why:** Shows tool-specific concerns, hurdles, questions
**Output:** Messaging that addresses competitor weaknesses

### Scenario 5: "I just want a quick pulse check"
**Use:** Basic Script
**Why:** Faster, cheaper, still very insightful
**Output:** Top tools, sentiment, themes in 15 minutes

### Scenario 6: "I want to track trends over time"
**Use:** Enhanced Script (with database enabled)
**Why:** Only enhanced has optional database logging
**Output:** Historical data for trend analysis

### Scenario 7: "I'm creating buyer personas"
**Use:** Enhanced Script
**Why:** Extracts audience needs, questions, pain points, hurdles
**Output:** Rich persona data (concerns, questions, needs)

### Scenario 8: "I'm writing a competitor analysis report"
**Use:** Basic Script first, Enhanced for specific tools
**Why:** Basic gives overview, enhanced gives detailed concerns per tool
**Output:** Comprehensive competitive intelligence

---

## 🔄 Can I Run Both?

**YES!** They're complementary, not mutually exclusive.

### Efficient Workflow:
1. **Run Basic** (10 min) → Get landscape overview
2. **Review results** → See if you need more depth
3. **Run Enhanced** (20 min) → Get strategic insights

### Benefits:
- Basic script is faster for quick checks
- Enhanced script for monthly deep-dives
- Both export CSVs you can combine/compare

### Avoid:
- Running both every time (wastes API credits)
- Running enhanced if you won't use the extra insights

---

## 📊 Output Comparison

### Basic Script Outputs:
- Top AI tools mentioned
- Sentiment breakdown
- Top themes discussed
- Top pain points
- Top use cases
- Professional role contexts
- Top contributors
- Subreddit distribution
- Top quotes by engagement
- **9 visualizations**
- **4 CSV exports**

### Enhanced Script Outputs:
**Everything from Basic, PLUS:**
- ✨ **Post type classification** (Question, Advice, etc.)
- ✨ **Post type performance** (avg score, avg comments)
- ✨ **Best posting times** (by hour)
- ✨ **Best posting days** (day of week)
- ✨ **AI tool-specific concerns**
- ✨ **Common questions about AI**
- ✨ **Onboarding/implementation hurdles**
- ✨ **Engagement triggers** (what makes posts viral)
- ✨ **Audience needs** (more granular than use cases)
- ✨ **Beautiful ASCII formatting** with bars
- ✨ **Optional database logging**
- ✨ **16 visualizations** (7 more than basic)
- ✨ **9 CSV exports** (5 more than basic)

---

## 💾 Database Feature (Enhanced Only)

The enhanced script can optionally log everything to SQLite database.

### Enable it when:
- You want to track trends month-over-month
- You're running analysis regularly (monthly+)
- You want to query historical data
- You need to compare competitor mentions over time

### Skip it when:
- First time running the script
- One-off analysis
- You prefer working with CSV exports

### How to enable:
```python
ENABLE_DATABASE = True  # In the script
```

---

## 🎓 Learning Path

### Beginner:
1. Start with **Basic Script**
2. Read the outputs carefully
3. Understand what each metric means
4. Run 2-3 times to see consistency

### Intermediate:
1. Move to **Enhanced Script**
2. Use posting time recommendations
3. Create content based on questions/needs
4. Export CSVs for deeper analysis in Excel

### Advanced:
1. Use **Enhanced Script** with database
2. Run monthly, track trends
3. Segment by subreddit
4. Combine with other data sources
5. Build automated dashboards

---

## ⚡ Quick Decision Tree

```
START
  ↓
Do you need to optimize WHEN to post?
  ├─ YES → Enhanced Script
  └─ NO → Continue
         ↓
Do you need to know WHAT makes posts engaging?
  ├─ YES → Enhanced Script
  └─ NO → Continue
         ↓
Do you need specific QUESTIONS people ask?
  ├─ YES → Enhanced Script
  └─ NO → Continue
         ↓
Do you want IMPLEMENTATION HURDLE insights?
  ├─ YES → Enhanced Script
  └─ NO → Continue
         ↓
Just want a quick competitive overview?
  └─ YES → Basic Script
```

---

## 💬 Still Not Sure?

### Ask Yourself:

**"Will I use posting time recommendations?"**
- YES → Enhanced
- NO → Basic

**"Do I need to understand WHY posts get engagement?"**
- YES → Enhanced
- NO → Basic

**"Is this a one-time analysis?"**
- YES → Basic (faster, cheaper)
- NO, monthly → Enhanced (database tracking)

**"Am I creating a content strategy?"**
- YES → Enhanced (gives you what/when/how to post)
- NO, just researching → Basic

**"Do I want the most comprehensive analysis possible?"**
- YES → Enhanced
- NO, just the essentials → Basic

---

## 🎯 Bottom Line

### 🥉 Basic Script = Competitive Intelligence
**Best for:** Understanding the landscape, finding competitors, general sentiment

### 🥇 Enhanced Script = Strategic Action Plan
**Best for:** Content strategy, posting optimization, positioning, tracking

**Both are valuable!** Start with basic, upgrade to enhanced when you need deeper strategic insights.

---

## 📝 Quick Reference

| What You Need | Script to Use |
|--------------|---------------|
| Top AI tools mentioned | Both (same) |
| Competitor mentions | Both (same) |
| General sentiment | Both (same) |
| When to post | **Enhanced only** |
| What post type performs best | **Enhanced only** |
| Common questions | **Enhanced only** |
| Onboarding hurdles | **Enhanced only** |
| Engagement triggers | **Enhanced only** |
| Quick 15-min analysis | **Basic** |
| Track trends monthly | **Enhanced (with DB)** |
| Content calendar creation | **Enhanced** |
| One-time research | **Basic** |

---

**Questions?** Check the respective README files for each script!

- `LEGAL_AI_ANALYSIS_README.md` → Basic Script Guide
- `ENHANCED_ANALYSIS_README.md` → Enhanced Script Guide
