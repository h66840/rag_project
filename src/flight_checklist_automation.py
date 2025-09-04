#!/usr/bin/env python3
"""
飞行前检查清单自动化脚本
Flight Pre-Check Automation Script

该脚本用于自动化飞行前的安全检查流程，提高效率并减少人为错误。
This script automates the pre-flight safety check process to improve efficiency and reduce human error.

作者: 开发团队
版本: 1.0.0
日期: 2025-01-08
"""

import json
import datetime
import logging
import sys
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from enum import Enum

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('flight_checklist.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

class CheckStatus(Enum):
    """检查状态枚举"""
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    SKIPPED = "skipped"

class Priority(Enum):
    """优先级枚举"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class CheckItem:
    """检查项目数据类"""
    id: str
    name: str
    description: str
    category: str
    priority: Priority
    status: CheckStatus = CheckStatus.PENDING
    result: Optional[str] = None
    timestamp: Optional[str] = None
    notes: Optional[str] = None

class FlightChecklistAutomation:
    """飞行前检查清单自动化类"""
    
    def __init__(self, aircraft_id: str, pilot_id: str):
        """
        初始化检查清单
        
        Args:
            aircraft_id: 飞机ID
            pilot_id: 飞行员ID
        """
        self.aircraft_id = aircraft_id
        self.pilot_id = pilot_id
        self.checklist_id = f"FL_{aircraft_id}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.start_time = datetime.datetime.now()
        self.check_items: List[CheckItem] = []
        self.logger = logging.getLogger(__name__)
        
        # 初始化检查项目
        self._initialize_checklist()
        
    def _initialize_checklist(self):
        """初始化检查清单项目"""
        # 关键系统检查
        critical_checks = [
            CheckItem("ENG_001", "发动机预检", "检查发动机外观、油液泄漏", "发动机系统", Priority.CRITICAL),
            CheckItem("FUEL_001", "燃油系统", "检查燃油量、燃油质量", "燃油系统", Priority.CRITICAL),
            CheckItem("CTRL_001", "操纵面检查", "检查副翼、升降舵、方向舵", "操纵系统", Priority.CRITICAL),
            CheckItem("LAND_001", "起落架检查", "检查起落架状态、轮胎气压", "起落架系统", Priority.CRITICAL),
        ]
        
        # 重要系统检查
        high_priority_checks = [
            CheckItem("ELEC_001", "电气系统", "检查电池、发电机、电气设备", "电气系统", Priority.HIGH),
            CheckItem("COMM_001", "通讯设备", "检查无线电、导航设备", "通讯导航", Priority.HIGH),
            CheckItem("INST_001", "仪表检查", "检查飞行仪表、警告灯", "仪表系统", Priority.HIGH),
        ]
        
        # 一般检查项目
        medium_priority_checks = [
            CheckItem("CABIN_001", "客舱检查", "检查座椅、安全带、紧急设备", "客舱系统", Priority.MEDIUM),
            CheckItem("CARGO_001", "货舱检查", "检查货物装载、重心平衡", "货舱系统", Priority.MEDIUM),
            CheckItem("WEATHER_001", "天气检查", "获取最新天气信息", "气象信息", Priority.MEDIUM),
        ]
        
        # 低优先级检查
        low_priority_checks = [
            CheckItem("DOC_001", "文档检查", "检查飞行计划、许可证", "文档资料", Priority.LOW),
            CheckItem("CLEAN_001", "清洁检查", "检查飞机外观清洁度", "外观检查", Priority.LOW),
        ]
        
        self.check_items.extend(critical_checks)
        self.check_items.extend(high_priority_checks)
        self.check_items.extend(medium_priority_checks)
        self.check_items.extend(low_priority_checks)
        
        self.logger.info(f"初始化检查清单完成，共 {len(self.check_items)} 个检查项目")

    def perform_automated_checks(self) -> Dict[str, any]:
        """执行自动化检查"""
        self.logger.info("开始执行自动化检查...")
        results = {
            "checklist_id": self.checklist_id,
            "aircraft_id": self.aircraft_id,
            "pilot_id": self.pilot_id,
            "start_time": self.start_time.isoformat(),
            "checks": [],
            "summary": {}
        }
        
        for item in self.check_items:
            self.logger.info(f"执行检查: {item.name}")
            
            # 模拟自动化检查逻辑
            check_result = self._simulate_check(item)
            item.status = check_result["status"]
            item.result = check_result["result"]
            item.timestamp = datetime.datetime.now().isoformat()
            item.notes = check_result.get("notes", "")
            
            results["checks"].append(asdict(item))
            
        # 生成检查摘要
        results["summary"] = self._generate_summary()
        results["end_time"] = datetime.datetime.now().isoformat()
        
        self.logger.info("自动化检查完成")
        return results

    def _simulate_check(self, item: CheckItem) -> Dict[str, any]:
        """
        模拟检查过程（实际应用中应连接真实的传感器和系统）
        
        Args:
            item: 检查项目
            
        Returns:
            检查结果字典
        """
        import random
        
        # 模拟不同的检查结果
        if item.priority == Priority.CRITICAL:
            # 关键项目通过率较高
            if random.random() < 0.95:
                return {
                    "status": CheckStatus.PASSED,
                    "result": "检查通过",
                    "notes": f"{item.name}状态正常"
                }
            else:
                return {
                    "status": CheckStatus.FAILED,
                    "result": "检查失败",
                    "notes": f"{item.name}发现异常，需要维护"
                }
        elif item.priority == Priority.HIGH:
            # 重要项目
            rand = random.random()
            if rand < 0.85:
                return {
                    "status": CheckStatus.PASSED,
                    "result": "检查通过",
                    "notes": f"{item.name}状态正常"
                }
            elif rand < 0.95:
                return {
                    "status": CheckStatus.WARNING,
                    "result": "检查警告",
                    "notes": f"{item.name}有轻微异常，建议关注"
                }
            else:
                return {
                    "status": CheckStatus.FAILED,
                    "result": "检查失败",
                    "notes": f"{item.name}发现问题"
                }
        else:
            # 中低优先级项目
            rand = random.random()
            if rand < 0.80:
                return {
                    "status": CheckStatus.PASSED,
                    "result": "检查通过",
                    "notes": f"{item.name}状态正常"
                }
            elif rand < 0.90:
                return {
                    "status": CheckStatus.WARNING,
                    "result": "检查警告",
                    "notes": f"{item.name}需要注意"
                }
            else:
                return {
                    "status": CheckStatus.SKIPPED,
                    "result": "检查跳过",
                    "notes": f"{item.name}条件不满足，跳过检查"
                }

    def _generate_summary(self) -> Dict[str, any]:
        """生成检查摘要"""
        summary = {
            "total_checks": len(self.check_items),
            "passed": 0,
            "failed": 0,
            "warnings": 0,
            "skipped": 0,
            "critical_issues": [],
            "overall_status": "UNKNOWN"
        }
        
        for item in self.check_items:
            if item.status == CheckStatus.PASSED:
                summary["passed"] += 1
            elif item.status == CheckStatus.FAILED:
                summary["failed"] += 1
                if item.priority == Priority.CRITICAL:
                    summary["critical_issues"].append({
                        "id": item.id,
                        "name": item.name,
                        "notes": item.notes
                    })
            elif item.status == CheckStatus.WARNING:
                summary["warnings"] += 1
            elif item.status == CheckStatus.SKIPPED:
                summary["skipped"] += 1
        
        # 确定总体状态
        if summary["failed"] > 0 and len(summary["critical_issues"]) > 0:
            summary["overall_status"] = "CRITICAL_FAILURE"
        elif summary["failed"] > 0:
            summary["overall_status"] = "FAILURE"
        elif summary["warnings"] > 0:
            summary["overall_status"] = "WARNING"
        else:
            summary["overall_status"] = "PASSED"
            
        return summary

    def export_report(self, results: Dict[str, any], format: str = "json") -> str:
        """
        导出检查报告
        
        Args:
            results: 检查结果
            format: 导出格式 (json, html, pdf)
            
        Returns:
            报告文件路径
        """
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format.lower() == "json":
            filename = f"flight_checklist_report_{self.checklist_id}_{timestamp}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            self.logger.info(f"JSON报告已导出: {filename}")
            return filename
            
        elif format.lower() == "html":
            filename = f"flight_checklist_report_{self.checklist_id}_{timestamp}.html"
            html_content = self._generate_html_report(results)
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            self.logger.info(f"HTML报告已导出: {filename}")
            return filename
            
        else:
            raise ValueError(f"不支持的导出格式: {format}")

    def _generate_html_report(self, results: Dict[str, any]) -> str:
        """生成HTML格式报告"""
        html_template = f"""
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>飞行前检查清单报告</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
                .summary {{ margin: 20px 0; padding: 15px; background-color: #e8f4fd; border-radius: 5px; }}
                .check-item {{ margin: 10px 0; padding: 10px; border: 1px solid #ddd; border-radius: 3px; }}
                .passed {{ background-color: #d4edda; }}
                .failed {{ background-color: #f8d7da; }}
                .warning {{ background-color: #fff3cd; }}
                .skipped {{ background-color: #e2e3e5; }}
                .critical {{ border-left: 5px solid #dc3545; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>飞行前检查清单报告</h1>
                <p><strong>检查清单ID:</strong> {results['checklist_id']}</p>
                <p><strong>飞机ID:</strong> {results['aircraft_id']}</p>
                <p><strong>飞行员ID:</strong> {results['pilot_id']}</p>
                <p><strong>检查时间:</strong> {results['start_time']} - {results.get('end_time', 'N/A')}</p>
            </div>
            
            <div class="summary">
                <h2>检查摘要</h2>
                <p><strong>总体状态:</strong> {results['summary']['overall_status']}</p>
                <p><strong>总检查项:</strong> {results['summary']['total_checks']}</p>
                <p><strong>通过:</strong> {results['summary']['passed']}</p>
                <p><strong>失败:</strong> {results['summary']['failed']}</p>
                <p><strong>警告:</strong> {results['summary']['warnings']}</p>
                <p><strong>跳过:</strong> {results['summary']['skipped']}</p>
            </div>
            
            <h2>详细检查结果</h2>
        """
        
        for check in results['checks']:
            status_class = check['status'].lower()
            priority_class = "critical" if check['priority'] == "critical" else ""
            html_template += f"""
            <div class="check-item {status_class} {priority_class}">
                <h3>{check['name']} ({check['id']})</h3>
                <p><strong>类别:</strong> {check['category']}</p>
                <p><strong>优先级:</strong> {check['priority']}</p>
                <p><strong>状态:</strong> {check['status']}</p>
                <p><strong>结果:</strong> {check['result']}</p>
                <p><strong>备注:</strong> {check.get('notes', 'N/A')}</p>
                <p><strong>检查时间:</strong> {check.get('timestamp', 'N/A')}</p>
            </div>
            """
        
        html_template += """
        </body>
        </html>
        """
        
        return html_template

    def get_dashboard_data(self) -> Dict[str, any]:
        """获取仪表板显示数据"""
        summary = self._generate_summary()
        
        dashboard_data = {
            "checklist_id": self.checklist_id,
            "aircraft_id": self.aircraft_id,
            "status": summary["overall_status"],
            "progress": {
                "completed": summary["passed"] + summary["failed"] + summary["warnings"],
                "total": summary["total_checks"],
                "percentage": round((summary["passed"] + summary["failed"] + summary["warnings"]) / summary["total_checks"] * 100, 2)
            },
            "alerts": {
                "critical": len(summary["critical_issues"]),
                "warnings": summary["warnings"],
                "failures": summary["failed"]
            },
            "last_updated": datetime.datetime.now().isoformat()
        }
        
        return dashboard_data

def main():
    """主函数 - 演示脚本使用"""
    print("飞行前检查清单自动化脚本启动...")
    
    # 创建检查清单实例
    checklist = FlightChecklistAutomation("A320-001", "PILOT-12345")
    
    # 执行自动化检查
    results = checklist.perform_automated_checks()
    
    # 导出报告
    json_report = checklist.export_report(results, "json")
    html_report = checklist.export_report(results, "html")
    
    # 获取仪表板数据
    dashboard_data = checklist.get_dashboard_data()
    
    print(f"\n检查完成!")
    print(f"总体状态: {results['summary']['overall_status']}")
    print(f"JSON报告: {json_report}")
    print(f"HTML报告: {html_report}")
    print(f"仪表板数据: {json.dumps(dashboard_data, ensure_ascii=False, indent=2)}")

if __name__ == "__main__":
    main()