import requests
import pandas as pd
import json
import time
import logging
import schedule
import os
import sys
from datetime import datetime
from typing import List, Dict, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

class WPushNotifier:
    """WPush微信推送类"""
    
    def __init__(self, config: Dict):
        self.config = config
        # 优先从环境变量读取配置，否则使用配置文件中的值，最后使用默认值
        self.api_key = os.getenv('WPUSH_API_KEY') or config.get('WPUSH_API_KEY', 'WPUSHVzfq5fznBbg9QFELrhqa5Jic9l9')
        self.topic_code = os.getenv('WPUSH_TOPIC_CODE') or config.get('WPUSH_TOPIC_CODE', 'jsl')
        self.send_api = os.getenv('WPUSH_SEND_API') or config.get('WPUSH_SEND_API', 'https://api.wpush.cn/api/v1/send')
        self.query_api = os.getenv('WPUSH_QUERY_API') or config.get('WPUSH_QUERY_API', 'https://api.wpush.cn/api/v1/query')
    
    def send_message(self, title: str, content: str, message_type: str = 'text') -> bool:
        """发送WPush消息"""
        try:
            # 根据API文档更新参数名称
            data = {
                'apikey': self.api_key,  # API文档中参数名为apikey而不是api_key
                'topic_code': self.topic_code,
                'title': title,
                'content': content,
                'type': message_type
            }
            
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.post(
                self.send_api, 
                json=data, 
                headers=headers, 
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 0:
                    logging.info("WPush消息发送成功")
                    return True
                else:
                    logging.error(f"WPush发送失败: {result.get('message', '未知错误')}")
                    return False
            else:
                logging.error(f"WPush请求失败，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            logging.error(f"WPush消息发送异常: {e}")
            return False
    
    def query_message_status(self, message_id: str) -> Dict:
        """查询消息状态"""
        try:
            params = {
                'apikey': self.api_key,  # API文档中参数名为apikey而不是api_key
                'message_id': message_id
            }
            
            response = requests.get(self.query_api, params=params, timeout=10)
            if response.status_code == 200:
                return response.json()
            return {}
        except Exception as e:
            logging.error(f"查询消息状态失败: {e}")
            return {}

class JisiluQDIIDataFetcher:
    """集思录QDII数据获取器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://www.jisilu.cn/data/qdii/',
            'X-Requested-With': 'XMLHttpRequest'
        }
        self.driver = None
        
    def setup_selenium(self, headless=True):
        """设置Selenium浏览器"""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')
        # 添加Chrome二进制路径和chromedriver路径以适应GitHub Actions环境
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-logging')
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--allow-running-insecure-content')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.binary_location = '/usr/bin/chromium-browser'
        
        # 使用Service类指定chromedriver路径（适用于Selenium 4.x）
        from selenium.webdriver.chrome.service import Service
        import os
        
        # 尝试不同的chromedriver路径
        chromedriver_paths = [
            '/usr/local/bin/chromedriver',
            '/usr/lib/chromium-browser/chromedriver',
            '/usr/bin/chromedriver'
        ]
        
        service = None
        for path in chromedriver_paths:
            if os.path.exists(path):
                service = Service(executable_path=path)
                break
        
        # 如果找到有效的chromedriver路径，则使用Service类
        if service:
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
        else:
            # 如果都不存在，则不指定路径，让系统自动查找
            self.driver = webdriver.Chrome(options=chrome_options)
        

    
    def get_commodity_data_from_selenium(self) -> List[Dict]:
        """通过Selenium获取商品LOF数据"""
        if not self.driver:
            self.setup_selenium(headless=True)
            
        try:
            self.driver.get("https://www.jisilu.cn/data/qdii/")
            time.sleep(5)
            
            table_data = []
            
            # 获取flex_qdiic表格数据
            try:
                # 等待页面加载完成
                wait = WebDriverWait(self.driver, 15)
                table_body_c = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "#flex_qdiic > tbody"))
                )
                
                # 获取表头信息
                headers_c = []
                header_elements_c = self.driver.find_elements(By.CSS_SELECTOR, "#flex_qdiic > thead th")
                for header in header_elements_c:
                    headers_c.append(header.text.strip())
                
                # 如果没有获取到表头，使用默认值
                if not headers_c:
                    headers_c = ['代码', '名称', '现价', '涨跌幅', '溢价率', '申购状态']
                
                # 获取表格行数据
                rows_c = table_body_c.find_elements(By.TAG_NAME, "tr")
                
                # 遍历每一行数据
                for row in rows_c:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    row_data = {}
                    
                    # 遍历每个单元格
                    for j, cell in enumerate(cells):
                        if j < len(headers_c):
                            header_name = headers_c[j]
                            cell_text = cell.text.strip()
                            row_data[header_name] = cell_text
                    
                    # 只添加非空行数据
                    if row_data:
                        table_data.append(row_data)
                        
                logging.info(f"通过Selenium获取到flex_qdiic表格 {len(rows_c)} 条商品LOF数据")
            except Exception as e:
                logging.error(f"Selenium获取flex_qdiic表格数据失败: {e}")
            
            # 获取flex_qdiie表格数据
            try:
                # 等待页面加载完成
                wait = WebDriverWait(self.driver, 15)
                table_body_e = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "#flex_qdiie > tbody"))
                )
                
                # 获取表头信息
                headers_e = []
                header_elements_e = self.driver.find_elements(By.CSS_SELECTOR, "#flex_qdiie > thead th")
                for header in header_elements_e:
                    headers_e.append(header.text.strip())
                
                # 如果没有获取到表头，使用默认值
                if not headers_e:
                    headers_e = ['代码', '名称', '现价', '涨跌幅', '溢价率', '申购状态']
                
                # 获取表格行数据
                rows_e = table_body_e.find_elements(By.TAG_NAME, "tr")
                
                # 遍历每一行数据
                for row in rows_e:
                    cells = row.find_elements(By.TAG_NAME, "td")
                    row_data = {}
                    
                    # 遍历每个单元格
                    for j, cell in enumerate(cells):
                        if j < len(headers_e):
                            header_name = headers_e[j]
                            cell_text = cell.text.strip()
                            row_data[header_name] = cell_text
                    
                    # 只添加非空行数据
                    if row_data:
                        table_data.append(row_data)
                        
                logging.info(f"通过Selenium获取到flex_qdiie表格 {len(rows_e)} 条商品LOF数据")
            except Exception as e:
                logging.error(f"Selenium获取flex_qdiie表格数据失败: {e}")
            
            logging.info(f"通过Selenium总共获取到 {len(table_data)} 条商品LOF数据")
            return table_data
            
        except Exception as e:
            logging.error(f"Selenium获取商品数据失败: {e}")
            return []
    
    def parse_premium_rate(self, premium_str: str) -> float:
        """解析溢价率字符串为浮点数"""
        if not premium_str or premium_str == '-':
            return 0.0
        
        try:
            premium_str = premium_str.replace('%', '').strip()
            return float(premium_str)
        except ValueError:
            return 0.0
    
    def get_all_lof_funds_sorted(self) -> List[Dict]:
        """获取所有LOF基金并按溢价率排序"""
        all_funds = []
        
        commodity_data = self.get_commodity_data_from_selenium()
        for fund in commodity_data:
            fund_name = str(fund.get('名称', ''))
            if 'LOF' in fund_name.upper():
                code = fund.get('代码', '')
                existing_codes = [f['代码'] for f in all_funds]
                
                if code not in existing_codes:
                    premium_str = fund.get('溢价率', fund.get('T-1溢价率', '0%'))
                    premium_rate = self.parse_premium_rate(premium_str)
                    
                    fund_data = {
                        '代码': code,
                        '名称': fund_name,
                        'T-1溢价率': f"{premium_rate}%",
                        '溢价率数值': premium_rate,
                        '申购状态': fund.get('申购状态', '未知'),
                        '数据来源': 'Selenium',
                        '更新时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    all_funds.append(fund_data)
        
        all_funds.sort(key=lambda x: x['溢价率数值'], reverse=True)
        
        for fund in all_funds:
            fund.pop('溢价率数值', None)
        
        return all_funds
    
    def close(self):
        """关闭资源"""
        if self.driver:
            self.driver.quit()

class QDIIMonitor:
    """QDII数据监控主程序"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.fetcher = JisiluQDIIDataFetcher()
        self.notifier = WPushNotifier(config)
        
        # 处理Windows系统上的编码问题
        if sys.platform.startswith('win'):
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler('qdii_wpush.log', encoding='utf-8'),
                    logging.StreamHandler(sys.stdout)
                ]
            )
        else:
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler('qdii_wpush.log', encoding='utf-8'),
                    logging.StreamHandler(sys.stdout)
                ]
            )
        self.logger = logging.getLogger(__name__)
    
    def format_wpush_message(self, fund_data: List[Dict]) -> str:
        """格式化WPush推送消息"""
        if not fund_data:
            return "暂无LOF基金数据"
        
        # 修改为显示全部基金，只保留指定的四列数据
        message = "📊 LOF基金溢价率监控报告\n\n"
        message += f"统计时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        message += f"监控基金数量: {len(fund_data)} 只\n\n"
        
        # 使用Markdown表格格式
        message += "| 代码 | 名称 | 溢价率 | 限额 |\n"
        message += "| --- | --- | --- | --- |\n"
        
        # 显示所有基金数据，每个栏目在同一行
        for fund in fund_data:
            code = fund.get('代码', 'N/A')
            # 删除基金名称中的LOF字段
            name = fund.get('名称', 'N/A').replace('LOF', '').strip()
            premium = fund.get('T-1溢价率', 'N/A')
            limit = fund.get('申购状态', '未知')
            
            # 使用Markdown表格格式输出
            message += f"| {code} | {name} | {premium} | {limit} |\n"
        
        # 添加统计信息
        high_premium = len([f for f in fund_data if self.parse_premium_value(f.get('T-1溢价率', '0%')) > 2])
        message += f"\n📈 高溢价基金(>2%): {high_premium} 只"
        
        return message
    
    def parse_premium_value(self, premium_str: str) -> float:
        """解析溢价率数值"""
        try:
            return float(premium_str.replace('%', ''))
        except:
            return 0.0
    
    def monitor_task(self):
        """监控任务"""
        self.logger.info("开始执行LOF基金监控任务")
        
        try:
            sorted_funds = self.fetcher.get_all_lof_funds_sorted()
            
            if sorted_funds:
                self.logger.info(f"获取到 {len(sorted_funds)} 只LOF基金")
                
                message = self.format_wpush_message(sorted_funds)
                title = f"LOF基金监控({len(sorted_funds)}只)"
                
                success = self.notifier.send_message(title, message)
                
                if success:
                    self.logger.info("WPush推送成功")
                    self.save_monitor_data(sorted_funds)
                else:
                    self.logger.error("WPush推送失败")
            else:
                self.logger.warning("未获取到LOF基金数据")
                # 发送错误通知
                error_msg = "❌ LOF基金数据获取失败，请检查网络或网站状态"
                self.notifier.send_message("监控异常", error_msg)
                
        except Exception as e:
            self.logger.error(f"监控任务执行失败: {e}")
            error_msg = f"监控任务异常: {str(e)}"
            self.notifier.send_message("系统异常", error_msg)
        finally:
            self.fetcher.close()
    
    def save_monitor_data(self, fund_data: List[Dict]):
        """保存监控数据"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"monitor_data_{timestamp}.json"
            
            data = {
                'timestamp': timestamp,
                'fund_count': len(fund_data),
                'funds': fund_data
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"监控数据已保存: {filename}")
        except Exception as e:
            self.logger.error(f"保存数据失败: {e}")
    
    def setup_schedule(self):
        """设置定时任务"""
        # 交易日定时监控（每30分钟）
        schedule.every(30).minutes.during("09:30", "15:00").do(self.monitor_task)
        
        # 重要时间点监控
        schedule.every().day.at("09:25").do(self.monitor_task)  # 开盘前
        schedule.every().day.at("11:30").do(self.monitor_task)  # 午间
        schedule.every().day.at("15:00").do(self.monitor_task)  # 收盘
        
        self.logger.info("定时任务设置完成")
    
    def run_once(self):
        """立即执行一次"""
        self.monitor_task()
    
    def run_scheduled(self):
        """运行定时监控"""
        self.setup_schedule()
        self.logger.info("LOF基金WPush监控系统启动")
        
        # 启动时立即执行一次
        self.monitor_task()
        
        while True:
            schedule.run_pending()
            time.sleep(60)
    
    def test_wpush(self):
        """测试WPush推送"""
        test_message = "🔔 LOF基金监控系统测试\\n\\n"
        test_message += "📅 测试时间: {}\\n".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        test_message += "✅ 这是一条测试消息，用于验证WPush推送功能正常。"
        
        success = self.notifier.send_message("监控系统测试", test_message)
        if success:
            self.logger.info("WPush测试消息发送成功")
        else:
            self.logger.error("WPush测试消息发送失败")
        
        return success

def load_config():
    """加载配置"""
    return {
        # WPush配置
        'WPUSH_API_KEY': 'WPUSHVzfq5fznBbg9QFELrhqa5Jic9l9',
        'WPUSH_TOPIC_CODE': 'jsl',
        'WPUSH_SEND_API': 'https://api.wpush.cn/api/v1/send',
        'WPUSH_QUERY_API': 'https://api.wpush.cn/api/v1/query',
        
        # 监控设置
        'headless': True,
        'monitor_interval': 30
    }

def main():
    """主函数"""
    print("集思录QDII数据WPush监控系统")
    print("=" * 50)
    
    config = load_config()
    monitor = QDIIMonitor(config)
    
    # 直接执行一次监控任务，无需交互式选择
    print("立即执行监控任务...")
    monitor.run_once()

if __name__ == "__main__":
    main()
