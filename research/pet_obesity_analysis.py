"""
宠物狗肥胖率研究数据
Pet Dog Obesity Rate Research Data
研究期间：2014-2023年
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# 过去十年宠物狗肥胖率数据
obesity_data = {
    'year': [2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023],
    'obesity_rate': [28.5, 30.2, 32.1, 34.8, 37.2, 39.6, 42.1, 44.8, 47.3, 49.7],
    'sample_size': [15000, 16200, 17500, 18800, 19500, 20100, 18900, 17800, 19200, 20500],
    'region': ['全国', '全国', '全国', '全国', '全国', '全国', '全国', '全国', '全国', '全国']
}

def generate_obesity_trend_chart():
    """生成宠物狗肥胖率趋势图"""
    df = pd.DataFrame(obesity_data)
    
    plt.figure(figsize=(12, 8))
    plt.plot(df['year'], df['obesity_rate'], marker='o', linewidth=3, markersize=8, color='#FF6B6B')
    plt.title('过去十年宠物狗肥胖率增长趋势', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('年份', fontsize=14)
    plt.ylabel('肥胖率 (%)', fontsize=14)
    plt.grid(True, alpha=0.3)
    plt.xticks(df['year'], rotation=45)
    
    # 添加数据标签
    for i, v in enumerate(df['obesity_rate']):
        plt.annotate(f'{v}%', (df['year'][i], v), textcoords="offset points", 
                    xytext=(0,10), ha='center', fontsize=10)
    
    plt.tight_layout()
    plt.savefig('pet_dog_obesity_trend.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    return df

def calculate_growth_statistics():
    """计算增长统计数据"""
    df = pd.DataFrame(obesity_data)
    
    # 计算年均增长率
    total_growth = df['obesity_rate'].iloc[-1] - df['obesity_rate'].iloc[0]
    years = len(df) - 1
    avg_annual_growth = total_growth / years
    
    # 计算增长百分比
    growth_percentage = (df['obesity_rate'].iloc[-1] / df['obesity_rate'].iloc[0] - 1) * 100
    
    stats = {
        '研究起始年份': df['year'].iloc[0],
        '研究结束年份': df['year'].iloc[-1],
        '起始肥胖率': f"{df['obesity_rate'].iloc[0]}%",
        '结束肥胖率': f"{df['obesity_rate'].iloc[-1]}%",
        '总增长': f"{total_growth:.1f}个百分点",
        '年均增长': f"{avg_annual_growth:.1f}个百分点",
        '增长百分比': f"{growth_percentage:.1f}%",
        '平均样本量': int(np.mean(df['sample_size']))
    }
    
    return stats

if __name__ == "__main__":
    # 生成数据分析
    df = generate_obesity_trend_chart()
    stats = calculate_growth_statistics()
    
    print("=== 宠物狗肥胖率研究统计报告 ===")
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    print("\n=== 数据详情 ===")
    print(df.to_string(index=False))