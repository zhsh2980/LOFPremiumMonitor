
from playwright.sync_api import sync_playwright
import time
import os

def test_qdii_scrape():
    with sync_playwright() as p:
        # 使用已有的登录状态如果存在
        auth_file = "auth_state.json"
        if os.path.exists(auth_file):
            print(f"Loading auth from {auth_file}")
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(storage_state=auth_file)
        else:
            print("No auth file, launching fresh")
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()
            
        page = context.new_page()
        
        # 访问 QDII 页面
        url = "https://www.jisilu.cn/data/qdii/#qdiie"
        print(f"Navigating to {url}")
        page.goto(url)
        
        # 滚动到底部以确保加载
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(3)
        
        # 点击"商品"标签如果需要（通常 #qdiie 是锚点，可能自动切换，但也有可能需要点击）
        # 观察页面结构，可能有一个 tab 点击操作
        # 假设 #topic_qdiie 下面有表格
        
        # 等待表格出现
        try:
            selector = "#flex_qdiic"
            page.wait_for_selector(selector, timeout=10000)
            print(f"Table {selector} found")
        except:
            print(f"Table {selector} not found")
            return

        # 获取表头
        headers = page.locator(f"{selector} th").all_inner_texts()
        print("Headers:", headers)
        
        # 获取第一行数据
        rows = page.locator(f"{selector} tbody tr").all()
        if rows:
            print(f"Found {len(rows)} rows")
            first_row = rows[0]
            cells = first_row.locator("td").all()
            cell_texts = [c.inner_text().strip() for c in cells]
            print("First Row Cells:")
            for i, text in enumerate(cell_texts):
                print(f"{i}: {text}")
                
            # 检查样式
            change_pct_cell = cells[3] # 假设index 3是涨幅
            style = change_pct_cell.evaluate("el => getComputedStyle(el).color")
            print(f"Change Pct Color: {style}")
            
        browser.close()

if __name__ == "__main__":
    test_qdii_scrape()
