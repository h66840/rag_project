#!/usr/bin/env python3
"""
Inventory Report Generator
=========================

A comprehensive tool for generating automated weekly inventory reports.
Supports multiple data sources and output formats with email notifications.

Author: Team Development
Created: 2024
Version: 1.0.0
"""

import os
import sys
import json
import csv
import sqlite3
import logging
import smtplib
import argparse
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from typing import Dict, List, Optional, Any
import pandas as pd
from jinja2 import Template


class InventoryReportGenerator:
    """Main class for generating inventory reports."""
    
    def __init__(self, config_file: str = "config.json"):
        """Initialize the report generator with configuration."""
        self.config = self._load_config(config_file)
        self.setup_logging()
        self.data_sources = []
        self.report_data = {}
        
    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        default_config = {
            "data_sources": {
                "csv_files": [],
                "json_files": [],
                "database": {
                    "enabled": False,
                    "connection_string": "",
                    "query": ""
                }
            },
            "output": {
                "format": "html",
                "filename_template": "inventory_report_{date}.{format}",
                "output_directory": "./reports"
            },
            "email": {
                "enabled": False,
                "smtp_server": "",
                "smtp_port": 587,
                "username": "",
                "password": "",
                "recipients": [],
                "subject_template": "Weekly Inventory Report - {date}"
            },
            "report_settings": {
                "include_low_stock_alerts": True,
                "low_stock_threshold": 10,
                "include_charts": True,
                "currency_symbol": "$"
            }
        }
        
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    # Merge with default config
                    default_config.update(user_config)
            except Exception as e:
                print(f"Warning: Could not load config file {config_file}: {e}")
                print("Using default configuration.")
        
        return default_config
    
    def setup_logging(self):
        """Setup logging configuration."""
        log_level = self.config.get('logging', {}).get('level', 'INFO')
        log_file = self.config.get('logging', {}).get('file', 'inventory_report.log')
        
        logging.basicConfig(
            level=getattr(logging, log_level),
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def load_csv_data(self, file_path: str) -> pd.DataFrame:
        """Load inventory data from CSV file."""
        try:
            self.logger.info(f"Loading CSV data from {file_path}")
            df = pd.read_csv(file_path)
            self.logger.info(f"Loaded {len(df)} records from CSV")
            return df
        except Exception as e:
            self.logger.error(f"Error loading CSV file {file_path}: {e}")
            return pd.DataFrame()
    
    def load_json_data(self, file_path: str) -> pd.DataFrame:
        """Load inventory data from JSON file."""
        try:
            self.logger.info(f"Loading JSON data from {file_path}")
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict) and 'inventory' in data:
                df = pd.DataFrame(data['inventory'])
            else:
                df = pd.DataFrame([data])
            
            self.logger.info(f"Loaded {len(df)} records from JSON")
            return df
        except Exception as e:
            self.logger.error(f"Error loading JSON file {file_path}: {e}")
            return pd.DataFrame()
    
    def load_database_data(self) -> pd.DataFrame:
        """Load inventory data from database."""
        db_config = self.config['data_sources']['database']
        if not db_config.get('enabled', False):
            return pd.DataFrame()
        
        try:
            self.logger.info("Loading data from database")
            connection_string = db_config['connection_string']
            query = db_config['query']
            
            # Simple SQLite support for demo
            if connection_string.startswith('sqlite:'):
                db_path = connection_string.replace('sqlite:', '')
                conn = sqlite3.connect(db_path)
                df = pd.read_sql_query(query, conn)
                conn.close()
            else:
                # For other databases, you would use appropriate connectors
                self.logger.warning("Only SQLite databases are supported in this demo")
                return pd.DataFrame()
            
            self.logger.info(f"Loaded {len(df)} records from database")
            return df
        except Exception as e:
            self.logger.error(f"Error loading database data: {e}")
            return pd.DataFrame()
    
    def collect_data(self) -> pd.DataFrame:
        """Collect data from all configured sources."""
        all_data = []
        
        # Load CSV files
        for csv_file in self.config['data_sources']['csv_files']:
            df = self.load_csv_data(csv_file)
            if not df.empty:
                all_data.append(df)
        
        # Load JSON files
        for json_file in self.config['data_sources']['json_files']:
            df = self.load_json_data(json_file)
            if not df.empty:
                all_data.append(df)
        
        # Load database data
        db_df = self.load_database_data()
        if not db_df.empty:
            all_data.append(db_df)
        
        # Combine all data
        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            self.logger.info(f"Combined data: {len(combined_df)} total records")
            return combined_df
        else:
            self.logger.warning("No data loaded from any source")
            return self._generate_sample_data()
    
    def _generate_sample_data(self) -> pd.DataFrame:
        """Generate sample inventory data for demonstration."""
        self.logger.info("Generating sample inventory data")
        sample_data = [
            {"item_id": "ITM001", "name": "Widget A", "category": "Electronics", "quantity": 150, "unit_price": 25.99, "supplier": "TechCorp"},
            {"item_id": "ITM002", "name": "Widget B", "category": "Electronics", "quantity": 8, "unit_price": 45.50, "supplier": "TechCorp"},
            {"item_id": "ITM003", "name": "Gadget X", "category": "Tools", "quantity": 75, "unit_price": 12.75, "supplier": "ToolMaster"},
            {"item_id": "ITM004", "name": "Component Y", "category": "Parts", "quantity": 5, "unit_price": 89.99, "supplier": "PartsPro"},
            {"item_id": "ITM005", "name": "Device Z", "category": "Electronics", "quantity": 200, "unit_price": 15.25, "supplier": "DeviceCo"},
        ]
        return pd.DataFrame(sample_data)
    
    def analyze_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze inventory data and generate insights."""
        self.logger.info("Analyzing inventory data")
        
        analysis = {
            "total_items": len(df),
            "total_value": 0,
            "categories": {},
            "suppliers": {},
            "low_stock_items": [],
            "top_value_items": [],
            "summary_stats": {}
        }
        
        if df.empty:
            return analysis
        
        # Ensure required columns exist
        required_columns = ['quantity', 'unit_price']
        for col in required_columns:
            if col not in df.columns:
                self.logger.warning(f"Required column '{col}' not found in data")
                return analysis
        
        # Calculate total value
        df['total_value'] = df['quantity'] * df['unit_price']
        analysis['total_value'] = df['total_value'].sum()
        
        # Category analysis
        if 'category' in df.columns:
            category_stats = df.groupby('category').agg({
                'quantity': 'sum',
                'total_value': 'sum',
                'item_id': 'count'
            }).to_dict('index')
            analysis['categories'] = category_stats
        
        # Supplier analysis
        if 'supplier' in df.columns:
            supplier_stats = df.groupby('supplier').agg({
                'quantity': 'sum',
                'total_value': 'sum',
                'item_id': 'count'
            }).to_dict('index')
            analysis['suppliers'] = supplier_stats
        
        # Low stock alerts
        threshold = self.config['report_settings']['low_stock_threshold']
        low_stock = df[df['quantity'] <= threshold]
        analysis['low_stock_items'] = low_stock.to_dict('records')
        
        # Top value items
        top_items = df.nlargest(5, 'total_value')
        analysis['top_value_items'] = top_items.to_dict('records')
        
        # Summary statistics
        analysis['summary_stats'] = {
            'avg_quantity': df['quantity'].mean(),
            'avg_unit_price': df['unit_price'].mean(),
            'total_quantity': df['quantity'].sum(),
            'unique_categories': df['category'].nunique() if 'category' in df.columns else 0,
            'unique_suppliers': df['supplier'].nunique() if 'supplier' in df.columns else 0
        }
        
        return analysis
    
    def generate_html_report(self, analysis: Dict[str, Any]) -> str:
        """Generate HTML report from analysis data."""
        template_str = """
<!DOCTYPE html>
<html>
<head>
    <title>Inventory Report - {{ date }}</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background-color: #f0f0f0; padding: 20px; border-radius: 5px; }
        .summary { display: flex; justify-content: space-around; margin: 20px 0; }
        .summary-item { text-align: center; padding: 15px; background-color: #e8f4f8; border-radius: 5px; }
        .alert { background-color: #ffebee; border-left: 4px solid #f44336; padding: 10px; margin: 10px 0; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        .currency { color: #2e7d32; font-weight: bold; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Weekly Inventory Report</h1>
        <p>Generated on: {{ date }}</p>
    </div>
    
    <div class="summary">
        <div class="summary-item">
            <h3>Total Items</h3>
            <p>{{ analysis.total_items }}</p>
        </div>
        <div class="summary-item">
            <h3>Total Value</h3>
            <p class="currency">{{ currency }}{{ "%.2f"|format(analysis.total_value) }}</p>
        </div>
        <div class="summary-item">
            <h3>Categories</h3>
            <p>{{ analysis.summary_stats.unique_categories }}</p>
        </div>
        <div class="summary-item">
            <h3>Suppliers</h3>
            <p>{{ analysis.summary_stats.unique_suppliers }}</p>
        </div>
    </div>
    
    {% if analysis.low_stock_items %}
    <div class="alert">
        <h3>⚠️ Low Stock Alerts</h3>
        <table>
            <tr><th>Item ID</th><th>Name</th><th>Quantity</th><th>Category</th></tr>
            {% for item in analysis.low_stock_items %}
            <tr>
                <td>{{ item.item_id }}</td>
                <td>{{ item.name }}</td>
                <td>{{ item.quantity }}</td>
                <td>{{ item.category or 'N/A' }}</td>
            </tr>
            {% endfor %}
        </table>
    </div>
    {% endif %}
    
    <h3>Top Value Items</h3>
    <table>
        <tr><th>Item ID</th><th>Name</th><th>Quantity</th><th>Unit Price</th><th>Total Value</th></tr>
        {% for item in analysis.top_value_items %}
        <tr>
            <td>{{ item.item_id }}</td>
            <td>{{ item.name }}</td>
            <td>{{ item.quantity }}</td>
            <td class="currency">{{ currency }}{{ "%.2f"|format(item.unit_price) }}</td>
            <td class="currency">{{ currency }}{{ "%.2f"|format(item.total_value) }}</td>
        </tr>
        {% endfor %}
    </table>
    
    {% if analysis.categories %}
    <h3>Category Breakdown</h3>
    <table>
        <tr><th>Category</th><th>Items</th><th>Total Quantity</th><th>Total Value</th></tr>
        {% for category, stats in analysis.categories.items() %}
        <tr>
            <td>{{ category }}</td>
            <td>{{ stats.item_id }}</td>
            <td>{{ stats.quantity }}</td>
            <td class="currency">{{ currency }}{{ "%.2f"|format(stats.total_value) }}</td>
        </tr>
        {% endfor %}
    </table>
    {% endif %}
    
    <div style="margin-top: 40px; font-size: 12px; color: #666;">
        <p>Report generated by Inventory Report Generator v1.0.0</p>
    </div>
</body>
</html>
        """
        
        template = Template(template_str)
        currency = self.config['report_settings']['currency_symbol']
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return template.render(
            analysis=analysis,
            currency=currency,
            date=date
        )
    
    def save_report(self, content: str, format: str = "html") -> str:
        """Save report to file."""
        output_config = self.config['output']
        output_dir = Path(output_config['output_directory'])
        output_dir.mkdir(exist_ok=True)
        
        date_str = datetime.now().strftime("%Y%m%d")
        filename = output_config['filename_template'].format(
            date=date_str,
            format=format
        )
        
        file_path = output_dir / filename
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.logger.info(f"Report saved to {file_path}")
        return str(file_path)
    
    def send_email_report(self, file_path: str):
        """Send report via email."""
        email_config = self.config['email']
        if not email_config.get('enabled', False):
            self.logger.info("Email sending is disabled")
            return
        
        try:
            self.logger.info("Sending email report")
            
            msg = MIMEMultipart()
            msg['From'] = email_config['username']
            msg['To'] = ', '.join(email_config['recipients'])
            
            date_str = datetime.now().strftime("%Y-%m-%d")
            subject = email_config['subject_template'].format(date=date_str)
            msg['Subject'] = subject
            
            # Email body
            body = f"""
            Dear Team,
            
            Please find attached the weekly inventory report generated on {date_str}.
            
            Best regards,
            Inventory Management System
            """
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach report file
            with open(file_path, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {os.path.basename(file_path)}'
            )
            msg.attach(part)
            
            # Send email
            server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
            server.starttls()
            server.login(email_config['username'], email_config['password'])
            server.send_message(msg)
            server.quit()
            
            self.logger.info("Email sent successfully")
            
        except Exception as e:
            self.logger.error(f"Error sending email: {e}")
    
    def generate_report(self) -> str:
        """Main method to generate the complete inventory report."""
        self.logger.info("Starting inventory report generation")
        
        try:
            # Collect data from all sources
            df = self.collect_data()
            
            # Analyze the data
            analysis = self.analyze_data(df)
            
            # Generate report content
            format = self.config['output']['format']
            if format.lower() == 'html':
                content = self.generate_html_report(analysis)
            else:
                # For other formats, you could add JSON, CSV, etc.
                content = json.dumps(analysis, indent=2, default=str)
            
            # Save report
            file_path = self.save_report(content, format)
            
            # Send email if configured
            self.send_email_report(file_path)
            
            self.logger.info("Inventory report generation completed successfully")
            return file_path
            
        except Exception as e:
            self.logger.error(f"Error generating report: {e}")
            raise


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description='Generate inventory reports')
    parser.add_argument('--config', '-c', default='config.json',
                       help='Configuration file path (default: config.json)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Create and run report generator
    try:
        generator = InventoryReportGenerator(args.config)
        if args.verbose:
            generator.logger.setLevel(logging.DEBUG)
        
        file_path = generator.generate_report()
        print(f"Report generated successfully: {file_path}")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()