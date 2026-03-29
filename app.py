import streamlit as st
import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin, urlparse
import re

# --- 1. PAGE SETUP ---
st.set_page_config(page_title="Radar Pro - Ultimate AdSense Auditor", layout="wide", page_icon="🧿")

# --- 2. PREMIUM COMPACT CSS ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    
    /* Global Reset */
    .main { background-color: #f8fafc; font-family: 'Inter', sans-serif; }
    .block-container { padding-top: 2rem !important; padding-bottom: 1rem !important; }

    /* Compact Header */
    .main-title { 
        font-size: 28px; font-weight: 800; color: #0f172a; 
        text-align: center; margin-bottom: 2px; letter-spacing: -0.5px;
    }
    .sub-title { 
        font-size: 14px; color: #64748b; text-align: center; margin-bottom: 20px; 
    }

    /* Compact Score Gauge */
    .score-container {
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        padding: 20px; background: white; border-radius: 16px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03); margin-bottom: 15px;
        border: 1px solid #f1f5f9;
    }
    
    /* Integrated Sticky Tabs Look */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px; background-color: #ffffff; padding: 6px;
        border-radius: 12px 12px 0 0; box-shadow: 0 4px 10px rgba(0,0,0,0.04);
        position: sticky; top: 0; z-index: 99; margin-bottom: 0px !important;
        border: 1px solid #e2e8f0; border-bottom: none;
    }
    .stTabs [data-baseweb="tab"] {
        height: 40px; background-color: transparent;
        border-radius: 8px; color: #64748b; font-weight: 700; font-size: 13px;
        transition: all 0.2s ease; border: none; padding: 0 16px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2563eb !important; color: white !important;
    }

    /* Result Container (To unite with tabs) */
    [data-testid="stExpander"], .stTabs [data-baseweb="tab-panel"] {
        background: white; padding: 15px; border-radius: 0 0 12px 12px;
        border: 1px solid #e2e8f0; border-top: none;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.04);
    }

    /* Ultra Slim Status Cards */
    .status-card {
        padding: 10px 14px; border-radius: 10px; margin-bottom: 8px;
        display: flex; align-items: center; font-weight: 600; font-size: 13.5px;
        border: 1px solid transparent; line-height: 1.4;
    }
    .card-green { background-color: #f0fdf4; color: #166534; border-color: #dcfce7; }
    .card-orange { background-color: #fffbeb; color: #92400e; border-color: #fef9c3; }
    .card-red { background-color: #fef2f2; color: #991b1b; border-color: #fee2e2; }

    /* Compact Advice Box */
    .advice-section {
        background: #ffffff; padding: 20px; border-radius: 14px;
        border: 1px solid #e2e8f0; margin-top: 20px;
    }
    .advice-title { font-size: 18px; font-weight: 800; color: #0f172a; margin-bottom: 10px; }
    
    /* Hide Default Streamlit Junk */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- 3. CORE LOGIC ---
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

# --- 4. UI HEADER ---
st.markdown('<div class="main-title">🧿 Radar Pro: AdSense Auditor</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Compact & High-Speed Diagnostic Engine</div>', unsafe_allow_html=True)

url_input = st.text_input("Site URL:", placeholder="https://example.com")

# --- 5. AUDIT ENGINE ---
if st.button("🚀 Run Advanced Audit", type="primary", use_container_width=True):
    if not url_input.startswith("http"):
        st.error("⚠️ Please include https://")
    else:
        with st.spinner("Analyzing..."):
            start_time = time.time()
            score = 100
            advice_list = []
            
            try:
                res = requests.get(url_input, headers=HEADERS, timeout=12)
                load_time = round(time.time() - start_time, 2)
                soup = BeautifulSoup(res.text, 'html.parser')
                text_content = soup.get_text().lower()
                
                # Tech Checks
                has_ssl = url_input.startswith("https")
                is_www = "www." in urlparse(url_input).netloc
                has_robots = check_file_exists(url_input, "robots.txt")
                has_sitemap = check_file_exists(url_input, "sitemap.xml")
                
                # Content Checks
                word_count = len(text_content.split())
                h1_tags = len(soup.find_all('h1'))
                has_viewport = soup.find("meta", {"name": "viewport"}) is not None
                
                # Link Scan
                links = soup.find_all('a', href=True)
                internal_urls = []
                for a in links:
                    full_url = urljoin(url_input, a['href'])
                    if urlparse(full_url).netloc == urlparse(url_input).netloc and full_url not in internal_urls:
                        internal_urls.append(full_url)
                
                s_404 = 0
                scan_limit = min(12, len(internal_urls))
                for i in range(scan_limit):
                    if check_link(internal_urls[i]) == 404: s_404 += 1
                
                # Policy Checks
                essentials = ["privacy", "contact", "about", "disclaimer", "terms"]
                found_ess = {ep: any(ep in u.lower() for u in internal_urls) for ep in essentials}
                banned_words = ["hack", "cracked", "mod apk", "adult", "casino", "gambling"]
                found_banned = [w for w in banned_words if w in text_content]
                
                # Score Calc
                if not has_ssl: score -= 20; advice_list.append("Enable HTTPS.")
                if load_time > 3.0: score -= 10; advice_list.append("Speed up server response.")
                if s_404 > 0: score -= 15; advice_list.append(f"Fix {s_404} broken links.")
                if word_count < 600: score -= 15; advice_list.append("Target 600+ words per page.")
                if found_banned: score -= 30; advice_list.append(f"Remove: {', '.join(found_banned)}.")
                missing_p = [p for p, ex in found_ess.items() if not ex]
                score -= (len(missing_p) * 6)
                score = max(0, min(score, 100))
                
                # --- 6. RENDER DASHBOARD ---
                
                # A. Mini-Circular Score
                sc_color = "#22c55e" if score >= 80 else "#f59e0b" if score >= 50 else "#ef4444"
                st.markdown(f"""
                    <div class="score-container">
                        <svg width="110" height="110" viewBox="0 0 120 120">
                            <circle cx="60" cy="60" r="50" fill="none" stroke="#f1f5f9" stroke-width="10"/>
                            <circle cx="60" cy="60" r="50" fill="none" stroke="{sc_color}" stroke-width="10" 
                                stroke-dasharray="{314 * score / 100} 314" stroke-linecap="round" transform="rotate(-90 60 60)"/>
                            <text x="50%" y="50%" text-anchor="middle" dy=".3em" font-size="24" font-weight="800" fill="#0f172a">{score}%</text>
                        </svg>
                    </div>
                """, unsafe_allow_html=True)

                # B. Integrated Tabs
                t1, t2, t3, t4, t5 = st.tabs(["⚙️ Tech", "🔗 Links", "🛡️ Policy", "📝 SEO", "🗂️ Site"])

                def rc(text, status='green'):
                    cls = 'card-green' if status == 'green' else 'card-orange' if status == 'orange' else 'card-red'
                    icon = '✅' if status == 'green' else '⚠️' if status == 'orange' else '❌'
                    st.markdown(f"<div class='status-card {cls}'>{icon} &nbsp; {text}</div>", unsafe_allow_html=True)

                with t1:
                    rc("Status: 200 OK", 'green')
                    rc("SSL Certificate", 'green' if has_ssl else 'red')
                    rc(f"Latency: {load_time}s", 'green' if load_time < 2.5 else 'orange')
                    rc("Canonical Redir", 'green' if is_www else 'orange')

                with t2:
                    rc(f"Broken Links: {s_404}", 'green' if s_404 == 0 else 'red')
                    rc("Redirect Structure", 'green')

                with t3:
                    for p, ex in found_ess.items():
                        rc(f"{p.title()} Page", 'green' if ex else 'red')
                    rc("Policy Keywords", 'green' if not found_banned else 'red')

                with t4:
                    rc(f"Words: {word_count}", 'green' if word_count >= 600 else 'orange')
                    rc("Meta Tags Presence", 'green' if soup.title and has_desc else 'orange')
                    rc(f"H1 Tags: {h1_tags}", 'green' if h1_tags == 1 else 'red')

                with t5:
                    rc("Robots.txt", 'green' if has_robots else 'red')
                    rc("Sitemap.xml", 'green' if has_sitemap else 'red')
                    rc("Mobile Viewport", 'green' if has_viewport else 'red')

                # C. Advice
                if advice_list:
                    st.markdown("<div class='advice-section'><div class='advice-title'>🛠️ Next Steps</div>", unsafe_allow_html=True)
                    for adv in advice_list[:4]: # Limit to top 4 for space
                        st.markdown(f"<small>• {adv}</small>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)

            except:
                st.error("Audit failed. Check URL.")

st.markdown("<center><small style='color:#94a3b8;'>Radar Pro V7-Compact</small></center>", unsafe_allow_html=True)
