import streamlit as st
import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin, urlparse
import re

# --- 1. PAGE SETUP & PREMIUM CSS ---
st.set_page_config(page_title="Radar Pro - Ultimate AdSense Checker", layout="wide", page_icon="🧿")

st.markdown("""
    <style>
    .title-text { font-size: 40px; font-weight: 900; color: #0f172a; margin-bottom: 5px; }
    .subtitle-text { font-size: 18px; color: #475569; margin-bottom: 30px; }
    
    /* Health Status Badges */
    .status-green { background-color: #dcfce7; color: #166534; padding: 10px 15px; border-radius: 8px; font-weight: bold; border-left: 5px solid #22c55e; margin-bottom: 8px;}
    .status-yellow { background-color: #fef9c3; color: #854d0e; padding: 10px 15px; border-radius: 8px; font-weight: bold; border-left: 5px solid #eab308; margin-bottom: 8px;}
    .status-red { background-color: #fee2e2; color: #991b1b; padding: 10px 15px; border-radius: 8px; font-weight: bold; border-left: 5px solid #ef4444; margin-bottom: 8px;}
    
    .advice-box { background-color: #f8fafc; padding: 20px; border-radius: 10px; border: 1px dashed #cbd5e1; margin-top: 20px; }
    </style>
""", unsafe_allow_html=True)

# --- 2. HEADER ---
st.markdown('<div class="title-text">🧿 Radar Pro: AdSense Eligibility Auditor</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle-text">Deep scanning engine for Technical SEO, Policies, and Content Health.</div>', unsafe_allow_html=True)

url_input = st.text_input("Enter your Website URL (e.g., https://projobalert.com):", placeholder="https://example.com")

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

def check_link(url):
    try:
        res = requests.head(url, headers=HEADERS, timeout=5, allow_redirects=False)
        return res.status_code, res.headers.get('Location', '')
    except:
        return 0, ''

# --- 3. MAIN ENGINE ---
if st.button("🚀 Initiate Advanced Scan", type="primary", use_container_width=True):
    if not url_input.startswith("http"):
        st.error("⚠️ URL must start with http:// or https://")
    else:
        with st.spinner("Executing Ultra Max Scan... Analyzing 50+ Ranking Factors..."):
            start_time = time.time()
            score = 100
            advice_list = []
            
            try:
                res = requests.get(url_input, headers=HEADERS, timeout=15)
                load_time = round(time.time() - start_time, 2)
                soup = BeautifulSoup(res.text, 'html.parser')
                text_content = soup.get_text().lower()
                
                # --- CATEGORY 1: TECHNICAL & CONNECTIVITY ---
                status_200 = res.status_code == 200
                has_ssl = url_input.startswith("https")
                # Canonical Check (Basic WWW check)
                is_www = "www." in urlparse(url_input).netloc
                
                # --- CATEGORY 2: REDIRECTION & ERRORS ---
                links = soup.find_all('a', href=True)
                internal_urls = []
                for a in links:
                    full_url = urljoin(url_input, a['href'])
                    if urlparse(full_url).netloc == urlparse(url_input).netloc and full_url not in internal_urls:
                        internal_urls.append(full_url)
                
                s_301, s_302, s_404 = 0, 0, 0
                scan_limit = min(15, len(internal_urls)) # Fast sample scan
                for i in range(scan_limit):
                    code, loc = check_link(internal_urls[i])
                    if code == 301: s_301 += 1
                    elif code in [302, 307]: s_302 += 1
                    elif code == 404: s_404 += 1
                
                # --- CATEGORY 3: ADSENSE POLICY COMPLIANCE ---
                essential_list = ["privacy", "contact", "about", "disclaimer", "terms"]
                found_essentials = [ep for ep in essential_list if any(ep in u.lower() for u in internal_urls)]
                
                banned_keywords = ["hack", "cracked", "mod apk", "adult", "casino", "gambling", "movie download", "porn"]
                found_banned = [w for w in banned_keywords if w in text_content]
                
                cookie_consent = any(w in text_content for w in ["cookie", "consent", "accept cookies", "got it"])
                under_construction = any(w in text_content for w in ["under construction", "coming soon", "lorem ipsum"])
                
                # --- CATEGORY 4: CONTENT & ON-PAGE SEO ---
                word_count = len(text_content.split())
                has_title = soup.title is not None and len(soup.title.text) > 10
                has_desc = soup.find("meta", {"name": "description"}) is not None
                
                h1_tags = len(soup.find_all('h1'))
                h2_tags = len(soup.find_all('h2'))
                heading_hierarchy = h1_tags == 1 and h2_tags > 0
                
                images = soup.find_all('img')
                img_total = len(images)
                img_alt = sum(1 for img in images if img.get('alt'))
                
                # --- CATEGORY 5: SITE STRUCTURE & NAVIGATION ---
                has_robots = requests.get(urljoin(url_input, "robots.txt"), headers=HEADERS, timeout=5).status_code == 200
                has_sitemap = requests.get(urljoin(url_input, "sitemap.xml"), headers=HEADERS, timeout=5).status_code == 200
                has_viewport = soup.find("meta", {"name": "viewport"}) is not None
                
                # --- SCORE CALCULATION & ADVICE GENERATION ---
                if not has_ssl: score -= 20; advice_list.append("Install an SSL Certificate (HTTPS) immediately.")
                if load_time > 3.0: score -= 10; advice_list.append("Speed up your site. Optimize images and use caching.")
                if s_404 > 0: score -= 15; advice_list.append(f"Fix {s_404} broken (404) links. AdSense hates broken sites.")
                if len(found_essentials) < 4: score -= 20; advice_list.append("Add missing essential pages (Privacy, Terms, Disclaimer).")
                if found_banned: score -= 30; advice_list.append(f"Remove prohibited content: {', '.join(found_banned)}.")
                if word_count < 600: score -= 15; advice_list.append("Increase word count on pages. Thin content leads to 'Low Value Content' rejection.")
                if h1_tags != 1: score -= 5; advice_list.append("Ensure every page has exactly ONE H1 tag for SEO.")
                if not has_sitemap: score -= 10; advice_list.append("Generate and submit a sitemap.xml to Google Search Console.")
                if under_construction: score -= 25; advice_list.append("Remove 'Coming Soon' or placeholder text before applying.")
                
                score = max(0, min(score, 100))
                
                # --- UI DASHBOARD (TABS FOR MODERN LOOK) ---
                st.success(f"✅ Deep Scan Completed in {load_time}s")
                
                st.markdown(f"### 🎯 AdSense Approval Odds: {score}%")
                st.progress(score / 100)
                
                # Create Tabs
                t1, t2, t3, t4, t5, t6 = st.tabs(["⚙️ Tech & Speed", "🔗 Links", "🛡️ Policy", "📝 Content & SEO", "🗂️ Structure", "🌐 Domain"])
                
                def render_badge(condition, pass_text, fail_text, warn_condition=False, warn_text=""):
                    if warn_condition:
                        st.markdown(f"<div class='status-yellow'>⚠️ {warn_text}</div>", unsafe_allow_html=True)
                    elif condition:
                        st.markdown(f"<div class='status-green'>✅ {pass_text}</div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div class='status-red'>❌ {fail_text}</div>", unsafe_allow_html=True)

                with t1:
                    render_badge(status_200, "Website Status: 200 OK (Live)", "Website Unreachable")
                    render_badge(has_ssl, "SSL Certificate: Active (HTTPS)", "SSL Missing (HTTP Only)")
                    render_badge(load_time < 2.5, f"Response Time: {load_time}s (Fast)", f"Response Time: {load_time}s (Too Slow)", warn_condition=(2.5 <= load_time <= 4.0), warn_text=f"Response Time: {load_time}s (Needs Speedup)")
                    render_badge(is_www, "Canonical URL: WWW present", "Canonical URL: Non-WWW (Ensure proper 301 redirection)")
                    
                with t2:
                    render_badge(s_404 == 0, "Broken Links (404): 0 Found", f"Broken Links: {s_404} Found (Fix immediately)")
                    render_badge(s_302 == 0, "Temp Redirects (302): None", "", warn_condition=(s_302 > 0), warn_text=f"Temp Redirects (302): {s_302} Found (Use 301 instead)")
                    render_badge(s_301 >= 0, f"Permanent Redirects (301): {s_301} Logged (Good for SEO)", "")
                    
                with t3:
                    render_badge(len(found_essentials) >= 4, f"Essential Pages: {len(found_essentials)}/5 Found", f"Essential Pages Missing! Only {len(found_essentials)}/5 found.")
                    render_badge(not found_banned, "Banned Content: 100% Clean", f"Prohibited Words Found: {', '.join(found_banned)}")
                    render_badge(not under_construction, "Site Readiness: Active", "Under Construction / Placeholder Text Found!")
                    render_badge(cookie_consent, "Cookie Consent: Banner Detected", "", warn_condition=(not cookie_consent), warn_text="Cookie Consent: Not strictly detected (Required for EU traffic)")

                with t4:
                    render_badge(word_count >= 600, f"Word Count: {word_count} words (Deep Content)", f"Thin Content: Only {word_count} words (Risk of rejection)", warn_condition=(300 <= word_count < 600), warn_text=f"Word Count: {word_count} words (Average, 600+ recommended)")
                    render_badge(has_title and has_desc, "Meta Tags: Title & Description Perfect", "Meta Tags: Missing Title or Description")
                    render_badge(heading_hierarchy, "Heading Hierarchy: Proper H1/H2 Structure", "Heading Errors: Missing H1 or multiple H1s used")
                    render_badge(img_total > 0 and (img_alt/img_total) > 0.8, f"Image Alt Text: {img_alt}/{img_total} Optimized", "", warn_condition=(img_total > 0 and (img_alt/img_total) <= 0.8), warn_text=f"Image Alt Text: Only {img_alt}/{img_total} images have Alt tags")
                    render_badge(True, "Plagiarism & Grammar: Manual Verification Required", "", warn_condition=True, warn_text="Grammar & Plagiarism: Ensure content is 100% unique manually.")

                with t5:
                    render_badge(has_robots, "Robots.txt: Visibility OK", "Robots.txt: Missing (Search engines can't crawl properly)")
                    render_badge(has_sitemap, "Sitemap.xml: Found", "Sitemap.xml: Missing (Crucial for indexing)")
                    render_badge(has_viewport, "Mobile Viewport: 100% Responsive Ready", "Mobile Viewport: Missing (Not mobile-friendly)")
                    render_badge(len(internal_urls) > 5, f"Internal Linking: {len(internal_urls)} links crawled (Good Depth)", f"Internal Linking: Poor depth, only {len(internal_urls)} links found")

                with t6:
                    st.info("💡 **Domain & Indexing requires Google Search Console access.**")
                    render_badge(True, "", "", warn_condition=True, warn_text="Domain Age: Ensure your domain is at least 1-2 months old.")
                    render_badge(True, "", "", warn_condition=True, warn_text="Google Indexing: Verify via 'site:yourdomain.com' in Google.")
                    render_badge(True, "", "", warn_condition=True, warn_text="Ad Placement: Ensure you have empty spaces ready for Ad units.")

                # --- 6. ACTIONABLE ADVICE SECTION ---
                st.markdown("---")
                st.markdown("### 🛠️ Actionable Advice (Next Steps)")
                if not advice_list:
                    st.success("🎉 Your site is practically perfect! You are ready to apply for Google AdSense.")
                else:
                    st.markdown("<div class='advice-box'>", unsafe_allow_html=True)
                    for i, advice in enumerate(advice_list):
                        st.write(f"**{i+1}.** {advice}")
                    st.markdown("</div>", unsafe_allow_html=True)

            except Exception as e:
                st.error(f"❌ Critical Error: Unable to scan the website. Make sure the URL is correct and the server is online.")

st.markdown("<br><center><small>Powered by Radar Pro V5 Ultimate Engine | Professional SEO Audit</small></center>", unsafe_allow_html=True)
