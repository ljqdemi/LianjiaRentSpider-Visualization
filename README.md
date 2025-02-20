# LianjiaRentSpider-Visualization
Implement a crawler for Lianjia rental website and perform data analysis and visualization

本系统包含两个主要模块：

(1) LianjiaRentSpider.py：负责从链家网爬取上海地区的租房信息，并将数据存储到SQLite数据库中。

(2) Data_Visualization.py：从数据库读取数据，进行数据预处理，并通过可视化图表展示分析结果。



运行结果说明：

（1）SH_lianjia_rentals_ALL.db：数据库文件，由运行LianjiaRentSpider.py生成，存储了链家网上海租房的上千条房源信息。

（2）image文件夹：由运行Data_Visualization.py生成，存储了对SH_lianjia_rentals_ALL.db中全部租房数据进行可视化分析的展示结果。
