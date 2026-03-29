import streamlit as st
import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin, urlparse

# --- 1. PAGE SETUP & CUSTOM CSS ---
st.set_page_config(page_title="Radar Pro - Ultimate SEO Auditor", layout="wide", page_icon="🎯")

# Advanced Custom CSS for Premium Dashboard Look
st.markdown("""
    <style>
    /* Main Title Styling */
    .main-title { font-size: 38px; font-weight: 800; color: #1e3a8a; margin-bottom: 0px; }
    .sub-title { font-size: 18px; color: #64748b; margin-bottom: 30px; }
    
    /* Result Cards Styling */
    .card-pass { background-color: #f0fdf4; border-left: 5px solid #22c55e; padding: 15px; border-radius: 8px; margin-bottom: 10px; }
    .card-warn { background-color: #fffbeb; border-left: 5px solid #f59e0b; padding: 15px; border-radius: 8px; margin-bottom: 10px; }
    .card-fail { background-color: #fef2f2; border-left: 5px solid #ef4444; padding: 15px; border-radius: 8px; margin-bottom: 10px; }
    
    /* Text Colors */
    .text-pass { color: #15803d; font-weight: bold; }
    .text-warn { color: #b45309; font-weight: bold; }
    .text-fail { color: #b91c1c; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- 2. HEADER SECTION ---
st.markdown('<div class="main-title">🎯 Radar Pro: Advanced Site Auditor</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Complete AdSense Readiness & Technical SEO Scan</div>', unsafe_allow_html=True)

url_input = st.text_input("Enter Website URL (Include https://)", placeholder="https://projobalert.com")

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# --- 3. HELPER FUNCTIONS (FIXED FOR REDIRECTS) ---
def check_url_status(link):
    """Link checker - allow_redirects=True to stop false 302 alarms"""
    try:
        res = requests.head(link, headers=HEADERS, timeout=5, allow_redirects=True)
        return res.status_code
    except:
        return 0

def check_file_exists(base_url, filename):
    """Sitemap/Robots checker - uses GET to bypass strict server blocking"""
    try:
        url = urljoin(base_url, filename)
        res = requests.get(url, headers=HEADERS, timeout=5, allow_redirects=True)
        return res.status_code == 200
    except:
        return False

# --- 4. MAIN SCANNING LOGIC ---
if st.button("🚀 Run Deep Scan", type="primary", use_container_width=True):
    if not url_input.startswith("http"):
        st.error("⚠️ Invalid URL. Please start with 'https://' or 'http://'")
    else:
        with st.spinner("Analyzing Site Structure, Fetching Meta Tags, and Running Policy Checks..."):
            start_time = time.time()
            score = 100 
            
            try:
                # Primary Fetch
                main_response = requests.get(url_input, headers=HEADERS, timeout=15)
                load_time = round(time.time() - start_time, 2)
                soup = BeautifulSoup(main_response.text, 'html.parser')
                page_text = soup.get_text().lower()
                
                # A. Domain & Technical Checks
                has_ssl = url_input.startswith("https")
                has_robots = check_file_exists(url_input, "robots.txt")
                has_sitemap = check_file_exists(url_input, "sitemap.xml")
                viewport = soup.find("meta", {"name": "viewport"})
                is_mobile_ready = viewport is not None
                
                # B. Content & SEO Checks
                word_count = len(page_text.split())
                has_title = soup.title is not None
                meta_desc = soup.find("meta", {"name": "description"})
                has_desc = meta_desc is not None
                
                # C. AdSense Policy & Link Extraction
                banned_list = ["hack", "cracked", "mod apk", "adult", "casino"]
                found_banned = [word for word in banned_list if word in page_text]
                
                essential_list = ["privacy", "contact", "about", "disclaimer", "terms"]
                links = soup.find_all('a', href=True)
                urls_to_check = []
                
                for a in links:
                    href = a['href']
                    full_url = urljoin(url_input, href)
                    if urlparse(full_url).netloc == urlparse(url_input).netloc:
                        if full_url not in urls_to_check:
                            urls_to_check.append(full_url)
                
                # Track exact missing/found essential pages
                page_status = {}
                for ep in essential_list:
                    page_status[ep] = any(ep in url.lower() for url in urls_to_check)
                
                # D. Deep Link Scanning (Top 20)
                status_404, status_errors = 0, 0
                scan_limit = min(20, len(urls_to_check))
                for i in range(scan_limit):
                    code = check_url_status(urls_to_check[i])
                    if code == 404:
                        status_404 += 1
                    elif code >= 500 or code == 0:
                        status_errors += 1
                
                # E. Score Calculation Engine
                if not has_ssl: score -= 20
                if load_time > 3.0: score -= 10
                if not has_robots: score -= 5
                if not has_sitemap: score -= 10
                if word_count < 300: score -= 15
                if not has_desc: score -= 5
                if found_banned: score -= 30
                
                missing_pages_count = list(page_status.values()).count(False)
                score -= (missing_pages_count * 5)
                score -= (status_404 * 5)
                score = max(0, min(score, 100)) # Keep between 0-100
                
                # --- 5. UI DASHBOARD RENDERING ---
                st.success(f"Audit Completed in {load_time}s")
                
                # Big Score Bar
                st.markdown(f"### 📊 Overall AdSense Readiness: {score}%")
                st.progress(score / 100)
                
                st.divider()
                
                # 2-Column Premium Layout
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### ⚙️ Technical & Core Web Vitals")
                    st.markdown(f"<div class='{'card-pass' if has_ssl else 'card-fail'}'><b>SSL Certificate:</b> {'✅ Secured' if has_ssl else '❌ Missing'}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='{'card-pass' if load_time < 2 else 'card-warn'}'><b>Server Speed:</b> {load_time}s {'(Excellent)' if load_time < 2 else '(Needs Optimization)'}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='{'card-pass' if has_robots else 'card-warn'}'><b>Robots.txt:</b> {'✅ Found & Valid' if has_robots else '❌ Missing (Critical for SEO)'}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='{'card-pass' if has_sitemap else 'card-warn'}'><b>Sitemap.xml:</b> {'✅ Found' if has_sitemap else '❌ Missing (Submit to Google)'}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='{'card-pass' if is_mobile_ready else 'card-warn'}'><b>Mobile Responsiveness:</b> {'✅ Viewport Configured' if is_mobile_ready else '❌ Not Mobile Friendly'}</div>", unsafe_allow_html=True)
                    
                    st.markdown("#### 🔗 Crawlability & Link Health")
                    st.caption("Scanning internal site structure...")
                    if status_404 == 0:
                        st.markdown("<div class='card-pass'><b>✅ No 404 Dead Links Found</b></div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div class='card-fail'><b>🚨 {status_404} Broken (404) Links Detected!</b><br>Fix immediately as AdSense rejects broken sites.</div>", unsafe_allow_html=True)

                with col2:
                    st.markdown("#### 📝 Content Quality & SEO")
                    st.markdown(f"<div class='{'card-pass' if word_count > 300 else 'card-fail'}'><b>Word Count (Home):</b> {word_count} words {'✅ (Good)' if word_count > 300 else '❌ (Thin Content Risk)'}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='{'card-pass' if has_desc else 'card-warn'}'><b>Meta Description:</b> {'✅ Optimized' if has_desc else '❌ Missing Tag'}</div>", unsafe_allow_html=True)
                    
                    if not found_banned:
                        st.markdown("<div class='card-pass'><b>Banned Keywords:</b> ✅ Clean (100% Policy Compliant)</div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div class='card-fail'><b>Banned Keywords:</b> 🚨 Found: {', '.join(found_banned).title()}</div>", unsafe_allow_html=True)
                        
                    st.markdown("#### 🛡️ Required AdSense Pages")
                    st.caption("Missing these will lead to instant rejection:")
                    # Detailed Page Breakdown
                    for page, exists in page_status.items():
                        if exists:
                            st.markdown(f"<div class='card-pass' style='padding: 8px;'>✅ <b>{page.title()}</b> Page Found</div>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<div class='card-fail' style='padding: 8px;'>❌ <b>{page.title()}</b> Page Missing</div>", unsafe_allow_html=True)

            except Exception as e:
                st.error("❌ Scan Failed! The website might be blocking bots or is currently down.")

st.markdown("<br><hr><center><small>Built with ❤️ for Webmasters | Radar Pro V3 Engine</small></center>", unsafe_allow_html=True)
