import streamlit as st
import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin, urlparse
import re
import concurrent.futures
from datetime import datetime
import random

# Try importing whois for domain age
try:
    import whois
    WHOIS_AVAILABLE = True
except ImportError:
    WHOIS_AVAILABLE = False

# --- 1. PAGE SETUP & AGGRESSIVE CSS (NO TRIMMING) ---
st.set_page_config(page_title="Radar Pro V7.2 | Elite AdSense Auditor", layout="wide", page_icon="🧿")

st.markdown("""
    <style>
    /* 🛡️ ANTI-IFRAME BRANDING (Hides Streamlit Badge & Fullscreen) */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden; display: none !important;}
    header {visibility: hidden; display: none !important;}
    .viewerBadge_container__1QS98 {display: none !important;}
    .stAppDeployButton {display: none !important;}
    [data-testid="stStatusWidget"] {display: none !important;}
    button[title="View fullscreen"] { display: none !important; }
    
    /* Overall Design */
    .stApp { background-color: #f8fafc; font-family: 'Inter', sans-serif; }
    
    /* Hero Section */
    .hero-box {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        padding: 40px 20px; border-radius: 15px; text-align: center;
        margin-bottom: 30px; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2);
    }
    .hero-title { font-size: 42px; font-weight: 900; color: #ffffff; margin-bottom: 5px; line-height: 1.2;}
    .hero-title span { color: #3b82f6; }
    .hero-subtitle { font-size: 16px; color: #94a3b8; }
    
    /* Metric Cards */
    .metric-container { display: flex; justify-content: space-between; gap: 15px; margin-bottom: 25px; flex-wrap: wrap; }
    .metric-card {
        background: white; padding: 20px; border-radius: 12px; flex: 1; min-width: 150px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); border-top: 4px solid #3b82f6; text-align: center;
    }
    .metric-value { font-size: 30px; font-weight: 800; color: #0f172a; margin-top: 5px;}
    .metric-label { font-size: 12px; color: #64748b; font-weight: 700; text-transform: uppercase; letter-spacing: 1px;}

    /* Swipeable Carousel & Menu */
    .slider-nav {
        display: flex; overflow-x: auto; gap: 10px; margin-bottom: 20px; padding-bottom: 10px;
        scrollbar-width: none; -ms-overflow-style: none;
    }
    .slider-nav::-webkit-scrollbar { display: none; }
    .slider-nav-btn {
        background: #f1f5f9; color: #475569; padding: 10px 20px; border-radius: 30px;
        font-weight: 700; font-size: 14px; white-space: nowrap; cursor: pointer;
        border: 2px solid #e2e8f0; transition: all 0.3s ease;
    }
    .slider-container {
        display: flex; overflow-x: auto; scroll-snap-type: x mandatory; gap: 15px;
        padding-bottom: 20px; scrollbar-width: none; -ms-overflow-style: none; scroll-behavior: smooth;
    }
    .slider-container::-webkit-scrollbar { display: none; }
    .slider-card {
        flex: 0 0 88%; scroll-snap-align: center; background: white; border: 1px solid #e2e8f0;
        border-top: 4px solid #3b82f6; border-radius: 12px; padding: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
    @media (min-width: 768px) { .slider-card { flex: 0 0 calc(33.333% - 14px); } }
    
    .card-title { font-size: 18px; font-weight: 800; color: #0f172a; margin-bottom: 15px; border-bottom: 2px solid #f1f5f9; padding-bottom: 10px;}
    
    /* Health Badges */
    .status-badge { display: flex; align-items: flex-start; padding: 12px 15px; border-radius: 8px; margin-bottom: 12px; font-weight: 600; font-size: 13.5px; line-height: 1.4; border-left: 5px solid #ccc;}
    .badge-pass { background-color: #dcfce7; color: #166534; border-color: #22c55e; }
    .badge-warn { background-color: #fef9c3; color: #854d0e; border-color: #eab308; }
    .badge-fail { background-color: #fee2e2; color: #991b1b; border-color: #ef4444; }

    /* Advice Wrapper */
    .advice-wrapper { background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; margin-top: 15px; }
    .advice-header { font-size: 18px; font-weight: 800; color: #0f172a; border-bottom: 2px solid #e2e8f0; padding-bottom: 12px; margin-bottom: 15px; text-transform: uppercase;}
    .advice-item { background: #fef2f2; padding: 15px; border-radius: 8px; margin-bottom: 12px; border-left: 5px solid #ef4444; color: #7f1d1d; font-weight: 500;}
    .advice-item-success { background: #f0fdf4; padding: 15px; border-radius: 8px; margin-bottom: 12px; border-left: 5px solid #22c55e; color: #14532d; font-weight: 500;}
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown("""
    <div class="hero-box">
        <div class="hero-title">🧿 Radar <span>Pro</span> Max</div>
        <div class="hero-subtitle">Swipeable 50-Page Engine • Professional Iframe-Ready Edition</div>
    </div>
""", unsafe_allow_html=True)

url_input = st.text_input("Enter Website URL:", placeholder="https://yourwebsite.com", label_visibility="collapsed")

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
}

# 🛡️ STEALTH FUNCTION
def fetch_and_analyze_page(url):
    try:
        time.sleep(random.uniform(0.2, 0.7)) # Jitter
        res = requests.get(url, headers=HEADERS, timeout=12, allow_redirects=True)
        is_loop = len(res.history) >= 3 
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            text = soup.get_text().lower()
            # Extract basic SEO info for deep analysis
            h1s = len(soup.find_all('h1'))
            return {'url': url, 'status': res.status_code, 'words': len(text.split()), 'loop': is_loop, 'history': res.history, 'text': text, 'h1s': h1s}
        return {'url': url, 'status': res.status_code, 'words': 0, 'loop': is_loop, 'history': res.history, 'text': "", 'h1s': 0}
    except:
        return {'url': url, 'status': 0, 'words': 0, 'loop': False, 'history':[], 'text': "", 'h1s': 0}

def get_badge_html(condition, pass_text, fail_text, warn_condition=False, warn_text=""):
    cls = "badge-pass" if condition else "badge-fail"
    if warn_condition: cls = "badge-warn"
    icon = "✅" if condition and not warn_condition else "⚠️" if warn_condition else "❌"
    txt = warn_text if warn_condition else (pass_text if condition else fail_text)
    return f"<div class='status-badge {cls}'><span style='margin-right:10px;'>{icon}</span><div>{txt}</div></div>"

# --- MAIN ENGINE ---
if st.button("🚀 INITIATE DEEP SCAN", type="primary", use_container_width=True):
    if not url_input.strip() or not url_input.startswith(("http://", "https://")):
        st.error("⚠️ Please enter a valid URL.")
    else:
        loading_box = st.empty()
        start_time = time.time()
        score, advice_list = 100, []
        
        try:
            loading_box.info("⏳ 🌍 Crawling Homepage & Analyzing Server...")
            main_res = requests.get(url_input, headers=HEADERS, timeout=15)
            load_time = round(time.time() - start_time, 2)
            soup = BeautifulSoup(main_res.text, 'html.parser')
            main_text = soup.get_text().lower()
            has_adsense_code = "pagead2.googlesyndication.com" in main_res.text
            
            # Link Extraction
            links = soup.find_all('a', href=True)
            internal_urls = list(set([urljoin(url_input, a['href']).split('#')[0] for a in links if urlparse(urljoin(url_input, a['href'])).netloc == urlparse(url_input).netloc]))
            
            scan_list = internal_urls[:50]
            if url_input not in scan_list: scan_list.insert(0, url_input)
            
            loading_box.warning(f"⏳ 🥷 Stealth Mode: Deep Scanning {len(scan_list)} pages...")
            
            scanned_pages_data = []
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                scanned_pages_data = list(executor.map(fetch_and_analyze_page, scan_list))
            
            # Deep Math
            s_200 = sum(1 for p in scanned_pages_data if p['status'] == 200)
            s_404 = sum(1 for p in scanned_pages_data if p['status'] >= 400)
            redirect_loops = sum(1 for p in scanned_pages_data if p['loop'])
            avg_word_count = sum(p['words'] for p in scanned_pages_data) // max(1, len([p for p in scanned_pages_data if p['words'] > 0]))
            combined_text = " ".join([p['text'] for p in scanned_pages_data])
            
            loading_box.success("⏳ 🛡️ Finalizing Security & Policy Audit...")
            
            # Logic Checks (No Trimming)
            has_ssl = url_input.startswith("https")
            found_essentials = [ep for ep in ["privacy", "contact", "about", "disclaimer", "terms"] if any(ep in u.lower() for u in internal_urls)]
            banned_keywords = ["hack", "cracked", "mod apk", "adult", "casino", "gambling", "movie download", "porn", "nude", "violence"]
            found_banned = [w for w in banned_keywords if w in combined_text]
            
            # Readability
            sentences = max(1, len(re.split(r'[.!?]+', main_text)))
            is_readable = 8 <= (len(main_text.split()) / sentences) <= 25
            
            # Meta & Tags
            has_title = soup.title is not None and len(soup.title.text) > 10
            has_desc = soup.find("meta", {"name": "description"}) is not None
            h1_tags = len(soup.find_all('h1'))
            h2_tags = len(soup.find_all('h2'))
            img_total = len(soup.find_all('img'))
            img_alt = sum(1 for img in soup.find_all('img') if img.get('alt'))
            
            has_robots = requests.get(urljoin(url_input, "robots.txt"), headers=HEADERS, timeout=5).status_code == 200
            has_sitemap = requests.get(urljoin(url_input, "sitemap.xml"), headers=HEADERS, timeout=5).status_code == 200
            has_viewport = soup.find("meta", {"name": "viewport"}) is not None
            
            # Domain Age
            domain_days = "Unknown"
            if WHOIS_AVAILABLE:
                try:
                    d_info = whois.whois(urlparse(url_input).netloc)
                    c_date = d_info.creation_date[0] if isinstance(d_info.creation_date, list) else d_info.creation_date
                    if c_date: domain_days = (datetime.now() - c_date).days
                except: pass

            # --- Scoring Logic ---
            if not has_ssl: score -= 15; advice_list.append("Enable HTTPS (SSL) immediately.")
            if s_404 > 0: score -= 15; advice_list.append(f"Fix {s_404} broken (404) links.")
            if len(found_essentials) < 4: score -= 20; advice_list.append("Add missing Policy pages (Privacy, Terms, About).")
            if found_banned: score -= 30; advice_list.append(f"Remove prohibited content: {', '.join(set(found_banned))}.")
            if avg_word_count < 600: score -= 15; advice_list.append(f"Thin Content (Avg {avg_word_count} words). Aim for 600+.")
            if h1_tags != 1: score -= 5; advice_list.append(f"Found {h1_tags} H1 tags. Exactly ONE is required.")
            
            score = max(0, min(score, 100))
            loading_box.empty()
            st.success("✅ Deep Scan Completed!")

            # Metric Dashboard
            score_col = "#22c55e" if score >= 80 else "#eab308" if score >= 50 else "#ef4444"
            st.markdown(f"""
                <div class="metric-container">
                    <div class="metric-card" style="border-top-color:{score_col}"><div class="metric-label">Odds</div><div class="metric-value" style="color:{score_col}">{score}%</div></div>
                    <div class="metric-card"><div class="metric-label">Scan Depth</div><div class="metric-value">{len(scanned_pages_data)}</div></div>
                    <div class="metric-card"><div class="metric-label">Avg Words</div><div class="metric-value">{avg_word_count}</div></div>
                    <div class="metric-card"><div class="metric-label">Speed</div><div class="metric-value">{load_time}s</div></div>
                </div>
            """, unsafe_allow_html=True)
            st.progress(score/100)

            # Swipeable Carousel Components
            c_tech = get_badge_html(s_200 > 0, f"Status: 200 OK ({s_200} pages)", "Connection Failed") + \
                     get_badge_html(has_ssl, "SSL Secure (HTTPS)", "SSL Missing!") + \
                     get_badge_html(load_time <= 2.5, f"Fast Load ({load_time}s)", f"Slow Load ({load_time}s)", warn_condition=(2.5 < load_time < 4))
            
            c_err = get_badge_html(s_404 == 0, "No 404 Errors Found", f"Found {s_404} Broken Links") + \
                    get_badge_html(redirect_loops == 0, "No Redirect Loops", f"{redirect_loops} Loops Found")
            
            c_pol = get_badge_html(len(found_essentials) >= 4, f"Policies: {len(found_essentials)}/5 Found", "Mandatory Pages Missing") + \
                    get_badge_html(not found_banned, "Clean Content Policy", "Banned Keywords Detected")
            
            c_seo = get_badge_html(avg_word_count >= 600, f"Rich Content ({avg_word_count} words)", "Thin Content Warning", warn_condition=(400 < avg_word_count < 600)) + \
                    get_badge_html(h1_tags == 1, "Perfect H1 Structure", f"H1 Tag Error ({h1_tags} found)") + \
                    get_badge_html(is_readable, "Good Readability Score", "Poor Grammar/Readability")

            c_str = get_badge_html(has_robots, "Robots.txt Present", "Robots.txt Missing") + \
                    get_badge_html(has_sitemap, "Sitemap.xml Found", "Sitemap.xml Missing") + \
                    get_badge_html(has_viewport, "Mobile Responsive", "Mobile Viewport Missing")

            d_age_warn = (domain_days != "Unknown" and 30 <= int(domain_days) < 60)
            d_age_pass = (domain_days != "Unknown" and int(domain_days) >= 60)
            c_dom = get_badge_html(d_age_pass, f"Domain Age: {domain_days} Days", "Domain Too New", warn_condition=d_age_warn, warn_text=f"Age: {domain_days} Days (Wait 60+ days)") + \
                    get_badge_html(has_adsense_code, "AdSense Code Detected", "No AdSense Code Found", warn_condition=(not has_adsense_code))

            carousel_html = f"""
            <div class="slider-nav">
                <div class="slider-nav-btn">⚙️ Tech</div><div class="slider-nav-btn">🔗 Errors</div><div class="slider-nav-btn">🛡️ Policy</div><div class="slider-nav-btn">📝 SEO</div><div class="slider-nav-btn">🗂️ Structure</div><div class="slider-nav-btn">🌐 Domain</div>
            </div>
            <div class="slider-container">
                <div class="slider-card"><div class="card-title">⚙️ Tech & Speed</div>{c_tech}</div>
                <div class="slider-card"><div class="card-title">🔗 Errors & Links</div>{c_err}</div>
                <div class="slider-card"><div class="card-title">🛡️ AdSense Policy</div>{c_pol}</div>
                <div class="slider-card"><div class="card-title">📝 Content & SEO</div>{c_seo}</div>
                <div class="slider-card"><div class="card-title">🗂️ Site Structure</div>{c_str}</div>
                <div class="slider-card"><div class="card-title">🌐 Domain Health</div>{c_dom}</div>
            </div>
            """
            st.markdown(carousel_html, unsafe_allow_html=True)

            # Advice Section
            if not advice_list:
                st.markdown("<div class='advice-wrapper advice-success'><div class='advice-header'>🎉 EXCELLENT: SITE READY</div><div class='advice-item-success'><b>Approved:</b> Site meets all quality guidelines.</div></div>", unsafe_allow_html=True)
            else:
                advice_html = "<div class='advice-wrapper'><div class='advice-header'>⚠️ ACTION REQUIRED: FIXES</div>"
                for i, a in enumerate(advice_list): advice_html += f"<div class='advice-item'><b>{i+1}.</b> {a}</div>"
                st.markdown(advice_html + "</div>", unsafe_allow_html=True)

        except Exception as e:
            loading_box.empty()
            st.error("❌ Critical Error Scanning Site.")

st.markdown("<br><hr><center><small>Radar Pro Master V7.2 • Enterprise Edition • Anti-Iframe Distraction Enabled</small></center>", unsafe_allow_html=True)
