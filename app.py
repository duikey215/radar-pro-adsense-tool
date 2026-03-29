import streamlit as st
import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin, urlparse
import re

# --- 1. PAGE SETUP & PREMIUM CSS (SaaS Level Look) ---
st.set_page_config(page_title="Radar Pro V5 | Ultimate AdSense Checker", layout="wide", page_icon="🧿")

# Custom CSS for Professional Iframe & Dashboard Look
st.markdown("""
    <style>
    /* Hide Streamlit Default Menu & Footer for clean Iframe look in Blogger */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Background & Typography */
    .stApp {
        background-color: #f8fafc;
        font-family: 'Inter', sans-serif;
    }
    
    /* Hero Section */
    .hero-box {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        padding: 40px 20px;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    .hero-title { font-size: 42px; font-weight: 900; color: #ffffff; margin-bottom: 5px; }
    .hero-title span { color: #3b82f6; }
    .hero-subtitle { font-size: 16px; color: #94a3b8; }
    
    /* Metric Cards */
    .metric-container { display: flex; justify-content: space-between; gap: 15px; margin-bottom: 25px; flex-wrap: wrap; }
    .metric-card {
        background: white; padding: 20px; border-radius: 12px; flex: 1; min-width: 200px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); border-top: 4px solid #3b82f6; text-align: center;
    }
    .metric-value { font-size: 32px; font-weight: 800; color: #0f172a; }
    .metric-label { font-size: 14px; color: #64748b; font-weight: 600; text-transform: uppercase; letter-spacing: 1px;}
    
    /* Health Badges */
    .status-badge { display: flex; align-items: center; padding: 12px 18px; border-radius: 8px; margin-bottom: 12px; font-weight: 600; font-size: 15px;}
    .badge-pass { background-color: #dcfce7; color: #166534; border-left: 5px solid #22c55e; }
    .badge-warn { background-color: #fef9c3; color: #854d0e; border-left: 5px solid #eab308; }
    .badge-fail { background-color: #fee2e2; color: #991b1b; border-left: 5px solid #ef4444; }
    .icon { margin-right: 10px; font-size: 18px; }
    
    /* Advice Box */
    .advice-wrapper { background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; }
    .advice-item { background: #f1f5f9; padding: 12px 15px; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid #ef4444; color: #334155; font-weight: 500;}
    
    /* Custom Input styling */
    .stTextInput input { border-radius: 8px !important; border: 2px solid #cbd5e1 !important; padding: 15px !important; font-size: 16px !important; }
    .stTextInput input:focus { border-color: #3b82f6 !important; box-shadow: 0 0 0 2px rgba(59,130,246,0.2) !important; }
    </style>
""", unsafe_allow_html=True)

# --- 2. HERO HEADER ---
st.markdown("""
    <div class="hero-box">
        <div class="hero-title">🧿 Radar <span>Pro</span></div>
        <div class="hero-subtitle">Enterprise-Grade AdSense Eligibility & Deep SEO Auditor</div>
    </div>
""", unsafe_allow_html=True)

url_input = st.text_input("Enter Website URL to Audit:", placeholder="https://yourwebsite.com", label_visibility="collapsed")

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

def check_link(url):
    try:
        res = requests.head(url, headers=HEADERS, timeout=5, allow_redirects=False)
        return res.status_code
    except:
        return 0

# --- 3. MAIN ENGINE (DEEP SCAN) ---
if st.button("🚀 INITIATE DEEP SCAN", type="primary", use_container_width=True):
    if not url_input.strip() or not url_input.startswith(("http://", "https://")):
        st.error("⚠️ Please enter a valid URL starting with http:// or https://")
    else:
        # --- INTERACTIVE TERMINAL FEELING ---
        with st.status("📡 Establishing Secure Connection to Server...", expanded=True) as status:
            start_time = time.time()
            score = 100
            advice_list =[]
            
            try:
                # Step 1: Homepage Fetch
                status.update(label="🌍 Crawling Homepage & Analyzing Server Response...")
                res = requests.get(url_input, headers=HEADERS, timeout=15)
                load_time = round(time.time() - start_time, 2)
                soup = BeautifulSoup(res.text, 'html.parser')
                text_content = soup.get_text().lower()
                time.sleep(0.5) # Adding slight delay so user can read the status
                
                # Step 2: Internal Links & Deep Scan Simulation
                status.update(label="🕸️ Extracting Architecture & Scanning Deep Links...")
                links = soup.find_all('a', href=True)
                internal_urls =[]
                for a in links:
                    full_url = urljoin(url_input, a['href'])
                    if urlparse(full_url).netloc == urlparse(url_input).netloc and full_url not in internal_urls:
                        internal_urls.append(full_url)
                
                # Deep scan up to 2 random internal pages to calculate total words
                total_word_count = len(text_content.split())
                pages_scanned = 1
                for internal_link in internal_urls[:2]:
                    try:
                        sub_res = requests.get(internal_link, headers=HEADERS, timeout=5)
                        sub_soup = BeautifulSoup(sub_res.text, 'html.parser')
                        total_word_count += len(sub_soup.get_text().split())
                        pages_scanned += 1
                    except: pass
                
                avg_word_count = total_word_count // pages_scanned
                time.sleep(0.5)

                # Step 3: Tech & Policies
                status.update(label="🛡️ Auditing AdSense Policies & Content Quality...")
                status_200 = res.status_code == 200
                has_ssl = url_input.startswith("https")
                is_www = "www." in urlparse(url_input).netloc
                
                s_301, s_302, s_404 = 0, 0, 0
                scan_limit = min(10, len(internal_urls))
                for i in range(scan_limit):
                    code = check_link(internal_urls[i])
                    if code == 301: s_301 += 1
                    elif code in[302, 307]: s_302 += 1
                    elif code >= 400: s_404 += 1
                
                essential_list =["privacy", "contact", "about", "disclaimer", "terms"]
                found_essentials =[ep for ep in essential_list if any(ep in u.lower() for u in internal_urls)]
                
                banned_keywords =["hack", "cracked", "mod apk", "adult", "casino", "gambling", "movie download", "porn", "nude"]
                found_banned =[w for w in banned_keywords if w in text_content]
                
                cookie_consent = any(w in text_content for w in["cookie", "consent", "accept", "got it"])
                under_construction = any(w in text_content for w in ["under construction", "coming soon", "lorem ipsum", "hello world"])
                has_adsense_code = "pagead2.googlesyndication.com" in res.text
                
                time.sleep(0.5)

                # Step 4: SEO Tags & Structure
                status.update(label="📊 Calculating Final Eligibility Score...")
                has_title = soup.title is not None and len(soup.title.text) > 10
                has_desc = soup.find("meta", {"name": "description"}) is not None
                h1_tags = len(soup.find_all('h1'))
                images = soup.find_all('img')
                img_total = len(images)
                img_alt = sum(1 for img in images if img.get('alt'))
                
                has_robots = requests.get(urljoin(url_input, "robots.txt"), headers=HEADERS, timeout=5).status_code == 200
                has_sitemap = requests.get(urljoin(url_input, "sitemap.xml"), headers=HEADERS, timeout=5).status_code == 200
                has_viewport = soup.find("meta", {"name": "viewport"}) is not None
                
                # --- ALGORITHM: SCORING LOGIC ---
                if not has_ssl: score -= 20; advice_list.append("Install an SSL Certificate (HTTPS). AdSense requires secure sites.")
                if load_time > 3.5: score -= 10; advice_list.append(f"Site is slow ({load_time}s). Optimize images and use a caching plugin.")
                if s_404 > 0: score -= 15; advice_list.append(f"Found {s_404} broken (404) links. Fix them to avoid 'Site Down' rejection.")
                if len(found_essentials) < 4: score -= 20; advice_list.append(f"Missing essential pages. We only found {len(found_essentials)}/5. (Require: Privacy, Terms, Disclaimer, About, Contact).")
                if found_banned: score -= 30; advice_list.append(f"Remove prohibited words immediately: {', '.join(found_banned)}.")
                if avg_word_count < 500: score -= 15; advice_list.append(f"Thin Content detected (Avg {avg_word_count} words/page). Write detailed, 800+ word articles.")
                if h1_tags != 1: score -= 5; advice_list.append("SEO Error: Ensure every page has exactly ONE H1 tag.")
                if not has_sitemap: score -= 10; advice_list.append("Sitemap missing. Generate 'sitemap.xml' and submit to Google Search Console.")
                if under_construction: score -= 25; advice_list.append("Remove placeholder text like 'Coming Soon' or 'Lorem Ipsum'.")
                if img_total > 0 and (img_alt/img_total) < 0.5: score -= 5; advice_list.append("More than 50% of your images are missing Alt tags. Add them for Image SEO.")

                score = max(0, min(score, 100))
                
                status.update(label="✅ Deep Audit Complete!", state="complete", expanded=False)

                # --- 4. PREMIUM UI DASHBOARD PRESENTATION ---
                
                # Dynamic Color for Score
                score_color = "#22c55e" if score >= 80 else "#eab308" if score >= 50 else "#ef4444"
                
                st.markdown(f"""
                <div class="metric-container">
                    <div class="metric-card" style="border-top-color: {score_color};">
                        <div class="metric-label">Approval Odds</div>
                        <div class="metric-value" style="color: {score_color};">{score}%</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Content Depth</div>
                        <div class="metric-value">{avg_word_count} <span style="font-size:14px; color:#64748b;">words/page</span></div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Server Speed</div>
                        <div class="metric-value">{load_time}s</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Pages Scanned</div>
                        <div class="metric-value">{pages_scanned}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.progress(score / 100)
                st.write("")

                # --- TABS FOR DETAILED REPORT ---
                t1, t2, t3, t4, t5 = st.tabs(["🛡️ Policy & Security", "📝 Content Quality", "⚙️ Tech SEO", "🔗 Architecture", "🌐 AdSense Status"])
                
                def render_badge(condition, pass_text, fail_text, warn_condition=False, warn_text=""):
                    if warn_condition:
                        st.markdown(f"<div class='status-badge badge-warn'><span class='icon'>⚠️</span> {warn_text}</div>", unsafe_allow_html=True)
                    elif condition:
                        st.markdown(f"<div class='status-badge badge-pass'><span class='icon'>✅</span> {pass_text}</div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div class='status-badge badge-fail'><span class='icon'>❌</span> {fail_text}</div>", unsafe_allow_html=True)

                with t1:
                    render_badge(has_ssl, "SSL Certificate is Active & Secure (HTTPS)", "SSL Certificate Missing! Critical for AdSense.")
                    render_badge(len(found_essentials) >= 4, f"Essential Pages Found ({len(found_essentials)}/5 detected)", f"Missing Essential Pages! Need Privacy, Terms, Disclaimer, etc.")
                    render_badge(not found_banned, "100% Clean: No Prohibited Content Found", f"Danger: Prohibited Words Found ({', '.join(found_banned)})")
                    render_badge(not under_construction, "Website is Live & Ready", "Template/Placeholder text found! Site looks under construction.")
                    render_badge(cookie_consent, "Cookie Consent Banner Detected (GDPR Ready)", "", warn_condition=(not cookie_consent), warn_text="Cookie Notice missing. Recommended for EU traffic.")

                with t2:
                    render_badge(avg_word_count >= 600, f"Rich Content Depth (Avg {avg_word_count} words/page)", f"Thin Content (Avg {avg_word_count} words/page). Risk of 'Low Value Content'.", warn_condition=(300 <= avg_word_count < 600), warn_text=f"Average Content (Avg {avg_word_count} words/page). Increase to 800+ for safety.")
                    render_badge(has_title and has_desc, "Meta Title & Description perfectly optimized", "Missing crucial Meta Title or Description tags.")
                    render_badge(h1_tags == 1, "Perfect Heading Hierarchy (1 H1 tag per page)", f"Heading Error: Found {h1_tags} H1 tags. Exactly 1 is required.")
                    render_badge(True, "Originality Check Required", "", warn_condition=True, warn_text="Reminder: AI cannot verify plagiarism here. Ensure content is 100% human-written.")

                with t3:
                    render_badge(status_200, "Server Response: 200 OK", "Server Unreachable or Blocking Bots")
                    render_badge(load_time <= 2.5, f"Excellent Load Speed ({load_time}s)", f"Poor Load Speed ({load_time}s)", warn_condition=(2.5 < load_time <= 4.0), warn_text=f"Average Speed ({load_time}s). Try caching or image compression.")
                    render_badge(has_viewport, "Mobile Responsive (Viewport detected)", "Not Mobile Friendly! AdSense requires responsive design.")
                    render_badge(img_total > 0 and (img_alt/img_total) > 0.8, f"Images Optimized ({img_alt}/{img_total} Alt Tags)", "", warn_condition=(img_total > 0 and (img_alt/img_total) <= 0.8), warn_text=f"Missing Alt Tags ({img_alt}/{img_total} images have Alt text).")

                with t4:
                    render_badge(has_robots, "Robots.txt found (Search Engines can crawl)", "Robots.txt is missing!")
                    render_badge(has_sitemap, "Sitemap.xml found (Good for indexing)", "Sitemap.xml is missing! Crucial for Google Search Console.")
                    render_badge(s_404 == 0, "No Broken Internal Links (404) Detected", f"Warning: {s_404} Broken Links Found!")
                    render_badge(len(internal_urls) > 10, f"Strong Internal Linking ({len(internal_urls)} links crawled)", f"Weak Internal Linking (Only {len(internal_urls)} links). Add navigation menus.")

                with t5:
                    if has_adsense_code:
                        st.info("ℹ️ **AdSense Publisher Code Detected!** It seems you have already applied or placed ad codes on your site.")
                    else:
                        st.info("ℹ️ **No AdSense Code Detected.** Ready to paste your publisher code in the `<head>` tag.")
                    
                    render_badge(True, "", "", warn_condition=True, warn_text="Traffic Source: Ensure your traffic is organic (Google/Bing). Social traffic may cause ad limits.")
                    render_badge(True, "", "", warn_condition=True, warn_text="Domain Age: AdSense prefers domains older than 1 month (6 months in some regions).")

                # --- 5. ACTIONABLE ADVICE (TO-DO LIST) ---
                st.markdown("<br><br>", unsafe_allow_html=True)
                st.markdown("### 📋 Executive Audit Summary & Next Steps")
                
                if score >= 90 and not advice_list:
                    st.success("🎉 **Outstanding!** Your website is in top 1% condition. Go ahead and apply for AdSense right now!")
                else:
                    st.markdown("<div class='advice-wrapper'>", unsafe_allow_html=True)
                    st.markdown("<p style='color: #475569; font-weight: 600; margin-bottom: 15px;'>Fix the following issues before applying to avoid rejection:</p>", unsafe_allow_html=True)
                    for idx, advice in enumerate(advice_list):
                        st.markdown(f"<div class='advice-item'><b>{idx+1}.</b> {advice}</div>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)

            except Exception as e:
                st.error(f"❌ **Connection Failed:** Could not scan the URL. Ensure the website is live, does not block bots (Cloudflare/Captcha), and the URL is correct.")

# Footer
st.markdown("<br><hr><p style='text-align:center; color:#94a3b8; font-size: 13px;'>Powered by Radar Pro V5 Algorithm • Free Enterprise Auditor</p>", unsafe_allow_html=True)
