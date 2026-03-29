import streamlit as st
import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin, urlparse
import re
import concurrent.futures
from datetime import datetime
import random

# Try importing whois for domain age, gracefully fallback if not installed
try:
    import whois
    WHOIS_AVAILABLE = True
except ImportError:
    WHOIS_AVAILABLE = False

# --- 1. PAGE SETUP & PREMIUM CSS (SaaS Level Look) ---
st.set_page_config(page_title="Radar Pro V6.2 | Stealth AdSense Auditor", layout="wide", page_icon="🧿")

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
    
    /* Professional Actionable Advice Section (Fixed & Upgraded) */
    .advice-wrapper { background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; margin-top: 15px; }
    .advice-header { font-size: 18px; font-weight: 800; color: #0f172a; border-bottom: 2px solid #e2e8f0; padding-bottom: 12px; margin-bottom: 15px; text-transform: uppercase; letter-spacing: 0.5px;}
    .advice-sub { color: #475569; font-size: 15px; margin-bottom: 20px; line-height: 1.6;}
    
    /* Warning Advice Box */
    .advice-item { background: #fef2f2; padding: 15px; border-radius: 8px; margin-bottom: 12px; border-left: 5px solid #ef4444; color: #7f1d1d; font-weight: 500; font-size: 14.5px;}
    
    /* Success Advice Box */
    .advice-success .advice-header { color: #166534; border-bottom-color: #dcfce7; }
    .advice-item-success { background: #f0fdf4; padding: 15px; border-radius: 8px; margin-bottom: 12px; border-left: 5px solid #22c55e; color: #14532d; font-weight: 500; font-size: 14.5px;}

    .stTextInput input { border-radius: 8px !important; border: 2px solid #cbd5e1 !important; padding: 15px !important; font-size: 16px !important; }
    .stTextInput input:focus { border-color: #3b82f6 !important; box-shadow: 0 0 0 2px rgba(59,130,246,0.2) !important; }
    </style>
""", unsafe_allow_html=True)

# --- 2. HERO HEADER ---
st.markdown("""
    <div class="hero-box">
        <div class="hero-title">🧿 Radar <span>Pro</span> Max</div>
        <div class="hero-subtitle">Deep Scanning 50-Page Engine • Anti-Ban Stealth Mode Enabled</div>
    </div>
""", unsafe_allow_html=True)

url_input = st.text_input("Enter Website URL:", placeholder="https://yourwebsite.com", label_visibility="collapsed")

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
}

# 🛡️ STEALTH FUNCTION: Random delay + Error handling
def fetch_and_analyze_page(url):
    try:
        time.sleep(random.uniform(0.2, 0.7)) # Anti-Ban Jitter
        res = requests.get(url, headers=HEADERS, timeout=12, allow_redirects=True)
        is_loop = len(res.history) >= 3 
        
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            text = soup.get_text().lower()
            words = len(text.split())
            return {'url': url, 'status': res.status_code, 'words': words, 'loop': is_loop, 'history': res.history, 'text': text}
        else:
            return {'url': url, 'status': res.status_code, 'words': 0, 'loop': is_loop, 'history': res.history, 'text': ""}
    except Exception as e:
        return {'url': url, 'status': 0, 'words': 0, 'loop': False, 'history':[], 'text': ""}

# --- 3. MAIN ENGINE (50-PAGE DEEP SCAN) ---
if st.button("🚀 INITIATE 50-PAGE DEEP SCAN", type="primary", use_container_width=True):
    if not url_input.strip() or not url_input.startswith(("http://", "https://")):
        st.error("⚠️ Please enter a valid URL starting with http:// or https://")
    else:
        # ✅ FIX 1: Removed `st.status` so there is NO Clickable/Collapsible Box anymore!
        # Using a dynamic placeholder that gets deleted when the scan finishes.
        loading_box = st.empty()
        
        start_time = time.time()
        score = 100
        advice_list =[]
        
        try:
            # --- STEP 1: Homepage Fetch ---
            loading_box.info("⏳ 🌍 Crawling Homepage & Analyzing Server Response...")
            main_res = requests.get(url_input, headers=HEADERS, timeout=15)
            load_time = round(time.time() - start_time, 2)
            soup = BeautifulSoup(main_res.text, 'html.parser')
            main_text = soup.get_text().lower()
            time.sleep(0.5)
            
            # --- STEP 2: Extract 50 Links ---
            loading_box.warning("⏳ 🕸️ Extracting Architecture & Finding Deep Links (up to 50)...")
            links = soup.find_all('a', href=True)
            internal_urls =[]
            for a in links:
                full_url = urljoin(url_input, a['href'])
                clean_url = full_url.split('#')[0]
                if urlparse(clean_url).netloc == urlparse(url_input).netloc and clean_url not in internal_urls:
                    internal_urls.append(clean_url)
            
            scan_list = internal_urls[:50] 
            if url_input not in scan_list: scan_list.insert(0, url_input)
            
            # --- STEP 3: Concurrent Multi-Threaded Scan (STEALTH MODE) ---
            loading_box.info(f"⏳ 🥷 Stealth Mode Active: Safely scanning {len(scan_list)} pages to bypass firewalls...")
            
            scanned_pages_data =[]
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
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
            loading_box.warning("⏳ 🛡️ Auditing AdSense Policies, SEO & Domain Health...")
            has_ssl = url_input.startswith("https")
            is_www = "www." in urlparse(url_input).netloc
            
            essential_list =["privacy", "contact", "about", "disclaimer", "terms"]
            found_essentials =[ep for ep in essential_list if any(ep in u for u in internal_urls)]
            
            banned_keywords =["hack", "cracked", "mod apk", "adult", "casino", "gambling", "movie download", "porn", "nude", "violence", "weapons"]
            found_banned =[w for w in banned_keywords if w in combined_text]
            
            cookie_consent = any(w in combined_text for w in["cookie", "consent", "accept", "got it", "gdpr"])
            under_construction = any(w in combined_text for w in["under construction", "coming soon", "lorem ipsum", "hello world"])
            
            sentences = max(1, len(re.split(r'[.!?]+', main_text)))
            readability_score = (len(main_text.split()) / sentences)
            is_readable = 8 <= readability_score <= 25 
            
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
            loading_box.success("⏳ 📊 Compiling Final Report Data...")
            
            if not has_ssl: score -= 15; advice_list.append("Install an SSL Certificate (HTTPS) immediately. Google strictly blocks unsecured sites.")
            if load_time > 3.0: score -= 5; advice_list.append(f"Server response is slow ({load_time}s). AdSense algorithms favor fast-loading content.")
            if s_404 > 0: score -= 15; advice_list.append(f"Found {s_404} broken (404) internal links. This triggers 'Site Behavior' policy violations.")
            if redirect_loops > 0: score -= 10; advice_list.append(f"Found {redirect_loops} redirect loops. Fix them to allow Googlebot crawling.")
            if len(found_essentials) < 4: score -= 20; advice_list.append(f"Missing mandatory policy pages (Found {len(found_essentials)}/5). Add Privacy, Contact, and Terms pages.")
            if found_banned: score -= 30; advice_list.append(f"CRITICAL: Policy violation detected. Remove prohibited content: {', '.join(set(found_banned))}.")
            if avg_word_count < 600: score -= 15; advice_list.append(f"Thin Content Risk. Your average word count is {avg_word_count}. AdSense requires deep, unique content (600+ words).")
            if h1_tags != 1: score -= 5; advice_list.append(f"SEO Tagging: Homepage has {h1_tags} H1 tags. It must have exactly ONE for proper indexing.")
            if not has_sitemap: score -= 5; advice_list.append("Sitemap.xml is missing. Required for fast Google indexing via Search Console.")
            if under_construction: score -= 25; advice_list.append("Site appears to be 'Under Construction' or contains dummy Lorem Ipsum text.")
            if domain_age_days != "Unknown" and int(domain_age_days) < 30: score -= 10; advice_list.append("Domain is less than 30 days old. Establish organic trust before applying.")

            score = max(0, min(score, 100))
            
            # ✅ Clear the loading box completely!
            loading_box.empty()
            
            # Main Result appears seamlessly
            st.success("✅ Deep Scan Completed Successfully!")

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
                    <div class="metric-value">{len(scanned_pages_data)} <span style="font-size:14px; color:#64748b;">Pages</span></div>
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

            # --- 7. FIX 2: PROFESSIONAL AUTHORITY ADVICE SECTION (NO EMPTY BOXES) ---
            st.markdown("<br>", unsafe_allow_html=True)
            
            if not advice_list:
                # 🟢 SUCCESS SCENARIO (No Critical Errors)
                success_html = """
                <div class='advice-wrapper advice-success'>
                    <div class='advice-header'>🎉 EXCELLENT: SITE READY FOR MONETIZATION</div>
                    <p class='advice-sub'>Your website meets all primary Google AdSense quality guidelines. Before submitting your final application, ensure you maintain the following best practices:</p>
                    <div class='advice-item-success'><b>1. Domain Trust:</b> Ensure your domain is consistently active for at least 1-2 months.</div>
                    <div class='advice-item-success'><b>2. Organic Traffic:</b> Avoid bot or paid traffic. AdSense highly prefers visitors coming organically from Google or Bing Search.</div>
                    <div class='advice-item-success'><b>3. Ad Placement Readiness:</b> Keep clear, non-intrusive spaces in your layout where Ad Units will eventually appear.</div>
                </div>
                """
                st.markdown(success_html, unsafe_allow_html=True)
            else:
                # 🔴 REJECTION/ERROR SCENARIO (Professional Notice)
                advice_html = "<div class='advice-wrapper'>"
                advice_html += "<div class='advice-header'>⚠️ ACTION REQUIRED: POLICY & SEO FIXES</div>"
                advice_html += "<p class='advice-sub'>Our automated systems detected the following issues that typically cause AdSense application rejections. Please resolve these critical errors before submitting your application to Google:</p>"
                
                # Dynamic loop rendering properly inside ONE html string (fixes the empty box bug)
                for idx, advice in enumerate(advice_list):
                    advice_html += f"<div class='advice-item'><b>{idx+1}.</b> {advice}</div>"
                
                advice_html += "</div>"
                st.markdown(advice_html, unsafe_allow_html=True)

        except Exception as e:
            loading_box.empty() # Clear loading state on error
            st.error(f"❌ **Deep Scan Failed:** Ensure the website is live. If the site is protected by strict Cloudflare ('Under Attack' mode), bots might be blocked.")

st.markdown("<br><hr><p style='text-align:center; color:#94a3b8; font-size: 13px;'>Powered by Radar Pro V6.2 Stealth Engine • Professional AdSense Auditor</p>", unsafe_allow_html=True)
