# coding=utf-8
"""
推送系统

支持多渠道推送：
1. 微信（通过Server酱/企业微信机器人）
2. 邮件（SMTP）
3. Webhook（自定义接口）
4. Telegram Bot
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from datetime import datetime
from dataclasses import dataclass
import json


@dataclass
class AlertMessage:
    """预警消息"""
    title: str
    content: str
    stock_code: str
    stock_name: str
    alert_type: str
    timestamp: datetime
    priority: str = 'normal'  # normal, high, urgent
    
    def to_text(self) -> str:
        """转换为文本格式"""
        return f"""
【{self.title}】

股票: {self.stock_name} ({self.stock_code})
类型: {self.alert_type}
时间: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}

{self.content}

---
来自 pytdx2 异动预警系统
""".strip()
    
    def to_markdown(self) -> str:
        """转换为Markdown格式"""
        return f"""
# {self.title}

**股票**: {self.stock_name} ({self.stock_code})  
**类型**: {self.alert_type}  
**时间**: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}

{self.content}

---
_来自 pytdx2 异动预警系统_
""".strip()


class Pusher(ABC):
    """推送器基类"""
    
    @abstractmethod
    def push(self, message: AlertMessage) -> bool:
        """推送消息"""
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """测试连接"""
        pass


class WeChatPusher(Pusher):
    """微信推送器（通过Server酱）"""
    
    def __init__(self, send_key: str):
        """
        Args:
            send_key: Server酱的SendKey
        """
        self.send_key = send_key
        self.api_url = f"https://sctapi.ftqq.com/{send_key}.send"
    
    def push(self, message: AlertMessage) -> bool:
        """推送消息到微信"""
        try:
            data = {
                'title': message.title,
                'desp': message.to_markdown()
            }
            
            response = requests.post(self.api_url, data=data, timeout=10)
            result = response.json()
            
            return result.get('code') == 0
        except Exception as e:
            print(f"微信推送失败: {e}")
            return False
    
    def test_connection(self) -> bool:
        """测试连接"""
        try:
            test_msg = AlertMessage(
                title="测试消息",
                content="这是一条测试消息",
                stock_code="000000",
                stock_name="测试",
                alert_type="test",
                timestamp=datetime.now()
            )
            return self.push(test_msg)
        except:
            return False


class WeChatWorkPusher(Pusher):
    """企业微信机器人推送器"""
    
    def __init__(self, webhook_url: str):
        """
        Args:
            webhook_url: 企业微信机器人的Webhook地址
        """
        self.webhook_url = webhook_url
    
    def push(self, message: AlertMessage) -> bool:
        """推送消息到企业微信"""
        try:
            data = {
                "msgtype": "markdown",
                "markdown": {
                    "content": message.to_markdown()
                }
            }
            
            response = requests.post(
                self.webhook_url,
                json=data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            result = response.json()
            
            return result.get('errcode') == 0
        except Exception as e:
            print(f"企业微信推送失败: {e}")
            return False
    
    def test_connection(self) -> bool:
        """测试连接"""
        try:
            test_msg = AlertMessage(
                title="测试消息",
                content="这是一条测试消息",
                stock_code="000000",
                stock_name="测试",
                alert_type="test",
                timestamp=datetime.now()
            )
            return self.push(test_msg)
        except:
            return False


class EmailPusher(Pusher):
    """邮件推送器"""
    
    def __init__(
        self,
        smtp_server: str,
        smtp_port: int,
        username: str,
        password: str,
        from_addr: str,
        to_addrs: List[str]
    ):
        """
        Args:
            smtp_server: SMTP服务器地址
            smtp_port: SMTP端口
            username: 用户名
            password: 密码
            from_addr: 发件人地址
            to_addrs: 收件人地址列表
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.from_addr = from_addr
        self.to_addrs = to_addrs
    
    def push(self, message: AlertMessage) -> bool:
        """发送邮件"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = message.title
            msg['From'] = self.from_addr
            msg['To'] = ', '.join(self.to_addrs)
            
            # 纯文本版本
            text_part = MIMEText(message.to_text(), 'plain', 'utf-8')
            msg.attach(text_part)
            
            # HTML版本
            html_content = f"""
            <html>
            <body>
            <h2>{message.title}</h2>
            <p><strong>股票</strong>: {message.stock_name} ({message.stock_code})</p>
            <p><strong>类型</strong>: {message.alert_type}</p>
            <p><strong>时间</strong>: {message.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
            <hr>
            <p>{message.content.replace(chr(10), '<br>')}</p>
            <hr>
            <p><em>来自 pytdx2 异动预警系统</em></p>
            </body>
            </html>
            """
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # 发送邮件
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
                server.sendmail(self.from_addr, self.to_addrs, msg.as_string())
            
            return True
        except Exception as e:
            print(f"邮件发送失败: {e}")
            return False
    
    def test_connection(self) -> bool:
        """测试连接"""
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.username, self.password)
            return True
        except:
            return False


class WebhookPusher(Pusher):
    """Webhook推送器"""
    
    def __init__(self, webhook_url: str, headers: Optional[Dict[str, str]] = None):
        """
        Args:
            webhook_url: Webhook地址
            headers: 自定义请求头
        """
        self.webhook_url = webhook_url
        self.headers = headers or {}
    
    def push(self, message: AlertMessage) -> bool:
        """推送到Webhook"""
        try:
            data = {
                'title': message.title,
                'content': message.content,
                'stock_code': message.stock_code,
                'stock_name': message.stock_name,
                'alert_type': message.alert_type,
                'timestamp': message.timestamp.isoformat(),
                'priority': message.priority
            }
            
            response = requests.post(
                self.webhook_url,
                json=data,
                headers=self.headers,
                timeout=10
            )
            
            return response.status_code == 200
        except Exception as e:
            print(f"Webhook推送失败: {e}")
            return False
    
    def test_connection(self) -> bool:
        """测试连接"""
        try:
            response = requests.get(self.webhook_url, timeout=5)
            return response.status_code < 500
        except:
            return False


class PusherManager:
    """推送器管理器"""
    
    def __init__(self):
        self.pushers: Dict[str, Pusher] = {}
    
    def add_pusher(self, name: str, pusher: Pusher):
        """添加推送器"""
        self.pushers[name] = pusher
    
    def remove_pusher(self, name: str):
        """移除推送器"""
        if name in self.pushers:
            del self.pushers[name]
    
    def push_to_channels(
        self,
        message: AlertMessage,
        channels: List[str]
    ) -> Dict[str, bool]:
        """推送到指定渠道"""
        results = {}
        
        for channel in channels:
            if channel in self.pushers:
                try:
                    success = self.pushers[channel].push(message)
                    results[channel] = success
                except Exception as e:
                    print(f"推送失败 [{channel}]: {e}")
                    results[channel] = False
            else:
                print(f"推送器不存在: {channel}")
                results[channel] = False
        
        return results
    
    def push_to_all(self, message: AlertMessage) -> Dict[str, bool]:
        """推送到所有渠道"""
        return self.push_to_channels(message, list(self.pushers.keys()))
