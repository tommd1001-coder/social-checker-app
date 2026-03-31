import streamlit as st
import pandas as pd
import time
import requests
import concurrent.futures
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, WebDriverException
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

#Chưa mở xoay(proxy, xoay)
#3
# CẤU HÌNH IPFAKE
PROXY_SERVER = "svhn3.proxyxoay.net:45802"
API_KEY = "974ffcb0-ed69-4723-9297-97c339777092"

st.set_page_config(page_title="SOCIAL FINAL STEALTH", layout="wide")

# 1: CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
    .stApp { background-color: #0d1117; color: #c9d1d9; font-family: 'JetBrains Mono', monospace; }
    .metric-box { background: #161b22; border: 1px solid #30363d; padding: 10px; border-radius: 5px; text-align: center; }
    .metric-val { font-size: 20px; font-weight: bold; }
    .metric-label { font-size: 10px; color: #8b949e; text-transform: uppercase; margin-bottom: 5px; }
    .queue-row { display: grid; grid-template-columns: 40px 2fr 1.5fr 1fr; gap: 15px; padding: 12px 10px; border-bottom: 1px solid #21262d; align-items: center; }
    .bio-badge { padding: 1px 4px; border-radius: 2px; font-weight: bold; font-size: 9px; }
    .bio-ok { background-color: #238636; color: white; }
    .bio-miss { background-color: #da3633; color: white; }
    .bio-na { background-color: #484f58; color: white; }
    </style>
    """, unsafe_allow_html=True)

def rotate_ip():
    api_key = "974ffcb0-ed69-4723-9297-97c339777092"
    url = f"https://proxyxoay.net/api/rotating-proxy/change-key-ip/{api_key}"
    
    try:
        response = requests.get(url, timeout=15)
        data = response.json()
        
        # Kiểm tra status 200 như trong ảnh tài liệu
        if data.get("status") == 200:
            print(f"✅ {data.get('message')}")
            return True
        else:
            # Thường sẽ báo: "Vui lòng đợi X giây để đổi IP tiếp theo"
            print(f"⏳ Thông báo: {data.get('message')}")
            return False
            
    except Exception as e:
        print(f"❌ Lỗi kết nối API: {e}")
        return False
    
#res = rotate_ip()
#print(f"Kết quả xoay IP: {res}")

# 2: LOGIC CHÍNH -----

def check_single_link(line, target_domain, search_bio):
    rotate_ip()
    # Tách dòng input
    parts = line.split(maxsplit=1)
    src = parts[0].strip() if len(parts) > 0 else ""
    # Nếu có phần tử thứ 2 thì lấy làm anchor, không thì để trống
    expected_anchor = parts[1].strip() if len(parts) > 1 else ""

    if not src.startswith("http"):
        src = "https://" + src

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    #options.add_argument(f'--proxy-server={PROXY_SERVER}')
    
    # Random User-Agent để tránh bị nhận diện pattern
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ]
    options.add_argument(f"user-agent={random.choice(user_agents)}")
    
    # Loại bỏ dấu vết WebDriver
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    driver = None
    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        })
        
        driver.set_page_load_timeout(35)
        driver.get(src)

        # Chờ trang tải ổn định (chờ body xuất hiện)
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        

    

#======================================================================================================================
    #Giả click about
        try:
        #Tìm và click vào tab About nếu có
            about_tab = driver.find_element("xpath", "//a[contains(@data-tp-primary, 'about')] | //a[contains(text(), 'About')]")
            driver.execute_script("arguments[0].click();", about_tab)
            time.sleep(3) # Đợi 3 giây để tab hiện ra
        except:
            pass # Nếu không có tab thì bỏ qua

    #Iframe và Cuộn trang
    ## 1. Cuộn trang xuống cuối để kích hoạt load dữ liệu (nếu có)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        # 2. Thử chuyển vào iframe nếu có (Ví dụ iframe của profile)
        iframes = driver.find_elements("tag name", "iframe")
        for iframe in iframes:
            try:
                driver.switch_to.frame(iframe)
                # Chạy thử script quét link trong iframe này (cần sửa logic một chút)
                driver.switch_to.default_content() # Thoát ra để quét tiếp
            except:
                continue
            
#======================================================================================================================




        # 3: JS quét sâu Link và Bio (Đã thêm xử lý KHÔNG DẤU) ---
        domain_clean = target_domain.replace("https://","").replace("http://","").replace("www.","").split('/')[0].lower()
        
        js_scan = f"""
            // Hàm loại bỏ dấu tiếng Việt và các ký tự đặc biệt
            function removeAccents(str) {{
                return str.normalize('NFD')
                          .replace(/[\\u0300-\\u036f]/g, '')
                          .replace(/đ/g, 'd').replace(/Đ/g, 'D');
            }}

            function scan() {{
                let targetDom = `{domain_clean}`;
                let expAnch = `{expected_anchor}`.toLowerCase().trim();
                let bioTxt = `{search_bio}`.toLowerCase().trim();
                let result = {{ status: "NOT_FOUND", actual_anchor: "N/A", found_href: "N/A", bio_found: false }};

                // 1. Kiểm tra Bio (So sánh không dấu)
                let bodyText = document.body.innerText.toLowerCase();
                
                // Chuẩn hóa cả text trên web và text bio nhập vào
                let normalizedBody = removeAccents(bodyText);
                let normalizedBio = removeAccents(bioTxt);
                
                // Kiểm tra xem chuỗi body không dấu có chứa chuỗi bio không dấu hay không
                if (normalizedBio !== "" && normalizedBody.includes(normalizedBio)) {{
                    result.bio_found = true;
                }}

                // 2. Quét Link
                let anchors = document.querySelectorAll('a');
                for (let a of anchors) {{
                    let href = (a.href || "").toLowerCase();
                    let textOriginal = (a.innerText || a.textContent || "").trim();
                    let altOriginal = a.getAttribute('title') || a.getAttribute('aria-label') || "";
                    
                    let text = textOriginal.toLowerCase();
                    let alt = altOriginal.toLowerCase();
                    
                    if (href === "" || href.startsWith("javascript:")) continue;

                    let isDomainMatch = href.includes(targetDom);
                    
                    if (expAnch === "") {{
                        if (isDomainMatch) {{
                            result.status = "VERIFIED";
                            result.found_href = a.href;
                            result.actual_anchor = textOriginal || (altOriginal ? "["+altOriginal+"]" : "Image/Icon");
                            return result; 
                        }}
                    }} else {{
                        let isTextMatch = (text === expAnch);
                        let isAltMatch = (alt === expAnch);
                        
                        // TH1: Domain đúng và Anchor đúng
                        if (isDomainMatch && (isTextMatch || isAltMatch)) {{
                            result.status = "VERIFIED";
                            result.found_href = a.href;
                            result.actual_anchor = isTextMatch ? textOriginal : "[Thuộc tính ẩn: " + altOriginal + "]";
                            return result;
                        }}
                        
                        // TH2: Domain đúng nhưng Anchor sai
                        if (isDomainMatch && !isTextMatch && !isAltMatch) {{
                            if (result.status !== "WRONG_ANCHOR") {{
                                result.status = "WRONG_ANCHOR";
                                result.actual_anchor = textOriginal || (altOriginal ? "["+altOriginal+"]" : "Image/Icon");
                            }}
                        }}
                        
                        // TH3: Anchor text đúng nhưng Domain trỏ đến sai
                        if (!isDomainMatch && (isTextMatch || isAltMatch)) {{
                            if (result.status === "NOT_FOUND") {{
                                result.status = "WRONG_DOMAIN";
                                result.actual_anchor = textOriginal || (altOriginal ? "["+altOriginal+"]" : "Image/Icon");
                            }}
                        }}
                    }}
                }}
                return result;
            }}
            return scan();
        """
        
        data = driver.execute_script(js_scan)
        driver.quit()

        return {
            "src": src, 
            "status": data['status'], 
            "actual_anchor": data['actual_anchor'], 
            "actual_url": data['found_href'], 
            "bio": "CÓ BIO" if data['bio_found'] else "KHÔNG CÓ BIO"
        }

    except Exception as e:
        if driver: driver.quit()
        return {"src": src, "status": "BLOCKED", "actual_anchor": "N/A", "actual_url": str(e), "bio": "N/A"}

# GIAO DIỆN
st.title("SOCIAL CHECKER 4 - DEEP SCAN - NO PROXY")

col_set, col_res = st.columns([1, 2.5])

with col_set:
    st.subheader("INPUT")
    raw_input = st.text_area("Danh sách (URL Anchor):", height=200)
    target_url = st.text_input("Domain Đích:", placeholder="https://domain.com")
    target_bio = st.text_area("Bio cần quét:", height=100)
    num_threads = st.slider("Số luồng đồng thời:", 1, 5, 8)
    batch_size = st.number_input("Xoay IP sau mỗi X link:", value=9)
    start_btn = st.button("▶ BẮT ĐẦU KIỂM TRA")

with col_res:
    metrics_placeholder = st.empty()
    # TÁCH LÀM 2 VÙNG RIÊNG BIỆT
    rotate_status = st.empty()  # Vùng dành riêng cho thông báo xoay IP
    table_area = st.empty()    # Vùng dành riêng cho bảng dữ liệu

    if start_btn and raw_input:
        lines = [l.strip() for l in raw_input.splitlines() if l.strip()]
        total = len(lines)
        results = [None] * total
        
        batches = [lines[i:i + batch_size] for i in range(0, total, batch_size)]
        
        curr_idx = 0
        for b_idx, batch in enumerate(batches):
            # HIỂN THỊ THÔNG BÁO XOAY IP Ở VÙNG RIÊNG
            # rotate_status.info(f"🔄 Đang xoay IP cho đợt {b_idx + 1}...")
            # rotate_ip()
            # time.sleep(8) 
            # rotate_status.empty() # Xóa thông báo sau khi xoay xong, không ảnh hưởng đến bảng bên dưới
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
                futures = {executor.submit(check_single_link, line, target_url, target_bio): curr_idx + i for i, line in enumerate(batch)}
                
                for future in concurrent.futures.as_completed(futures):
                    idx = futures[future]
                    results[idx] = future.result()
                    
                    done_res = [r for r in results if r is not None]
                    c_verified = len([r for r in done_res if r['status'] == "VERIFIED"])
                    c_blocked = len([r for r in done_res if r['status'] == "BLOCKED"])
                    c_notfound = len([r for r in done_res if r['status'] == "NOT_FOUND"])
                    c_wrong_anchor = len([r for r in done_res if r['status'] == "WRONG_ANCHOR"])
                    c_wrong_domain = len([r for r in done_res if r['status'] == "WRONG_DOMAIN"])

                    # Cập nhật Metrics
                    metrics_placeholder.markdown(f"""
                        <div style="display: flex; gap: 8px; margin-bottom: 20px;">
                            <div class="metric-box" style="flex:1; border-top: 3px solid #58a6ff;">
                                <div class="metric-label">Tổng</div><div class="metric-val">{total}</div>
                            </div>
                            <div class="metric-box" style="flex:1; border-top: 3px solid #3fb950;">
                                <div class="metric-label">Verified</div><div class="metric-val">{c_verified}</div>
                            </div>
                            <div class="metric-box" style="flex:1; border-top: 3px solid #ff4b4b;">
                                <div class="metric-label">Bị chặn (IP)</div><div class="metric-val">{c_blocked}</div>
                            </div>
                            <div class="metric-box" style="flex:1; border-top: 3px solid #ff7b72;">
                                <div class="metric-label">Không thấy dữ liệu</div><div class="val">{c_notfound}</div>
                            </div>
                            <div class="metric-box" style="flex:1; border-top: 3px solid #e3b341;">
                                <div class="metric-label">Sai Anchor</div><div class="metric-val">{c_wrong_anchor}</div>
                            </div>
                            <div class="metric-box" style="flex:1; border-top: 3px solid #d29922;">
                                <div class="metric-label">Sai Domain</div><div class="metric-val">{c_wrong_domain}</div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

                    # Cập nhật Bảng danh sách vào table_area
                    html_list = ""
                    for i, res in enumerate(results):
                        if not res: continue
                        stt_map = {
                            "VERIFIED": ("✔ VERIFIED", "#3fb950"),
                            "BLOCKED": ("🚫 BỊ CHẶN (IP/CAP)", "#ff4b4b"),
                            "NOT_FOUND": ("🔍 KHÔNG THẤY DỮ LIỆU", "#ff7b72"),
                            "WRONG_DOMAIN": ("⚠ SAI DOMAIN", "#d29922"),
                            "WRONG_ANCHOR": ("⚠ SAI ANCHOR", "#e3b341")
                        }
                        stt_text, color = stt_map.get(res['status'], ("N/A", "#8b949e"))
                        
                        if res['bio'] == "CÓ BIO": b_cls = "bio-ok"
                        elif res['bio'] == "KHÔNG CÓ BIO": b_cls = "bio-miss"
                        else: b_cls = "bio-na"

                        html_list += f"""
                        <div class='queue-row'>
                            <div style='color:#8b949e'>{i+1}</div>
                            <div style='overflow:hidden; text-overflow:ellipsis; white-space:nowrap;'>
                                <a href='{res['src']}' target='_blank' style='color:#58a6ff; text-decoration:none;' title='{res['src']}'>
                                    {res['src']}
                                </a>
                            </div>
                            <div>
                                <div style='font-size:11px'>Bio: <span class='bio-badge {b_cls}'>{res['bio']}</span></div>
                                <div style='font-size:10px; color:{color}; margin-top:4px;'>Thấy: "{res['actual_anchor']}"</div>
                            </div>
                            <div style='color:{color}; font-weight:bold; font-size:11px'>{stt_text}</div>
                        </div>"""
                    
                    # Đẩy dữ liệu vào vùng bảng, không bị placeholder nào khác ghi đè
                    table_area.markdown(f"<div style='max-height:600px; overflow-y:auto;'>{html_list}</div>", unsafe_allow_html=True)
            
            curr_idx += len(batch)
        st.success("Hoàn tất kiểm tra!")