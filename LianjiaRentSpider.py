import requests
from bs4 import BeautifulSoup
import sqlite3
import time
import sqlite3
database_filename = 'SH_lianjia_rentals_ALL.db'  # 数据库文件名
NULL_INFO = "未知"  # 网页未展示数据填充为"未知"

# 创建数据库
def setup_database():
    conn = sqlite3.connect(database_filename)
    c = conn.cursor()
    c.execute('''
              CREATE TABLE IF NOT EXISTS rentals(
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                title TEXT,
                lease_type TEXT, 
                location TEXT, 
                name TEXT, 
                area TEXT,
                price TEXT, 
                style TEXT, 
                orientation TEXT,
                floor TEXT, 
                decoration TEXT, 
                transportation TEXT, 
                pay_type TEXT, 
                first_rent TEXT, 
                brand TEXT,
                link TEXT
              )
            ''')
    conn.commit()
    return conn

# 获取网页内容
def get_page_content(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # 检查请求是否成功
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve webpage: {url}, error: {e}")
        return None

# 解析单个网页内容
def parse_page_content(html):
    soup = BeautifulSoup(html, 'html.parser')
    rentals = []
    # 查找房源信息
    for item in soup.find_all('div', class_='content__list--item'):
        try:
            # 提取标题
            title = item.find('a', class_='content__list--item--aside').get('title', '').strip()
            # 提取房屋信息
            houseinfo = item.find('p', class_='content__list--item--des').get_text(strip=True)
            lease_type, location,  name, area, orientation, style, floor = parse_houseinfo(title, houseinfo)
            # 提取底部信息
            bottom = item.find('p', class_='content__list--item--bottom').get_text(strip=True)
            decoration_tag = item.find('i', class_='content__item__tag--decoration')
            decoration = decoration_tag.get_text(strip=True) if decoration_tag else NULL_INFO
            transportation_tag = item.find('i', class_='content__item__tag--is_subway_house')
            transportation = transportation_tag.get_text(strip=True) if transportation_tag else NULL_INFO
            pay_type_tag = item.find('i', class_='content__item__tag--deposit_1_pay_1')
            pay_type = pay_type_tag.get_text(strip=True) if pay_type_tag else NULL_INFO
            first_rent_tag = item.find('i', class_='content__item__tag--first_rent')
            first_rent = first_rent_tag.get_text(strip=True) if first_rent_tag else NULL_INFO
            # 提取品牌信息
            brand = item.find('span', class_='brand').get_text(strip=True)
            # 提取价格
            price = item.find('span', class_='content__list--item-price').get_text(strip=True)
            # 提取链接
            link = 'https://sh.lianjia.com' + item.find('a', class_='content__list--item--aside').get('href', '').strip()
            # 添加到列表
            rentals.append((title, lease_type, location, name, area, price, style, orientation, floor, price, decoration, transportation, pay_type, first_rent, brand, link
))
        except AttributeError as e:
            print(f"Error parsing item: {e}")
            continue
    return rentals

# 解析单条房源信息
def parse_houseinfo(title, houseinfo):
    lease_type, location, name, area, orientation, style, floor = NULL_INFO, NULL_INFO, NULL_INFO, NULL_INFO, NULL_INFO, NULL_INFO, NULL_INFO
    title_parts = title.split('·')
    if len(title_parts) >= 2:
        lease_type = title_parts[0].strip()  # 租赁类型
        remaining = '·'.join(title_parts[1:]).strip()
    if lease_type == "独栋":  # 租赁类型为"独栋"
        # 从houseinfo中获取信息
        houseinfo_parts = houseinfo.split('/')
        if len(houseinfo_parts) >= 3:
            style = houseinfo_parts[-1].strip()
            area = houseinfo_parts[-3].strip()
        # 从title中获取额外信息
        remaining_parts = remaining.split()
        if len(remaining_parts) >= 1:
            name = remaining_parts[0].strip()
            location = remaining_parts[1].strip()
            for part in reversed(remaining_parts):
                if "朝南" in part:
                    orientation="南"
                    break
                elif "朝北" in part:
                    orientation = "北"
                    break
    else:  # 租赁类型为"整租"或"合租"
        # 从houseinfo中获取信息
        houseinfo_parts = houseinfo.lstrip("精选/").split('/')
        location = houseinfo_parts[0].strip().split('-')[0] + '-' + houseinfo_parts[0].strip().split('-')[1]
        name = houseinfo_parts[0].strip().split('-')[2]
        area = houseinfo_parts[1].strip()
        orientation = houseinfo_parts[2].strip()
        style = houseinfo_parts[3].strip()
        floor_part = houseinfo_parts[4].strip()
        floor = floor_part.split()[0].strip() + floor_part.split()[1].strip()
    return lease_type, location, name, area, orientation, style, floor

# 保存数据到数据库
def save_to_database(conn, rentals):
    c = conn.cursor()
    c.executemany('INSERT OR IGNORE INTO rentals (title, lease_type, location, name, area, price, style, orientation, floor, price, decoration, transportation, pay_type, first_rent, brand, link) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', rentals)
    conn.commit()
    print(f"Saved {len(rentals)} rentals to database.")


# 主函数
def main():
    base_url = 'https://sh.lianjia.com/zufang/pg'  # 链家租房页面
    conn = setup_database()
    for page in range(1, 50):
        url = f"{base_url}{page}/"
        print(f"Fetching page: {url}")
        html = get_page_content(url)
        if html:
            rentals = parse_page_content(html)
            if rentals:
                save_to_database(conn, rentals)
            else:
                print(f"No rentals found on page {page}.")
        else:
            print(f"Failed to fetch page {page}.")
        # 添加请求间隔，避免触发反爬虫机制
        time.sleep(2)
    conn.close()

if __name__ == '__main__':
    main()
