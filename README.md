# TECHi: RSS Headline Collector


Source: ZR-26-00741 · Built for the TechAbout employee Growth task
"TECHi: RSS Headline Collector".


A Streamlit app that collects tech headlines from RSS/Atom feeds:


- Paste feed URLs (one per line) — ships with tech-news defaults
  (TechCrunch, The Verge, Ars Technica, Wired, Hacker News, MIT Tech Review)
- Fetches and parses feeds with `feedparser` (via stdlib `urllib`, with a
  per-feed timeout); broken feeds are reported, not fatal
- Clean table of latest headlines: published time, source, headline, link
- Keyword filter and a Refresh button (clears cache and re-fetches)


## Run locally


```bash
cd techi-rss-collector
pip install -r requirements.txt
streamlit run app.py
```


Then open the URL Streamlit prints (usually http://localhost:8501).


## Deploy on Streamlit Community Cloud


1. Push this folder to a GitHub repository.
2. Go to https://share.streamlit.io → **New app**.
3. Select the repo, branch, and `app.py` as the main file.
4. Click **Deploy**. No secrets or API keys are needed.


---
## Built for BlogReach
SEO outreach for this project via [BlogReach](https://blogreach.com) — the guest-posting marketplace.
---
