#!/usr/bin/env python3
"""
生物信息分析流程脚本 - 专注于somatic mutation分析
Bioinformatics Analysis Pipeline - Focused on Somatic Mutation Analysis

作者: 生物信息团队
版本: 2.0.0
更新日期: 2024-12-19
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Tuple, Optional
import json
from pathlib import Path

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SomaticMutationAnalyzer:
    """
    体细胞突变分析器
    专门用于处理和分析somatic mutation数据
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        初始化分析器
        
        Args:
            config_file: 配置文件路径
        """
        self.config = self._load_config(config_file)
        self.mutation_data = None
        self.filtered_data = None
        self.analysis_results = {}
        
        logger.info("SomaticMutationAnalyzer initialized successfully")
    
    def _load_config(self, config_file: Optional[str]) -> Dict:
        """加载配置文件"""
        default_config = {
            "quality_threshold": 30,
            "depth_threshold": 10,
            "allele_frequency_threshold": 0.05,
            "somatic_confidence_threshold": 0.8,
            "output_format": "vcf"
        }
        
        if config_file and Path(config_file).exists():
            with open(config_file, 'r') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        
        return default_config
    
    def load_mutation_data(self, file_path: str, file_format: str = "vcf") -> bool:
        """
        加载突变数据
        
        Args:
            file_path: 数据文件路径
            file_format: 文件格式 (vcf, tsv, csv)
            
        Returns:
            bool: 加载是否成功
        """
        try:
            if file_format.lower() == "vcf":
                self.mutation_data = self._parse_vcf(file_path)
            elif file_format.lower() in ["tsv", "csv"]:
                separator = '\t' if file_format.lower() == "tsv" else ','
                self.mutation_data = pd.read_csv(file_path, sep=separator)
            else:
                raise ValueError(f"Unsupported file format: {file_format}")
            
            logger.info(f"Successfully loaded {len(self.mutation_data)} mutations from {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load mutation data: {str(e)}")
            return False
    
    def _parse_vcf(self, vcf_path: str) -> pd.DataFrame:
        """
        解析VCF文件
        这是一个简化的VCF解析器，实际应用中建议使用专业的VCF解析库
        """
        mutations = []
        
        with open(vcf_path, 'r') as f:
            for line in f:
                if line.startswith('#'):
                    continue
                
                fields = line.strip().split('\t')
                if len(fields) >= 8:
                    mutation = {
                        'chromosome': fields[0],
                        'position': int(fields[1]),
                        'reference': fields[3],
                        'alternative': fields[4],
                        'quality': float(fields[5]) if fields[5] != '.' else 0,
                        'info': fields[7]
                    }
                    mutations.append(mutation)
        
        return pd.DataFrame(mutations)
    
    def filter_somatic_mutations(self) -> bool:
        """
        过滤体细胞突变
        应用质量控制标准来识别高置信度的somatic mutations
        
        Returns:
            bool: 过滤是否成功
        """
        if self.mutation_data is None:
            logger.error("No mutation data loaded. Please load data first.")
            return False
        
        try:
            # 应用质量过滤
            quality_filter = self.mutation_data['quality'] >= self.config['quality_threshold']
            
            # 模拟深度和等位基因频率过滤（实际应用中需要从INFO字段解析）
            # 这里使用随机数据作为示例
            np.random.seed(42)
            self.mutation_data['depth'] = np.random.randint(5, 100, len(self.mutation_data))
            self.mutation_data['allele_frequency'] = np.random.uniform(0.01, 0.5, len(self.mutation_data))
            self.mutation_data['somatic_confidence'] = np.random.uniform(0.1, 1.0, len(self.mutation_data))
            
            depth_filter = self.mutation_data['depth'] >= self.config['depth_threshold']
            af_filter = self.mutation_data['allele_frequency'] >= self.config['allele_frequency_threshold']
            somatic_filter = self.mutation_data['somatic_confidence'] >= self.config['somatic_confidence_threshold']
            
            # 组合所有过滤条件
            combined_filter = quality_filter & depth_filter & af_filter & somatic_filter
            
            self.filtered_data = self.mutation_data[combined_filter].copy()
            
            logger.info(f"Filtered {len(self.filtered_data)} high-confidence somatic mutations "
                       f"from {len(self.mutation_data)} total mutations")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to filter somatic mutations: {str(e)}")
            return False
    
    def analyze_mutation_patterns(self) -> Dict:
        """
        分析突变模式
        
        Returns:
            Dict: 分析结果
        """
        if self.filtered_data is None:
            logger.error("No filtered data available. Please filter mutations first.")
            return {}
        
        try:
            analysis = {}
            
            # 突变类型分布
            mutation_types = self._classify_mutations()
            analysis['mutation_types'] = mutation_types
            
            # 染色体分布
            chr_distribution = self.filtered_data['chromosome'].value_counts().to_dict()
            analysis['chromosome_distribution'] = chr_distribution
            
            # 质量统计
            quality_stats = {
                'mean_quality': float(self.filtered_data['quality'].mean()),
                'median_quality': float(self.filtered_data['quality'].median()),
                'min_quality': float(self.filtered_data['quality'].min()),
                'max_quality': float(self.filtered_data['quality'].max())
            }
            analysis['quality_statistics'] = quality_stats
            
            # somatic突变置信度统计
            somatic_stats = {
                'mean_confidence': float(self.filtered_data['somatic_confidence'].mean()),
                'high_confidence_count': int(sum(self.filtered_data['somatic_confidence'] > 0.9)),
                'medium_confidence_count': int(sum((self.filtered_data['somatic_confidence'] > 0.7) & 
                                                 (self.filtered_data['somatic_confidence'] <= 0.9))),
                'low_confidence_count': int(sum(self.filtered_data['somatic_confidence'] <= 0.7))
            }
            analysis['somatic_confidence_statistics'] = somatic_stats
            
            self.analysis_results = analysis
            logger.info("Mutation pattern analysis completed successfully")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze mutation patterns: {str(e)}")
            return {}
    
    def _classify_mutations(self) -> Dict:
        """分类突变类型"""
        mutation_types = {}
        
        for _, row in self.filtered_data.iterrows():
            ref = row['reference']
            alt = row['alternative']
            
            if len(ref) == 1 and len(alt) == 1:
                # SNV (Single Nucleotide Variant)
                mutation_type = f"{ref}>{alt}"
                mutation_types[mutation_type] = mutation_types.get(mutation_type, 0) + 1
            elif len(ref) > len(alt):
                # Deletion
                mutation_types['deletion'] = mutation_types.get('deletion', 0) + 1
            elif len(ref) < len(alt):
                # Insertion
                mutation_types['insertion'] = mutation_types.get('insertion', 0) + 1
            else:
                # Complex
                mutation_types['complex'] = mutation_types.get('complex', 0) + 1
        
        return mutation_types
    
    def generate_report(self, output_path: str = "somatic_mutation_report.json") -> bool:
        """
        生成分析报告
        
        Args:
            output_path: 输出文件路径
            
        Returns:
            bool: 报告生成是否成功
        """
        try:
            report = {
                'analysis_summary': {
                    'total_mutations': len(self.mutation_data) if self.mutation_data is not None else 0,
                    'filtered_somatic_mutations': len(self.filtered_data) if self.filtered_data is not None else 0,
                    'filter_parameters': self.config
                },
                'analysis_results': self.analysis_results,
                'timestamp': pd.Timestamp.now().isoformat()
            }
            
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Analysis report saved to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to generate report: {str(e)}")
            return False
    
    def export_filtered_mutations(self, output_path: str = "filtered_somatic_mutations.tsv") -> bool:
        """
        导出过滤后的somatic mutations
        
        Args:
            output_path: 输出文件路径
            
        Returns:
            bool: 导出是否成功
        """
        if self.filtered_data is None:
            logger.error("No filtered data available for export")
            return False
        
        try:
            self.filtered_data.to_csv(output_path, sep='\t', index=False)
            logger.info(f"Filtered somatic mutations exported to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export filtered mutations: {str(e)}")
            return False


def main():
    """主函数 - 演示somatic mutation分析流程"""
    print("=== 生物信息分析流程 - Somatic Mutation Analysis ===")
    
    # 初始化分析器
    analyzer = SomaticMutationAnalyzer()
    
    # 创建示例数据（实际使用中应该加载真实的VCF或其他格式文件）
    print("创建示例somatic mutation数据...")
    sample_data = pd.DataFrame({
        'chromosome': ['chr1', 'chr2', 'chr3', 'chr1', 'chr2'] * 20,
        'position': range(1000, 1100),
        'reference': ['A', 'T', 'G', 'C', 'A'] * 20,
        'alternative': ['T', 'C', 'A', 'G', 'C'] * 20,
        'quality': np.random.uniform(20, 60, 100)
    })
    
    analyzer.mutation_data = sample_data
    print(f"加载了 {len(sample_data)} 个突变位点")
    
    # 过滤somatic mutations
    print("正在过滤高置信度somatic mutations...")
    if analyzer.filter_somatic_mutations():
        print(f"过滤完成，保留 {len(analyzer.filtered_data)} 个高质量somatic mutations")
    
    # 分析突变模式
    print("正在分析somatic mutation模式...")
    results = analyzer.analyze_mutation_patterns()
    
    if results:
        print("分析结果:")
        print(f"- 突变类型分布: {results.get('mutation_types', {})}")
        print(f"- 平均质量分数: {results.get('quality_statistics', {}).get('mean_quality', 0):.2f}")
        print(f"- 高置信度somatic mutations: {results.get('somatic_confidence_statistics', {}).get('high_confidence_count', 0)}")
    
    # 生成报告
    print("正在生成分析报告...")
    if analyzer.generate_report():
        print("分析报告已生成: somatic_mutation_report.json")
    
    # 导出过滤后的数据
    if analyzer.export_filtered_mutations():
        print("过滤后的somatic mutations已导出: filtered_somatic_mutations.tsv")
    
    print("=== Somatic Mutation分析流程完成 ===")


if __name__ == "__main__":
    main()