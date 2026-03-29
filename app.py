import streamlit as st
import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin, urlparse

# --- PAGE SETUP (Wide Layout for Premium Look) ---
st.set_page_config(page_title="Radar Pro - SEO & AdSense Auditor", layout="wide")

# Custom CSS for Modern Clean Look
st.markdown("""
    <style>
    .big-font {font-size:20px !important; font-weight: bold;}
    .metric-box {background-color: #f8f9fa; padding: 15px; border-radius: 10px; border: 1px solid #e9ecef;}
    </style>
""", unsafe_allow_html=True)

st.title("🚀 Radar Pro: Advanced Site Auditor")
st.markdown("<p class='big-font'>Apni website ka in-depth SEO aur AdSense health check karein.</p>", unsafe_allow_html=True)

url_input = st.text_input("Enter Website URL (e.g., https://projobalert.com):", placeholder="https://example.com")

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
}

def check_url_status(link):
    try:
        res = requests.head(link, headers=HEADERS, timeout=5, allow_redirects=False)
        return res.status_code
    except:
        return 0

def check_file_exists(base_url, filename):
    try:
        url = urljoin(base_url, filename)
        res = requests.head(url, headers=HEADERS, timeout=3)
        return res.status_code == 200
    except:
        return False

if st.button("Start Premium Scan", type="primary"):
    if not url_input.startswith("http"):
        st.error("⚠️ URL ke aage 'https://' lagana zaroori hai!")
    else:
        with st.spinner("Analyzing site structure, SEO, and AdSense readiness..."):
            start_time = time.time()
            score = 100 # Starting Score
            
            try:
                # 1. Main Page Fetch
                main_response = requests.get(url_input, headers=HEADERS, timeout=10)
                load_time = round(time.time() - start_time, 2)
                soup = BeautifulSoup(main_response.text, 'html.parser')
                page_text = soup.get_text().lower()
                
                # --- NEW CHECKS ---
                # Technical
                has_ssl = url_input.startswith("https")
                has_robots = check_file_exists(url_input, "robots.txt")
                has_sitemap = check_file_exists(url_input, "sitemap.xml")
                
                # SEO & Content
                word_count = len(page_text.split())
                has_title = soup.title is not None
                meta_desc = soup.find("meta", {"name": "description"})
                has_desc = meta_desc is not None
                viewport = soup.find("meta", {"name": "viewport"})
                is_mobile_ready = viewport is not None
                
                images = soup.find_all('img')
                total_images = len(images)
                images_with_alt = sum(1 for img in images if img.get('alt'))
                
                if not has_ssl: score -= 20
                if load_time > 3.0: score -= 5
                if not has_robots: score -= 5
                if not has_sitemap: score -= 10
                if word_count < 300: score -= 15
                if not has_desc: score -= 10
                
                # AdSense Policy & Links
                status_302, status_404 = 0, 0
                essential_pages_found = 0
                banned_keywords_found = 0
                
                banned_list = ["hack", "cracked", "mod apk", "adult", "casino"] # Removed 'download'
                essential_list = ["privacy", "contact", "about", "disclaimer", "terms"]
                
                for word in banned_list:
                    if word in page_text:
                        banned_keywords_found += 1
                        score -= 10
                        
                links = soup.find_all('a', href=True)
                urls_to_check = []
                
                for a in links:
                    href = a['href']
                    full_url = urljoin(url_input, href)
                    for ep in essential_list:
                        if ep in href.lower():
                            essential_pages_found += 1
                    
                    if urlparse(full_url).netloc == urlparse(url_input).netloc:
                        if full_url not in urls_to_check:
                            urls_to_check.append(full_url)
                            
                if essential_pages_found < 3: score -= 15
                
                # Scan internal links (Max 20)
                scan_limit = min(20, len(urls_to_check))
                for i in range(scan_limit):
                    code = check_url_status(urls_to_check[i])
                    if code in [301, 302, 307]:
                        status_302 += 1
                    elif code == 404:
                        status_404 += 1
                    time.sleep(0.2)
                
                if status_404 > 0: score -= (status_404 * 5)
                score = max(0, score) # Score negative na ho
                
                # --- MODERN UI DASHBOARD ---
                st.success(f"Audit Completed in {load_time}s")
                
                # Main Score
                st.markdown(f"### 🎯 AdSense Readiness Score: {score}%")
                st.progress(score / 100)
                if score >= 80:
                    st.info("Great job! Your site looks ready for AdSense.")
                elif score >= 50:
                    st.warning("Needs some improvement before applying for AdSense.")
                else:
                    st.error("Critical issues found. Fix them before applying.")
                
                st.divider()
                
                # Expandable Sections (WordPress Style)
                col1, col2 = st.columns(2)
                
                with col1:
                    with st.expander("⚙️ Technical & Domain Health", expanded=True):
                        st.write(f"**SSL Certificate:** {'✅ Secure (HTTPS)' if has_ssl else '❌ Missing'}")
                        st.write(f"**Server Latency:** {'✅ ' + str(load_time) + 's' if load_time < 2 else '⚠️ ' + str(load_time) + 's (Slow)'}")
                        st.write(f"**Robots.txt:** {'✅ Found' if has_robots else '❌ Missing'}")
                        st.write(f"**Sitemap.xml:** {'✅ Found' if has_sitemap else '❌ Missing'}")
                        st.write(f"**Mobile Ready (Viewport):** {'✅ Yes' if is_mobile_ready else '❌ No'}")

                    with st.expander("📝 Content & On-Page SEO", expanded=True):
                        st.write(f"**Word Count (Home):** {'✅ ' + str(word_count) + ' words' if word_count > 300 else '⚠️ ' + str(word_count) + ' words (Thin Content)'}")
                        st.write(f"**Title Tag:** {'✅ Found' if has_title else '❌ Missing'}")
                        st.write(f"**Meta Description:** {'✅ Found' if has_desc else '❌ Missing'}")
                        if total_images > 0:
                            st.write(f"**Image Alt Tags:** {images_with_alt}/{total_images} Optimized")
                        else:
                            st.write("**Images:** No images found to scan.")

                with col2:
                    with st.expander("🔗 Redirection & Broken Links", expanded=True):
                        st.write("*(Scanning top 20 internal URLs)*")
                        if status_302 == 0 and status_404 == 0:
                            st.success("✅ No Broken Links or Redirect Issues Found!")
                        else:
                            st.metric("⚠️ 302/301 Redirects", status_302)
                            st.metric("🚨 404 Broken Links", status_404)
                            if status_404 > 0:
                                st.caption("Fix 404 errors immediately, they harm SEO.")

                    with st.expander("🛡️ AdSense Policy Checks", expanded=True):
                        if essential_pages_found >= 3:
                            st.write("**Essential Pages:** ✅ Mostly Found (Privacy, Contact, etc.)")
                        else:
                            st.write("**Essential Pages:** ❌ Missing required pages.")
                            
                        if banned_keywords_found == 0:
                            st.write("**Banned Content:** ✅ Clean (No restricted words)")
                        else:
                            st.write(f"**Banned Content:** 🚨 Found {banned_keywords_found} restricted words!")

            except Exception as e:
                st.error("❌ Website scan nahi ho payi. Details: Check if URL is correct and accessible.")
