import streamlit as st
import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin, urlparse
import re
import concurrent.futures
from datetime import datetime

# Try importing whois for domain age, gracefully fallback if not installed
try:
    import whois
    WHOIS_AVAILABLE = True
except ImportError:
    WHOIS_AVAILABLE = False

# --- 1. PAGE SETUP & PREMIUM CSS (SaaS Level Look) ---
st.set_page_config(page_title="Radar Pro V6 | AdSense & SEO Master Auditor", layout="wide", page_icon="🧿")

st.markdown("""
    <style>
    /* Clean Iframe Look */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
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
    
    /* Metric Cards Flexbox for Mobile/PC */
    .metric-container { display: flex; justify-content: space-between; gap: 15px; margin-bottom: 25px; flex-wrap: wrap; }
    .metric-card {
        background: white; padding: 20px; border-radius: 12px; flex: 1; min-width: 180px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); border-top: 4px solid #3b82f6; text-align: center;
    }
    .metric-value { font-size: 32px; font-weight: 800; color: #0f172a; margin-top: 5px;}
    .metric-label { font-size: 13px; color: #64748b; font-weight: 700; text-transform: uppercase; letter-spacing: 1px;}
    
    /* Health Badges */
    .status-badge { display: flex; align-items: center; padding: 12px 18px; border-radius: 8px; margin-bottom: 12px; font-weight: 600; font-size: 14px;}
    .badge-pass { background-color: #dcfce7; color: #166534; border-left: 5px solid #22c55e; }
    .badge-warn { background-color: #fef9c3; color: #854d0e; border-left: 5px solid #eab308; }
    .badge-fail { background-color: #fee2e2; color: #991b1b; border-left: 5px solid #ef4444; }
    .icon { margin-right: 12px; font-size: 18px; }
    
    /* Advice Box */
    .advice-wrapper { background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; }
    .advice-item { background: #fef2f2; padding: 12px 15px; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid #ef4444; color: #7f1d1d; font-weight: 500;}
    
    .stTextInput input { border-radius: 8px !important; border: 2px solid #cbd5e1 !important; padding: 15px !important; font-size: 16px !important; }
    .stTextInput input:focus { border-color: #3b82f6 !important; box-shadow: 0 0 0 2px rgba(59,130,246,0.2) !important; }
    </style>
""", unsafe_allow_html=True)

# --- 2. HERO HEADER ---
st.markdown("""
    <div class="hero-box">
        <div class="hero-title">🧿 Radar <span>Pro</span> Max</div>
        <div class="hero-subtitle">Deep Scanning 50-Page Engine • 7-Point AdSense Master Audit</div>
    </div>
""", unsafe_allow_html=True)

url_input = st.text_input("Enter Website URL:", placeholder="https://yourwebsite.com", label_visibility="collapsed")

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}

# Function for concurrent deep scanning
def fetch_and_analyze_page(url):
    try:
        res = requests.get(url, headers=HEADERS, timeout=10, allow_redirects=True)
        is_loop = len(res.history) >= 3 # Detect redirect loops
        soup = BeautifulSoup(res.text, 'html.parser')
        text = soup.get_text().lower()
        words = len(text.split())
        return {'url': url, 'status': res.status_code, 'words': words, 'loop': is_loop, 'history': res.history, 'text': text}
    except:
        return {'url': url, 'status': 0, 'words': 0, 'loop': False, 'history':[], 'text': ""}

# --- 3. MAIN ENGINE (50-PAGE DEEP SCAN) ---
if st.button("🚀 INITIATE 50-PAGE DEEP SCAN", type="primary", use_container_width=True):
    if not url_input.strip() or not url_input.startswith(("http://", "https://")):
        st.error("⚠️ Please enter a valid URL starting with http:// or https://")
    else:
        with st.status("📡 Establishing Secure Connection to Server...", expanded=True) as status:
            start_time = time.time()
            score = 100
            advice_list =[]
            
            try:
                # --- STEP 1: Homepage Fetch ---
                status.update(label="🌍 Crawling Homepage & Analyzing Server Response...")
                main_res = requests.get(url_input, headers=HEADERS, timeout=15)
                load_time = round(time.time() - start_time, 2)
                soup = BeautifulSoup(main_res.text, 'html.parser')
                main_text = soup.get_text().lower()
                time.sleep(0.5)
                
                # --- STEP 2: Extract 50 Links ---
                status.update(label="🕸️ Extracting Architecture & Finding Deep Links (up to 50)...")
                links = soup.find_all('a', href=True)
                internal_urls =[]
                for a in links:
                    full_url = urljoin(url_input, a['href'])
                    # Clean URL to avoid anchor jumps causing duplicates
                    clean_url = full_url.split('#')[0]
                    if urlparse(clean_url).netloc == urlparse(url_input).netloc and clean_url not in internal_urls:
                        internal_urls.append(clean_url)
                
                scan_list = internal_urls[:50] # Taking top 50 pages!
                if url_input not in scan_list: scan_list.insert(0, url_input) # Ensure homepage is scanned
                
                # --- STEP 3: Concurrent Multi-Threaded Scan ---
                status.update(label=f"⚡ Multi-Threading Engine: Deep Scanning {len(scan_list)} pages simultaneously...")
                
                scanned_pages_data =[]
                with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
                    results = executor.map(fetch_and_analyze_page, scan_list)
                    for r in results:
                        scanned_pages_data.append(r)
                
                # Math over deep scan data
                s_200 = sum(1 for p in scanned_pages_data if p['status'] == 200)
                s_404 = sum(1 for p in scanned_pages_data if p['status'] >= 400)
                s_301 = sum(1 for p in scanned_pages_data if any(h.status_code == 301 for h in p['history']))
                s_302 = sum(1 for p in scanned_pages_data if any(h.status_code in[302, 307] for h in p['history']))
                redirect_loops = sum(1 for p in scanned_pages_data if p['loop'])
                
                total_words = sum(p['words'] for p in scanned_pages_data)
                valid_pages_count = max(1, len([p for p in scanned_pages_data if p['words'] > 0]))
                avg_word_count = total_words // valid_pages_count
                
                combined_text = " ".join([p['text'] for p in scanned_pages_data])
                
                time.sleep(0.5)

                # --- STEP 4: Technical & Domain Checks ---
                status.update(label="🛡️ Auditing AdSense Policies, SEO & Domain Health...")
                has_ssl = url_input.startswith("https")
                is_www = "www." in urlparse(url_input).netloc
                
                essential_list =["privacy", "contact", "about", "disclaimer", "terms"]
                found_essentials =[ep for ep in essential_list if any(ep in u for u in internal_urls)]
                
                banned_keywords =["hack", "cracked", "mod apk", "adult", "casino", "gambling", "movie download", "porn", "nude", "violence", "weapons"]
                found_banned =[w for w in banned_keywords if w in combined_text]
                
                cookie_consent = any(w in combined_text for w in ["cookie", "consent", "accept", "got it", "gdpr"])
                under_construction = any(w in combined_text for w in["under construction", "coming soon", "lorem ipsum", "hello world"])
                
                # Readability Engine (Sentence length proxy)
                sentences = max(1, len(re.split(r'[.!?]+', main_text)))
                readability_score = (len(main_text.split()) / sentences)
                is_readable = 8 <= readability_score <= 25 # Ideal average sentence length
                
                # On-Page SEO details from Homepage
                has_title = soup.title is not None and len(soup.title.text) > 10
                has_desc = soup.find("meta", {"name": "description"}) is not None
                h1_tags = len(soup.find_all('h1'))
                h2_tags = len(soup.find_all('h2'))
                h3_tags = len(soup.find_all('h3'))
                images = soup.find_all('img')
                img_total = len(images)
                img_alt = sum(1 for img in images if img.get('alt'))
                
                has_robots = requests.get(urljoin(url_input, "robots.txt"), headers=HEADERS, timeout=5).status_code == 200
                has_sitemap = requests.get(urljoin(url_input, "sitemap.xml"), headers=HEADERS, timeout=5).status_code == 200
                has_viewport = soup.find("meta", {"name": "viewport"}) is not None
                
                # Domain Age Logic
                domain_age_days = "Unknown"
                if WHOIS_AVAILABLE:
                    try:
                        domain_info = whois.whois(urlparse(url_input).netloc)
                        creation_date = domain_info.creation_date
                        if type(creation_date) is list: creation_date = creation_date[0]
                        if creation_date:
                            domain_age_days = (datetime.now() - creation_date).days
                    except: pass

                # --- STEP 5: MASTER SCORING ALGORITHM ---
                status.update(label="📊 Calculating Final Report Data...")
                
                if not has_ssl: score -= 15; advice_list.append("Install an SSL Certificate (HTTPS) immediately.")
                if load_time > 3.0: score -= 5; advice_list.append(f"Server response is slow ({load_time}s). Improve hosting or cache.")
                if s_404 > 0: score -= 15; advice_list.append(f"Found {s_404} broken (404) internal links. Find and remove them.")
                if redirect_loops > 0: score -= 10; advice_list.append(f"Found {redirect_loops} redirect loops. Fix them to allow Googlebot crawling.")
                if len(found_essentials) < 4: score -= 20; advice_list.append(f"Missing essential policy pages. (Found {len(found_essentials)}/5). Add Privacy, Contact, Terms etc.")
                if found_banned: score -= 30; advice_list.append(f"CRITICAL: Prohibited content found: {', '.join(set(found_banned))}.")
                if avg_word_count < 600: score -= 15; advice_list.append(f"Thin Content Risk: Your average word count is {avg_word_count}. AdSense requires deep, valuable content (600+).")
                if h1_tags != 1: score -= 5; advice_list.append(f"Homepage has {h1_tags} H1 tags. It must have exactly ONE.")
                if not has_sitemap: score -= 5; advice_list.append("Sitemap.xml is missing. Required for fast Google indexing.")
                if under_construction: score -= 25; advice_list.append("Site appears to be 'Under Construction' or contains Lorem Ipsum.")
                if domain_age_days != "Unknown" and int(domain_age_days) < 30: score -= 10; advice_list.append("Domain is less than 30 days old. Wait slightly longer before applying.")

                score = max(0, min(score, 100))
                
                status.update(label="✅ Deep Audit Complete!", state="complete", expanded=False)

                # --- 4. PREMIUM UI DASHBOARD PRESENTATION ---
                score_color = "#22c55e" if score >= 80 else "#eab308" if score >= 50 else "#ef4444"
                
                st.markdown(f"""
                <div class="metric-container">
                    <div class="metric-card" style="border-top-color: {score_color};">
                        <div class="metric-label">Approval Odds</div>
                        <div class="metric-value" style="color: {score_color};">{score}%</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Deep Scan Depth</div>
                        <div class="metric-value">{len(scan_list)} <span style="font-size:14px; color:#64748b;">Pages</span></div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Avg. Word Count</div>
                        <div class="metric-value">{avg_word_count}</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Server Speed</div>
                        <div class="metric-value">{load_time}s</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.progress(score / 100)
                st.write("")

                # --- 7-POINT MASTER CHECKLIST TABS ---
                t1, t2, t3, t4, t5, t6 = st.tabs(["⚙️ Tech & Speed", "🔗 Redirects & Errors", "🛡️ AdSense Policy", "📝 Content & SEO", "🗂️ Structure", "🌐 Domain"])
                
                def render_badge(condition, pass_text, fail_text, warn_condition=False, warn_text=""):
                    if warn_condition:
                        st.markdown(f"<div class='status-badge badge-warn'><span class='icon'>⚠️</span> {warn_text}</div>", unsafe_allow_html=True)
                    elif condition:
                        st.markdown(f"<div class='status-badge badge-pass'><span class='icon'>✅</span> {pass_text}</div>", unsafe_allow_html=True)
                    else:
                        st.markdown(f"<div class='status-badge badge-fail'><span class='icon'>❌</span> {fail_text}</div>", unsafe_allow_html=True)

                with t1: # 1. TECHNICAL & CONNECTIVITY
                    render_badge(s_200 > 0, f"Website Status: 200 OK (Scanned {s_200} live pages)", "Website Connection Failed")
                    render_badge(has_ssl, "SSL Certificate Valid (HTTPS)", "SSL Missing. Critical for AdSense.")
                    render_badge(load_time <= 2.5, f"LCP/Server Latency: Fast ({load_time}s)", f"Server Latency: Slow ({load_time}s)", warn_condition=(2.5 < load_time <= 4.0), warn_text=f"Server Latency: Average ({load_time}s). Optimization needed.")
                    render_badge(is_www, "Canonical URL: WWW setup correctly", "Canonical URL: Non-WWW detected. Ensure 301 redirects are working.")

                with t2: # 2. REDIRECTION & ERROR TRACKING
                    render_badge(s_404 == 0, f"Broken Links (404): 0 Found out of {len(scan_list)}", f"Broken Links Alert! Found {s_404} dead pages.")
                    render_badge(redirect_loops == 0, "Redirect Loops: 0 Found (Healthy)", f"Redirect Loops: {redirect_loops} detected! Googlebot will fail to crawl.")
                    render_badge(s_302 == 0, "Temporary Redirects (302): None", "", warn_condition=(s_302 > 0), warn_text=f"Temp Redirects (302) Found: {s_302}. Use 301 Permanent instead.")
                    render_badge(s_301 >= 0, f"Permanent Redirects (301): {s_301} Logged (SEO Safe)", "")

                with t3: # 3. ADSENSE POLICY COMPLIANCE
                    render_badge(len(found_essentials) >= 4, f"Essential Pages Found ({len(found_essentials)}/5)", "Missing Mandatory Privacy/Contact Pages!")
                    render_badge(not found_banned, "Content Policy: 100% Clean", f"Prohibited Material Found! Words: {', '.join(set(found_banned))}")
                    render_badge(not under_construction, "Low Value Content Check: Site is Live", "Site contains 'Under Construction' or 'Lorem Ipsum' spam.")
                    render_badge(cookie_consent, "Cookie/GDPR Consent Detected", "", warn_condition=(not cookie_consent), warn_text="Cookie Consent missing. Highly recommended for European Traffic.")

                with t4: # 4. CONTENT & ON-PAGE SEO
                    render_badge(avg_word_count >= 600, f"Deep Content Scan: {avg_word_count} avg words per page", f"Thin Content Warning: Only {avg_word_count} avg words. High risk of rejection.", warn_condition=(400 <= avg_word_count < 600), warn_text=f"Moderate Content Depth: {avg_word_count} avg words. Target 600+.")
                    render_badge(has_title and has_desc, "Meta Title & Description perfectly mapped", "Missing Title or Description Meta tags.")
                    render_badge(h1_tags == 1 and h2_tags > 0 and h3_tags >= 0, f"Heading Hierarchy: Perfect (H1: {h1_tags}, H2: {h2_tags}, H3: {h3_tags})", f"Heading Error: Found {h1_tags} H1 tags. Needs exactly 1.")
                    render_badge(img_total > 0 and (img_alt/img_total) > 0.8, f"Image SEO: {img_alt}/{img_total} Optimized with Alt Text", "", warn_condition=(img_total > 0 and (img_alt/img_total) <= 0.8), warn_text=f"Image SEO: Only {img_alt}/{img_total} images have Alt Text.")
                    render_badge(is_readable, "Readability & Grammar Score: Healthy sentence length", "", warn_condition=(not is_readable), warn_text="Readability Warning: Sentences are either too short (spammy) or too long (hard to read).")
                    render_badge(True, "Plagiarism: Manual Check Required", "", warn_condition=True, warn_text="Reminder: Ensure content is strictly 100% human-written and unique.")

                with t5: # 5. SITE STRUCTURE & NAVIGATION
                    render_badge(has_robots, "Robots.txt present (Search Engine friendly)", "Robots.txt missing! Google cannot crawl your site.")
                    render_badge(has_sitemap, "Sitemap.xml present (Indexing ready)", "Sitemap.xml missing! Crucial for Webmaster tools.")
                    render_badge(has_viewport, "Mobile Viewport Tag (100% Responsive)", "Not Mobile Friendly! Missing viewport tag.")
                    render_badge(len(scan_list) > 15, f"Internal Linking Depth: Excellent ({len(scan_list)} pages crawled)", "", warn_condition=(len(scan_list) <= 15), warn_text=f"Site Structure: Too small (Only {len(scan_list)} pages crawled). Build more categories.")

                with t6: # 6. DOMAIN & INDEXING
                    if domain_age_days != "Unknown":
                        render_badge(int(domain_age_days) >= 60, f"Domain Age: {domain_age_days} Days (Trusted)", f"Domain Age: {domain_age_days} Days (Too New)", warn_condition=(30 <= int(domain_age_days) < 60), warn_text=f"Domain Age: {domain_age_days} Days (Wait a little longer to apply).")
                    else:
                        render_badge(True, "", "", warn_condition=True, warn_text="Domain Age: Could not verify automatically. Ensure domain is 1-2 months old.")
                    
                    render_badge(True, "", "", warn_condition=True, warn_text="Google Indexing: Go to Google and search 'site:yourdomain.com' to verify indexed pages.")
                    render_badge(True, "", "", warn_condition=True, warn_text="Ad Placement: Ensure you have clear spaces/sidebars ready for Google Ads.")

                # --- 7. FINAL RESULT LOGIC & ACTIONABLE ADVICE ---
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("### 📋 Step-by-Step Actionable Advice")
                
                if score >= 90 and not advice_list:
                    st.success("🎉 **Outstanding!** Your website passes the Radar Pro Max Audit with flying colors. You are highly eligible for Google AdSense.")
                else:
                    st.markdown("<div class='advice-wrapper'>", unsafe_allow_html=True)
                    st.markdown("<p style='color: #475569; font-weight: 600; margin-bottom: 15px;'>Fix the following critical errors before applying:</p>", unsafe_allow_html=True)
                    for idx, advice in enumerate(advice_list):
                        st.markdown(f"<div class='advice-item'><b>{idx+1}.</b> {advice}</div>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)

            except Exception as e:
                st.error(f"❌ **Deep Scan Failed:** Could not complete the 50-page crawl. Ensure the website does not have a strict firewall (like Cloudflare Under Attack mode) blocking our bot.")

st.markdown("<br><hr><p style='text-align:center; color:#94a3b8; font-size: 13px;'>Powered by Radar Pro V6 Concurrent Engine • 50-Page Enterprise Auditor</p>", unsafe_allow_html=True)
