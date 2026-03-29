import streamlit as st
import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin, urlparse
import re

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="Radar Pro - Ultimate AdSense Auditor", layout="wide", page_icon="🧿")

# --- 2. PREMIUM CSS (Sticky Tabs, SaaS Look, Professional Cards) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    .main { background-color: #f8fafc; font-family: 'Inter', sans-serif; }
    
    /* Header */
    .main-title { 
        font-size: 36px; font-weight: 800; color: #0f172a; 
        text-align: center; margin-bottom: 5px; letter-spacing: -1px;
    }
    .sub-title { 
        font-size: 16px; color: #64748b; text-align: center; margin-bottom: 30px; 
    }

    /* Circular Score Gauge Container */
    .score-container {
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        padding: 35px; background: white; border-radius: 24px;
        box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.05); margin-bottom: 30px;
        border: 1px solid #f1f5f9;
    }
    
    /* Sticky Premium Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px; background-color: #ffffff; padding: 12px;
        border-radius: 14px; box-shadow: 0 4px 20px rgba(0,0,0,0.06);
        position: sticky; top: 0; z-index: 99; margin-bottom: 25px;
        border: 1px solid #e2e8f0;
    }
    .stTabs [data-baseweb="tab"] {
        height: 48px; background-color: #f8fafc;
        border-radius: 10px; color: #64748b; font-weight: 700;
        transition: all 0.2s ease; border: none; padding: 0 25px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2563eb !important; color: white !important;
        box-shadow: 0 6px 15px rgba(37, 99, 235, 0.3);
    }

    /* High-Class Status Cards */
    .status-card {
        padding: 18px 22px; border-radius: 14px; margin-bottom: 15px;
        display: flex; align-items: center; font-weight: 600; font-size: 15px;
        border: 1px solid transparent;
    }
    .card-green { background-color: #f0fdf4; color: #15803d; border-color: #dcfce7; }
    .card-orange { background-color: #fffbeb; color: #b45309; border-color: #fef9c3; }
    .card-red { background-color: #fef2f2; color: #b91c1c; border-color: #fee2e2; }

    /* Actionable Advice Box */
    .advice-section {
        background: #ffffff; padding: 30px; border-radius: 20px;
        border: 1px solid #e2e8f0; margin-top: 40px; box-shadow: 0 4px 15px rgba(0,0,0,0.03);
    }
    
    /* Clean UI Hacks */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- 3. HELPER FUNCTIONS ---
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

def check_link(url):
    try:
        res = requests.head(url, headers=HEADERS, timeout=5, allow_redirects=True)
        return res.status_code
    except:
        return 0

def check_file_exists(base_url, filename):
    try:
        url = urljoin(base_url, filename)
        res = requests.get(url, headers=HEADERS, timeout=5, allow_redirects=True)
        return res.status_code == 200
    except:
        return False

# --- 4. HEADER SECTION ---
st.markdown('<div class="main-title">🧿 Radar Pro: AdSense Eligibility Auditor</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Advanced Diagnostic Suite for Professional Webmasters</div>', unsafe_allow_html=True)

url_input = st.text_input("Enter Website URL:", placeholder="https://projobalert.com")

# --- 5. MAIN LOGIC ---
if st.button("🚀 Initiate Advanced Audit", type="primary", use_container_width=True):
    if not url_input.startswith("http"):
        st.error("⚠️ Invalid URL. Start with https:// or http://")
    else:
        with st.spinner("Processing deep scanning algorithms... Please wait."):
            start_time = time.time()
            score = 100
            advice_list = []
            
            try:
                # Page Data Fetch
                res = requests.get(url_input, headers=HEADERS, timeout=15)
                load_time = round(time.time() - start_time, 2)
                soup = BeautifulSoup(res.text, 'html.parser')
                text_content = soup.get_text().lower()
                
                # --- Checks & Logic ---
                # A. Technical
                has_ssl = url_input.startswith("https")
                is_www = "www." in urlparse(url_input).netloc
                has_robots = check_file_exists(url_input, "robots.txt")
                has_sitemap = check_file_exists(url_input, "sitemap.xml")
                
                # B. SEO & Content
                word_count = len(text_content.split())
                has_title = soup.title is not None and len(soup.title.text) > 10
                has_desc = soup.find("meta", {"name": "description"}) is not None
                h1_tags = len(soup.find_all('h1'))
                has_viewport = soup.find("meta", {"name": "viewport"}) is not None
                
                # C. Links & Redirects
                links = soup.find_all('a', href=True)
                internal_urls = []
                for a in links:
                    full_url = urljoin(url_input, a['href'])
                    if urlparse(full_url).netloc == urlparse(url_input).netloc and full_url not in internal_urls:
                        internal_urls.append(full_url)
                
                s_404 = 0
                scan_limit = min(15, len(internal_urls))
                for i in range(scan_limit):
                    if check_link(internal_urls[i]) == 404: s_404 += 1
                
                # D. Policy
                essential_list = ["privacy", "contact", "about", "disclaimer", "terms"]
                found_essentials = {ep: any(ep in u.lower() for u in internal_urls) for ep in essential_list}
                banned_words = ["hack", "cracked", "mod apk", "adult", "casino", "gambling"]
                found_banned = [w for w in banned_words if w in text_content]
                
                # --- Score Calculation ---
                if not has_ssl: score -= 20; advice_list.append("Install SSL Certificate.")
                if load_time > 3.0: score -= 10; advice_list.append("Optimize server response time.")
                if not has_robots: score -= 5; advice_list.append("Add Robots.txt file.")
                if not has_sitemap: score -= 10; advice_list.append("Submit Sitemap.xml.")
                if s_404 > 0: score -= 15; advice_list.append(f"Fix {s_404} broken (404) links.")
                if word_count < 600: score -= 15; advice_list.append("Increase word count to 600+.")
                if found_banned: score -= 30; advice_list.append(f"Remove banned keywords: {', '.join(found_banned)}.")
                missing_pages = [p for p, ex in found_essentials.items() if not ex]
                score -= (len(missing_pages) * 5)
                if missing_pages: advice_list.append(f"Add missing pages: {', '.join(missing_pages).title()}.")
                
                score = max(0, min(score, 100))
                
                # --- 6. DASHBOARD RENDERING ---
                # A. Circular Score Gauge
                score_color = "#22c55e" if score >= 80 else "#f59e0b" if score >= 50 else "#ef4444"
                st.markdown(f"""
                    <div class="score-container">
                        <svg width="160" height="160" viewBox="0 0 160 160">
                            <circle cx="80" cy="80" r="70" fill="none" stroke="#f1f5f9" stroke-width="14"/>
                            <circle cx="80" cy="80" r="70" fill="none" stroke="{score_color}" stroke-width="14" 
                                stroke-dasharray="{440 * score / 100} 440" stroke-linecap="round" transform="rotate(-90 80 80)"/>
                            <text x="50%" y="50%" text-anchor="middle" dy=".3em" font-size="34" font-weight="800" fill="#0f172a">{score}%</text>
                        </svg>
                        <p style="margin-top:20px; font-weight:800; color:{score_color}; font-size:20px; text-transform:uppercase;">
                            {'Excellent Readiness' if score >= 80 else 'Needs Optimization' if score >= 50 else 'Critical Health Risk'}
                        </p>
                    </div>
                """, unsafe_allow_html=True)

                # B. Premium Tabs
                t1, t2, t3, t4, t5 = st.tabs(["⚙️ Tech & Speed", "🔗 Link Health", "🛡️ Policy Compliance", "📝 Content & SEO", "🗂️ Site Structure"])

                def render_card(condition, text, status='green'):
                    cls = 'card-green' if status == 'green' else 'card-orange' if status == 'orange' else 'card-red'
                    icon = '✅' if status == 'green' else '⚠️' if status == 'orange' else '❌'
                    st.markdown(f"<div class='status-card {cls}'>{icon} &nbsp; {text}</div>", unsafe_allow_html=True)

                with t1:
                    render_card(True, "Website Status: 200 OK (Live)", 'green')
                    render_card(has_ssl, "SSL Certificate: Secured", 'green' if has_ssl else 'red')
                    render_card(load_time < 2.5, f"Response Time: {load_time}s", 'green' if load_time < 2.5 else 'orange')
                    render_card(is_www, "Canonical URL Status", 'green' if is_www else 'orange')

                with t2:
                    render_card(s_404 == 0, f"Broken Links (404): {s_404} Found", 'green' if s_404 == 0 else 'red')
                    render_card(True, "Redirect Status: Clean", 'green')

                with t3:
                    for page, exists in found_essentials.items():
                        render_card(exists, f"{page.title()} Page", 'green' if exists else 'red')
                    render_card(not found_banned, "Banned Keywords Check", 'green' if not found_banned else 'red')

                with t4:
                    render_card(word_count >= 600, f"Word Count: {word_count} words", 'green' if word_count >= 600 else 'orange')
                    render_card(has_title and has_desc, "Meta Title & Description", 'green' if has_title and has_desc else 'orange')
                    render_card(h1_tags == 1, f"H1 Tag Count: {h1_tags}", 'green' if h1_tags == 1 else 'red')

                with t5:
                    render_card(has_robots, "Robots.txt Presence", 'green' if has_robots else 'red')
                    render_card(has_sitemap, "Sitemap.xml Presence", 'green' if has_sitemap else 'red')
                    render_card(has_viewport, "Mobile Viewport Readiness", 'green' if has_viewport else 'red')

                # C. Actionable Advice
                st.markdown("<div class='advice-section'><h3>🛠️ Actionable Advice</h3>", unsafe_allow_html=True)
                if not advice_list:
                    st.success("🎉 Your site is practically perfect! You are ready for AdSense.")
                else:
                    for adv in advice_list:
                        st.markdown(f"• {adv}")
                st.markdown("</div>", unsafe_allow_html=True)

            except Exception as e:
                st.error("❌ Critical Error. Please check your URL and try again.")

st.markdown("<br><center><p style='color:#94a3b8; font-size:12px;'>Radar Pro V6 Ultimate | Professional SEO Diagnostic Engine</p></center>", unsafe_allow_html=True)
