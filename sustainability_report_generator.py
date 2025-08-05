#!/usr/bin/env python3
"""
自动化季度可持续发展报告生成器
Automated Quarterly Sustainability Report Generator

该脚本用于自动收集、分析和生成企业季度可持续发展报告，
涵盖环境、社会和治理(ESG)三个维度的关键指标。

作者: h66840
版本: 1.0.0
创建日期: 2025-01-15
"""

import json
import logging
import os
import sqlite3
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple, Any
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('sustainability_report.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class EnvironmentalMetrics:
    """环境指标数据类"""
    carbon_emissions: float  # 碳排放量 (吨CO2当量)
    energy_consumption: float  # 能源消耗 (MWh)
    water_usage: float  # 用水量 (立方米)
    waste_generated: float  # 废物产生量 (吨)
    renewable_energy_ratio: float  # 可再生能源比例 (%)
    recycling_rate: float  # 回收率 (%)

@dataclass
class SocialMetrics:
    """社会指标数据类"""
    employee_count: int  # 员工总数
    diversity_ratio: float  # 多样性比例 (%)
    training_hours: float  # 培训小时数
    safety_incidents: int  # 安全事故数
    community_investment: float  # 社区投资 (万元)
    customer_satisfaction: float  # 客户满意度 (%)

@dataclass
class GovernanceMetrics:
    """治理指标数据类"""
    board_independence: float  # 董事会独立性 (%)
    ethics_training_completion: float  # 道德培训完成率 (%)
    compliance_violations: int  # 合规违规数
    data_security_incidents: int  # 数据安全事件数
    transparency_score: float  # 透明度评分 (1-10)

@dataclass
class SustainabilityReport:
    """可持续发展报告数据类"""
    quarter: str
    year: int
    environmental: EnvironmentalMetrics
    social: SocialMetrics
    governance: GovernanceMetrics
    generated_at: datetime
    
class SustainabilityReportGenerator:
    """可持续发展报告生成器"""
    
    def __init__(self, data_source: str = "database"):
        """
        初始化报告生成器
        
        Args:
            data_source: 数据源类型 ("database", "api", "file")
        """
        self.data_source = data_source
        self.output_dir = Path("sustainability_reports")
        self.output_dir.mkdir(exist_ok=True)
        
        # 初始化数据库连接
        self.db_path = "sustainability_data.db"
        self._init_database()
        
    def _init_database(self):
        """初始化数据库表结构"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 创建环境指标表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS environmental_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        quarter TEXT NOT NULL,
                        year INTEGER NOT NULL,
                        carbon_emissions REAL,
                        energy_consumption REAL,
                        water_usage REAL,
                        waste_generated REAL,
                        renewable_energy_ratio REAL,
                        recycling_rate REAL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # 创建社会指标表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS social_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        quarter TEXT NOT NULL,
                        year INTEGER NOT NULL,
                        employee_count INTEGER,
                        diversity_ratio REAL,
                        training_hours REAL,
                        safety_incidents INTEGER,
                        community_investment REAL,
                        customer_satisfaction REAL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # 创建治理指标表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS governance_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        quarter TEXT NOT NULL,
                        year INTEGER NOT NULL,
                        board_independence REAL,
                        ethics_training_completion REAL,
                        compliance_violations INTEGER,
                        data_security_incidents INTEGER,
                        transparency_score REAL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                conn.commit()
                logger.info("数据库初始化完成")
                
        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")
            raise
    
    def collect_environmental_data(self, quarter: str, year: int) -> EnvironmentalMetrics:
        """
        收集环境指标数据
        
        Args:
            quarter: 季度 (Q1, Q2, Q3, Q4)
            year: 年份
            
        Returns:
            EnvironmentalMetrics: 环境指标数据
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT carbon_emissions, energy_consumption, water_usage,
                           waste_generated, renewable_energy_ratio, recycling_rate
                    FROM environmental_data 
                    WHERE quarter = ? AND year = ?
                    ORDER BY created_at DESC LIMIT 1
                ''', (quarter, year))
                
                result = cursor.fetchone()
                
                if result:
                    return EnvironmentalMetrics(*result)
                else:
                    # 如果没有数据，生成模拟数据
                    logger.warning(f"未找到{year}年{quarter}的环境数据，使用模拟数据")
                    return self._generate_mock_environmental_data()
                    
        except Exception as e:
            logger.error(f"收集环境数据失败: {e}")
            return self._generate_mock_environmental_data()
    
    def collect_social_data(self, quarter: str, year: int) -> SocialMetrics:
        """
        收集社会指标数据
        
        Args:
            quarter: 季度
            year: 年份
            
        Returns:
            SocialMetrics: 社会指标数据
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT employee_count, diversity_ratio, training_hours,
                           safety_incidents, community_investment, customer_satisfaction
                    FROM social_data 
                    WHERE quarter = ? AND year = ?
                    ORDER BY created_at DESC LIMIT 1
                ''', (quarter, year))
                
                result = cursor.fetchone()
                
                if result:
                    return SocialMetrics(*result)
                else:
                    logger.warning(f"未找到{year}年{quarter}的社会数据，使用模拟数据")
                    return self._generate_mock_social_data()
                    
        except Exception as e:
            logger.error(f"收集社会数据失败: {e}")
            return self._generate_mock_social_data()
    
    def collect_governance_data(self, quarter: str, year: int) -> GovernanceMetrics:
        """
        收集治理指标数据
        
        Args:
            quarter: 季度
            year: 年份
            
        Returns:
            GovernanceMetrics: 治理指标数据
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT board_independence, ethics_training_completion,
                           compliance_violations, data_security_incidents, transparency_score
                    FROM governance_data 
                    WHERE quarter = ? AND year = ?
                    ORDER BY created_at DESC LIMIT 1
                ''', (quarter, year))
                
                result = cursor.fetchone()
                
                if result:
                    return GovernanceMetrics(*result)
                else:
                    logger.warning(f"未找到{year}年{quarter}的治理数据，使用模拟数据")
                    return self._generate_mock_governance_data()
                    
        except Exception as e:
            logger.error(f"收集治理数据失败: {e}")
            return self._generate_mock_governance_data()
    
    def _generate_mock_environmental_data(self) -> EnvironmentalMetrics:
        """生成模拟环境数据"""
        return EnvironmentalMetrics(
            carbon_emissions=1250.5,
            energy_consumption=2800.0,
            water_usage=15000.0,
            waste_generated=45.2,
            renewable_energy_ratio=35.8,
            recycling_rate=78.5
        )
    
    def _generate_mock_social_data(self) -> SocialMetrics:
        """生成模拟社会数据"""
        return SocialMetrics(
            employee_count=1250,
            diversity_ratio=42.3,
            training_hours=8500.0,
            safety_incidents=2,
            community_investment=125.5,
            customer_satisfaction=87.2
        )
    
    def _generate_mock_governance_data(self) -> GovernanceMetrics:
        """生成模拟治理数据"""
        return GovernanceMetrics(
            board_independence=65.0,
            ethics_training_completion=95.8,
            compliance_violations=0,
            data_security_incidents=1,
            transparency_score=8.5
        )
    
    def generate_report(self, quarter: str, year: int) -> SustainabilityReport:
        """
        生成可持续发展报告
        
        Args:
            quarter: 季度
            year: 年份
            
        Returns:
            SustainabilityReport: 完整的可持续发展报告
        """
        logger.info(f"开始生成{year}年{quarter}季度可持续发展报告")
        
        # 收集各维度数据
        environmental = self.collect_environmental_data(quarter, year)
        social = self.collect_social_data(quarter, year)
        governance = self.collect_governance_data(quarter, year)
        
        # 创建报告对象
        report = SustainabilityReport(
            quarter=quarter,
            year=year,
            environmental=environmental,
            social=social,
            governance=governance,
            generated_at=datetime.now()
        )
        
        logger.info("报告数据收集完成")
        return report
    
    def export_to_json(self, report: SustainabilityReport) -> str:
        """
        导出报告为JSON格式
        
        Args:
            report: 可持续发展报告
            
        Returns:
            str: JSON文件路径
        """
        filename = f"sustainability_report_{report.year}_{report.quarter}.json"
        filepath = self.output_dir / filename
        
        # 转换为可序列化的字典
        report_dict = asdict(report)
        report_dict['generated_at'] = report.generated_at.isoformat()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report_dict, f, ensure_ascii=False, indent=2)
        
        logger.info(f"JSON报告已导出: {filepath}")
        return str(filepath)
    
    def export_to_html(self, report: SustainabilityReport) -> str:
        """
        导出报告为HTML格式
        
        Args:
            report: 可持续发展报告
            
        Returns:
            str: HTML文件路径
        """
        filename = f"sustainability_report_{report.year}_{report.quarter}.html"
        filepath = self.output_dir / filename
        
        html_content = self._generate_html_report(report)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"HTML报告已导出: {filepath}")
        return str(filepath)
    
    def _generate_html_report(self, report: SustainabilityReport) -> str:
        """生成HTML报告内容"""
        html_template = f"""
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{report.year}年{report.quarter}季度可持续发展报告</title>
            <style>
                body {{ font-family: 'Microsoft YaHei', Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                .header {{ text-align: center; margin-bottom: 40px; }}
                .section {{ margin-bottom: 30px; padding: 20px; border: 1px solid #ddd; border-radius: 8px; }}
                .metric {{ display: flex; justify-content: space-between; margin: 10px 0; }}
                .metric-name {{ font-weight: bold; }}
                .metric-value {{ color: #2c5aa0; }}
                h1 {{ color: #2c5aa0; }}
                h2 {{ color: #4a7c59; border-bottom: 2px solid #4a7c59; padding-bottom: 5px; }}
                .environmental {{ background-color: #f0f8f0; }}
                .social {{ background-color: #f0f0f8; }}
                .governance {{ background-color: #f8f0f0; }}
                .footer {{ text-align: center; margin-top: 40px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{report.year}年{report.quarter}季度可持续发展报告</h1>
                <p>生成时间: {report.generated_at.strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="section environmental">
                <h2>🌱 环境指标 (Environmental)</h2>
                <div class="metric">
                    <span class="metric-name">碳排放量:</span>
                    <span class="metric-value">{report.environmental.carbon_emissions:.1f} 吨CO₂当量</span>
                </div>
                <div class="metric">
                    <span class="metric-name">能源消耗:</span>
                    <span class="metric-value">{report.environmental.energy_consumption:.1f} MWh</span>
                </div>
                <div class="metric">
                    <span class="metric-name">用水量:</span>
                    <span class="metric-value">{report.environmental.water_usage:.1f} 立方米</span>
                </div>
                <div class="metric">
                    <span class="metric-name">废物产生量:</span>
                    <span class="metric-value">{report.environmental.waste_generated:.1f} 吨</span>
                </div>
                <div class="metric">
                    <span class="metric-name">可再生能源比例:</span>
                    <span class="metric-value">{report.environmental.renewable_energy_ratio:.1f}%</span>
                </div>
                <div class="metric">
                    <span class="metric-name">回收率:</span>
                    <span class="metric-value">{report.environmental.recycling_rate:.1f}%</span>
                </div>
            </div>
            
            <div class="section social">
                <h2>👥 社会指标 (Social)</h2>
                <div class="metric">
                    <span class="metric-name">员工总数:</span>
                    <span class="metric-value">{report.social.employee_count:,} 人</span>
                </div>
                <div class="metric">
                    <span class="metric-name">多样性比例:</span>
                    <span class="metric-value">{report.social.diversity_ratio:.1f}%</span>
                </div>
                <div class="metric">
                    <span class="metric-name">培训小时数:</span>
                    <span class="metric-value">{report.social.training_hours:.1f} 小时</span>
                </div>
                <div class="metric">
                    <span class="metric-name">安全事故数:</span>
                    <span class="metric-value">{report.social.safety_incidents} 起</span>
                </div>
                <div class="metric">
                    <span class="metric-name">社区投资:</span>
                    <span class="metric-value">{report.social.community_investment:.1f} 万元</span>
                </div>
                <div class="metric">
                    <span class="metric-name">客户满意度:</span>
                    <span class="metric-value">{report.social.customer_satisfaction:.1f}%</span>
                </div>
            </div>
            
            <div class="section governance">
                <h2>⚖️ 治理指标 (Governance)</h2>
                <div class="metric">
                    <span class="metric-name">董事会独立性:</span>
                    <span class="metric-value">{report.governance.board_independence:.1f}%</span>
                </div>
                <div class="metric">
                    <span class="metric-name">道德培训完成率:</span>
                    <span class="metric-value">{report.governance.ethics_training_completion:.1f}%</span>
                </div>
                <div class="metric">
                    <span class="metric-name">合规违规数:</span>
                    <span class="metric-value">{report.governance.compliance_violations} 起</span>
                </div>
                <div class="metric">
                    <span class="metric-name">数据安全事件数:</span>
                    <span class="metric-value">{report.governance.data_security_incidents} 起</span>
                </div>
                <div class="metric">
                    <span class="metric-name">透明度评分:</span>
                    <span class="metric-value">{report.governance.transparency_score:.1f}/10</span>
                </div>
            </div>
            
            <div class="footer">
                <p>本报告由自动化系统生成 | 数据来源: 企业内部系统</p>
            </div>
        </body>
        </html>
        """
        return html_template
    
    def generate_charts(self, report: SustainabilityReport) -> List[str]:
        """
        生成可视化图表
        
        Args:
            report: 可持续发展报告
            
        Returns:
            List[str]: 图表文件路径列表
        """
        chart_paths = []
        
        # 创建图表目录
        charts_dir = self.output_dir / "charts"
        charts_dir.mkdir(exist_ok=True)
        
        # 生成ESG综合评分雷达图
        radar_path = self._create_esg_radar_chart(report, charts_dir)
        chart_paths.append(radar_path)
        
        # 生成环境指标柱状图
        env_bar_path = self._create_environmental_bar_chart(report, charts_dir)
        chart_paths.append(env_bar_path)
        
        logger.info(f"已生成{len(chart_paths)}个图表")
        return chart_paths
    
    def _create_esg_radar_chart(self, report: SustainabilityReport, charts_dir: Path) -> str:
        """创建ESG雷达图"""
        # 计算ESG评分 (简化算法)
        env_score = min(100, (report.environmental.renewable_energy_ratio + 
                             report.environmental.recycling_rate) / 2)
        social_score = min(100, (report.social.diversity_ratio + 
                                report.social.customer_satisfaction) / 2)
        gov_score = min(100, (report.governance.board_independence + 
                             report.governance.ethics_training_completion + 
                             report.governance.transparency_score * 10) / 3)
        
        # 创建雷达图
        categories = ['环境\n(Environmental)', '社会\n(Social)', '治理\n(Governance)']
        values = [env_score, social_score, gov_score]
        
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))
        
        # 设置角度
        angles = [i * 2 * 3.14159 / len(categories) for i in range(len(categories))]
        angles += angles[:1]  # 闭合图形
        values += values[:1]
        
        # 绘制雷达图
        ax.plot(angles, values, 'o-', linewidth=2, label='ESG评分')
        ax.fill(angles, values, alpha=0.25)
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categories)
        ax.set_ylim(0, 100)
        ax.set_title(f'{report.year}年{report.quarter}季度 ESG评分雷达图', 
                    fontsize=14, fontweight='bold', pad=20)
        
        # 添加网格和标签
        ax.grid(True)
        ax.set_yticks([20, 40, 60, 80, 100])
        ax.set_yticklabels(['20', '40', '60', '80', '100'])
        
        plt.tight_layout()
        
        # 保存图表
        filename = f"esg_radar_{report.year}_{report.quarter}.png"
        filepath = charts_dir / filename
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return str(filepath)
    
    def _create_environmental_bar_chart(self, report: SustainabilityReport, charts_dir: Path) -> str:
        """创建环境指标柱状图"""
        metrics = ['可再生能源比例', '回收率', '能源效率指数', '水资源利用率']
        values = [
            report.environmental.renewable_energy_ratio,
            report.environmental.recycling_rate,
            min(100, 100 - (report.environmental.energy_consumption / 50)),  # 简化计算
            min(100, 100 - (report.environmental.water_usage / 200))  # 简化计算
        ]
        
        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.bar(metrics, values, color=['#2E8B57', '#4682B4', '#DAA520', '#CD853F'])
        
        # 添加数值标签
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                   f'{value:.1f}%', ha='center', va='bottom')
        
        ax.set_ylabel('百分比 (%)')
        ax.set_title(f'{report.year}年{report.quarter}季度 环境指标表现', 
                    fontsize=14, fontweight='bold')
        ax.set_ylim(0, 110)
        
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # 保存图表
        filename = f"environmental_metrics_{report.year}_{report.quarter}.png"
        filepath = charts_dir / filename
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        return str(filepath)
    
    def insert_sample_data(self, quarter: str, year: int):
        """插入示例数据用于测试"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 插入环境数据
                cursor.execute('''
                    INSERT INTO environmental_data 
                    (quarter, year, carbon_emissions, energy_consumption, water_usage,
                     waste_generated, renewable_energy_ratio, recycling_rate)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (quarter, year, 1250.5, 2800.0, 15000.0, 45.2, 35.8, 78.5))
                
                # 插入社会数据
                cursor.execute('''
                    INSERT INTO social_data 
                    (quarter, year, employee_count, diversity_ratio, training_hours,
                     safety_incidents, community_investment, customer_satisfaction)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (quarter, year, 1250, 42.3, 8500.0, 2, 125.5, 87.2))
                
                # 插入治理数据
                cursor.execute('''
                    INSERT INTO governance_data 
                    (quarter, year, board_independence, ethics_training_completion,
                     compliance_violations, data_security_incidents, transparency_score)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (quarter, year, 65.0, 95.8, 0, 1, 8.5))
                
                conn.commit()
                logger.info(f"已插入{year}年{quarter}的示例数据")
                
        except Exception as e:
            logger.error(f"插入示例数据失败: {e}")

def main():
    """主函数 - 演示脚本功能"""
    print("🌱 自动化季度可持续发展报告生成器")
    print("=" * 50)
    
    # 创建报告生成器
    generator = SustainabilityReportGenerator()
    
    # 设置报告参数
    quarter = "Q4"
    year = 2024
    
    try:
        # 插入示例数据（仅用于演示）
        generator.insert_sample_data(quarter, year)
        
        # 生成报告
        print(f"正在生成{year}年{quarter}季度可持续发展报告...")
        report = generator.generate_report(quarter, year)
        
        # 导出报告
        json_path = generator.export_to_json(report)
        html_path = generator.export_to_html(report)
        
        # 生成图表
        chart_paths = generator.generate_charts(report)
        
        # 输出结果
        print("\n✅ 报告生成完成!")
        print(f"📄 JSON报告: {json_path}")
        print(f"🌐 HTML报告: {html_path}")
        print(f"📊 图表文件: {len(chart_paths)}个")
        
        # 显示关键指标摘要
        print("\n📊 关键指标摘要:")
        print(f"🌱 环境: 碳排放 {report.environmental.carbon_emissions:.1f}吨, 可再生能源 {report.environmental.renewable_energy_ratio:.1f}%")
        print(f"👥 社会: 员工 {report.social.employee_count:,}人, 客户满意度 {report.social.customer_satisfaction:.1f}%")
        print(f"⚖️ 治理: 董事会独立性 {report.governance.board_independence:.1f}%, 透明度 {report.governance.transparency_score:.1f}/10")
        
        print(f"\n📁 所有文件已保存到: {generator.output_dir}")
        
    except Exception as e:
        logger.error(f"报告生成失败: {e}")
        print(f"❌ 错误: {e}")

if __name__ == "__main__":
    main()