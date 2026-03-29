import streamlit as st
import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin, urlparse

st.set_page_config(page_title="Radar Pro - AdSense Auditor", layout="centered")

st.title("🚀 Radar Pro: Site Auditor")
st.write("Apni website ka safe aur fast scan karein (Numbers Only Dashboard)")

url_input = st.text_input("Enter Website URL (e.g., https://projobalert.com):")

# Safe Headers taaki bot samajh kar block na ho
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
}

def check_url_status(link):
    try:
        res = requests.head(link, headers=HEADERS, timeout=5, allow_redirects=False)
        return res.status_code
    except:
        return 0

if st.button("Start Safe Scan"):
    if not url_input.startswith("http"):
        st.error("URL ke aage 'https://' lagana zaroori hai!")
    else:
        with st.spinner("Stealth Mode on... Scanning fast and safe..."):
            start_time = time.time()
            
            # Counting Variables
            status_200 = 0
            status_302 = 0
            status_404 = 0
            
            essential_pages_found = 0
            banned_keywords_found = 0
            
            banned_list = ["download", "hack", "cracked", "mod apk", "adult", "casino"]
            essential_list = ["privacy", "contact", "about", "disclaimer", "terms"]
            
            try:
                # Page Fetch
                main_response = requests.get(url_input, headers=HEADERS, timeout=10)
                load_time = round(time.time() - start_time, 2)
                soup = BeautifulSoup(main_response.text, 'html.parser')
                page_text = soup.get_text().lower()
                
                is_ssl = "Active ✅" if url_input.startswith("https") else "Missing ❌"
                
                # Banned Keywords Check
                for word in banned_list:
                    if word in page_text:
                        banned_keywords_found += 1
                        
                # Links Check (Max 20 for safety & speed)
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
                            
                scan_limit = min(20, len(urls_to_check))
                for i in range(scan_limit):
                    code = check_url_status(urls_to_check[i])
                    if code == 200:
                        status_200 += 1
                    elif code in [301, 302, 307]:
                        status_302 += 1
                    elif code == 404:
                        status_404 += 1
                    time.sleep(0.3) # Safe delay
                
                # UI Result Dashboard
                st.success(f"Scan Complete in {load_time} seconds!")
                
                st.subheader("📊 Basic Health")
                col1, col2, col3 = st.columns(3)
                col1.metric("SSL Status", is_ssl)
                col2.metric("Latency", f"{load_time}s")
                col3.metric("Banned Words", f"{banned_keywords_found} Found")
                
                st.divider()
                
                st.subheader("🔗 Links & Redirects (Top 20 Sample)")
                e_col1, e_col2, e_col3 = st.columns(3)
                e_col1.metric("✅ 200 OK", status_200)
                e_col2.metric("⚠️ 302/301 Redirects", status_302)
                e_col3.metric("🚨 404 Broken", status_404)
                
                st.divider()
                
                st.subheader("🛡️ AdSense Policy")
                if essential_pages_found >= 3:
                    st.success("✅ Essential Pages: Mostly Found")
                else:
                    st.warning("⚠️ Essential Pages: Some are Missing")

            except Exception as e:
                st.error("❌ Website scan nahi ho payi. Server ne block kiya ya site down hai.")
