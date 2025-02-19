import sqlite3
import pandas as pd
import re
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
plt.rcParams['font.sans-serif'] = ['SimHei']
database_filename = 'SH_lianjia_rentals_ALL.db'

# 数据预处理：清洗价格字段
def process_price(price_str):
    """处理价格字段中的范围值：如果是范围值如'6615-7020'则取平均值；否则直接转为float型"""
    if pd.isna(price_str):  #如果数据为缺失值则返回None
        return None
    price_str = price_str.replace("元/月", "").strip()
    # 分开处理范围值和固定值
    if "-" in price_str:
        try:
            low, high = price_str.split("-")
            return (float(low) + float(high)) / 2  # 取平均值
        except:
            return None  # 无法解析的返回空值
    else:
        try:
            return float(price_str)
        except:
            return None

# 数据预处理：清洗面积字段
def process_area(area_str):
    """处理面积字段中的范围值：如果是范围值如'71.69-72.07㎡'则取平均值；否则直接转为float型"""
    if pd.isna(area_str):  #如果数据为缺失值则返回None
        return None
    area_str = area_str.replace("㎡", "").strip()
    # 分开处理范围值和固定值）
    if "-" in area_str:
        try:
            low, high = area_str.split("-")
            return (float(low) + float(high)) / 2  # 取平均值
        except:
            return None  # 无法解析的返回空值
    else:
        try:
            return float(area_str)
        except:
            return None

# 数据预处理：清洗楼层字段
def process_floor(floor_str):
    """提取楼层数字（如 '高楼层（6层）' 提取数字6）"""
    if pd.isna(floor_str):  #如果数据为缺失值则返回None
        return None
    # 提取括号内的第一个数字
    match = re.search(r'(\d+)', floor_str)
    return int(match.group(1)) if match else None

# 数据可视化：对所有数据统计分析挖掘其中关联，并进行可视化展示
def data_visualize(df):
    df['price_per_area'] = df['price'] / df['area']

    # 统计品牌出现的频率，以词云图形式显示
    brand_counts = df['brand'].value_counts()
    # 生成词云
    wordcloud = WordCloud(font_path='simhei.ttf',  # 支持中文的字体文件路径
                          width=800, height=400, background_color='white').generate_from_frequencies(brand_counts)
    # 显示词云
    plt.figure(figsize=(8, 4))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title('品牌词云分析')
    plt.savefig('./image/brand_wordcloud.png', dpi=150)  # 设置文件名和分辨率（dpi）
    plt.show()

    # 统计各区域的房源数量
    region_counts = df['region'].value_counts()
    # 绘制饼状图
    plt.figure(figsize=(6, 6))
    plt.pie(region_counts, labels=region_counts.index, autopct=lambda p: '{:.0f}'.format(p * sum(region_counts) / 100),
            startangle=140)
    plt.title('房屋数量按区域分布')
    plt.savefig('./image/region_counts.png', dpi=150)  # 设置文件名和分辨率（dpi）
    plt.show()

    # 统计租金价格按区间分布
    bins = [0, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000, float('inf')]
    labels = ['0-1000', '1000-2000', '2000-3000', '3000-4000', '4000-5000',
              '5000-6000', '6000-7000', '7000-8000', '8000-9000', '9000-10000', '10000+']
    # 将价格划分为区间
    df['price_range'] = pd.cut(df['price'], bins=bins, labels=labels, right=False)
    # 统计每个区间的房源数量
    price_distribution = df['price_range'].value_counts().sort_index()
    # 绘制柱状图
    plt.figure(figsize=(12, 6))
    sns.barplot(x=price_distribution.index, y=price_distribution.values, palette='viridis')
    plt.title('价格区间分布')
    plt.xlabel('价格区间 (元/月)')
    plt.ylabel('房源数量')
    plt.xticks(rotation=45)
    plt.savefig('./image/price_distribution.png', dpi=300)
    plt.show()

    # 统计前50个租金最低的房源
    top_50 = df.sort_values(by='price').head(50)
    # 绘制条形图
    plt.figure(figsize=(12, 8))
    sns.barplot(data=top_50, x='price', y='name', palette='viridis')
    plt.title('租金最低的前50个房源')
    plt.xlabel('租金 (元)')
    plt.ylabel('房源名称')
    plt.savefig('./image/price_top50.png', dpi=300)
    plt.show()

    # 统计前50个单位租金最低的房源
    df['price_per_area'] = df['price'] / df['area']
    # 按性价比排序，取前50个
    top_50 = df.sort_values(by='price_per_area').head(50)
    # 绘制条形图
    plt.figure(figsize=(12, 8))
    sns.barplot(data=top_50, x='price_per_area', y='name', palette='viridis')
    plt.title('单位租金最低的前50个房源')
    plt.xlabel('单位租金 (元/㎡)')
    plt.ylabel('房源名称')
    plt.savefig('./image/price_per_area_top50.png', dpi=300)
    plt.show()

    # 绘制箱线图，统计不同区域租金比较
    plt.figure(figsize=(12, 6))
    sns.boxplot(data=df, x='region', y='price', order=df['region'].value_counts().index)
    plt.title('不同区域的租金比较')
    plt.xlabel('区域')
    plt.ylabel('租金 (元/㎡)')
    plt.xticks(rotation=45)
    plt.savefig('./image/region_price.png', dpi=300)
    plt.show()

    # 绘制箱线图，统计不同区域单位租金比较
    plt.figure(figsize=(12, 6))
    sns.boxplot(data=df, x='region', y='price_per_area', order=df['region'].value_counts().index)
    plt.title('不同区域的单位租金比较')
    plt.xlabel('区域')
    plt.ylabel('单位租金 (元/㎡)')
    plt.xticks(rotation=45)
    plt.savefig('./image/region_price_per_area.png', dpi=300)
    plt.show()

    # 绘制散点图，统计面积与价格的关系
    plt.figure(figsize=(12, 6))
    sns.scatterplot(data=df, x='area', y='price', hue='region')
    plt.xlabel('面积 (㎡)')
    plt.ylabel('价格 (元/月)')
    plt.title('面积与价格的关系')
    plt.savefig('./image/area_price.png', dpi=300)
    plt.show()

    # 楼层分布
    df['floor'] = df['floor'].fillna(0).astype(int)
    plt.figure(figsize=(12, 6))
    sns.countplot(data=df, x='floor')
    plt.title('不同楼层的房源数量')
    plt.xticks(rotation=0)
    plt.gca().set_xticklabels([int(x) for x in plt.gca().get_xticks()])  # 强制横坐标为整数
    plt.savefig('./image/floor_count.png', dpi=300)
    plt.show()

    # 绘制箱线图，统计楼层对租金的影响
    plt.figure(figsize=(12, 6))
    sns.boxplot(data=df, x='floor', y='price_per_area', palette='viridis')
    plt.title('楼层对单位租金的影响')
    plt.xlabel('楼层')
    plt.ylabel('单位租金 (元/月)')
    plt.savefig('./image/floor_price.png', dpi=300)
    plt.show()

    # 绘制箱线图
    plt.figure(figsize=(12, 6))
    sns.boxplot(data=df, x='lease_type', y='price_per_area', order=df['lease_type'].value_counts().index)
    plt.title('租赁类型对单位租金的影响')
    plt.xlabel('租赁类型')
    plt.ylabel('单位租金 (元/㎡)')
    plt.xticks(rotation=45)
    plt.savefig('./image/leasetype_price.png', dpi=300)
    plt.show()

    # 统计朝向分布
    plt.figure(figsize=(12, 6))
    sns.countplot(data=df, x='orientation')
    plt.title('不同朝向的房源数量')
    plt.savefig('./image/orientation_count.png', dpi=300)
    plt.show()

    # 绘制箱线图
    plt.figure(figsize=(12, 6))
    sns.boxplot(data=df, x='orientation', y='price_per_area', order=df['orientation'].value_counts().index)
    plt.title('朝向对单位租金的影响')
    plt.xlabel('朝向')
    plt.ylabel('单位租金 (元/㎡)')
    plt.xticks(rotation=45)
    plt.savefig('./image/orientation_price.png', dpi=300)
    plt.show()

    # 绘制箱线图，统计交通便利性对租金的影响
    plt.figure(figsize=(12, 6))
    sns.boxplot(data=df, x='transportation', y='price_per_area', order=df['transportation'].value_counts().index)
    plt.title('交通便利性对单位租金的影响')
    plt.xlabel('交通便利性')
    plt.ylabel('单位租金 (元/月)')
    plt.xticks(rotation=45)
    plt.savefig('./image/transportation_price.png', dpi=300)
    plt.show()

    # 绘制箱线图，统计装修情况对租金性价比的影响
    plt.figure(figsize=(12, 6))
    sns.boxplot(data=df, x='decoration', y='price_per_area', order=df['decoration'].value_counts().index)
    plt.title('装修情况对单位租金的影响')
    plt.xlabel('装修情况')
    plt.ylabel('单位租金 (元/㎡)')
    plt.xticks(rotation=45)
    plt.savefig('./image/decoration_price.png', dpi=300)
    plt.show()

    # 计算每个区域和装修情况的平均租金性价比
    heatmap_data = df.groupby(['region', 'decoration'])['price'].mean().unstack()
    # 绘制热力图
    plt.figure(figsize=(12, 8))
    sns.heatmap(heatmap_data, annot=True, fmt=".1f", cmap='viridis')
    plt.title('不同区域和装修情况的租金性价比热力图')
    plt.xlabel('装修情况')
    plt.ylabel('区域')
    plt.savefig('./image/region_decoration_price.png', dpi=300)
    plt.show()

    # 计算每个品牌的平均租金
    brand_avg_price = df.groupby('brand')['price'].mean().sort_values(ascending=False)
    plt.figure(figsize=(12, 8))
    sns.barplot(x=brand_avg_price.values, y=brand_avg_price.index, palette='viridis', orient='h')
    plt.title('不同品牌的平均租金')
    plt.xlabel('平均租金 (元/月)')
    plt.ylabel('品牌')
    plt.savefig('./image/brand_average_price.png', dpi=300)
    plt.show()

    # 绘制箱线图，统计不同品牌的租金比较
    plt.figure(figsize=(12, 6))
    sns.boxplot(data=df, x='brand', y='price')
    plt.title('不同品牌的租金')
    plt.xlabel('品牌')
    plt.ylabel('租金 (元/月)')
    plt.xticks(rotation=90)
    plt.savefig('./image/brand_price_distribution.png', dpi=300)
    plt.show()


# 主函数
def main():
    # 连接数据库
    conn = sqlite3.connect(database_filename)
    query = "SELECT * FROM rentals"
    df = pd.read_sql_query(query, conn)
    # 数据处理：对price/area/floor/region进行数据处理，应用清洗函数
    df["price"] = df["price"].apply(process_price)
    df["area"] = df["area"].apply(process_area)
    df["floor"] = df["floor"].apply(process_floor)
    df['region'] = df['location'].apply(lambda x: x.split('-')[0] if '-' in x else None)
    # 删除无法解析价格或面积的无效行
    df = df.dropna(subset=["price", "area"])
    # 数据可视化：对所有数据统计分析挖掘其中关联，并进行可视化展示
    data_visualize(df)

if __name__ == '__main__':
    main()