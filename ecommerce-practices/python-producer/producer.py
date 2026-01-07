#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
电商场景 Kafka 生产者示例
模拟发送订单事件到 Kafka
"""

import json
import time
import random
from datetime import datetime
from kafka import KafkaProducer
from kafka.errors import KafkaError


class OrderEventProducer:
    """订单事件生产者"""
    
    def __init__(self, bootstrap_servers):
        """
        初始化 Kafka 生产者
        
        Args:
            bootstrap_servers: Kafka 服务器地址，格式: 'host:port,host:port'
        """
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None,
            # 配置选项
            acks='all',  # 等待所有副本确认
            retries=3,   # 重试次数
            batch_size=16384,  # 批量发送大小
            linger_ms=10,  # 等待时间（毫秒）
        )
        self.topic = 'order-events'
    
    def create_order_event(self, order_id, user_id, amount, product_id=None):
        """
        创建订单事件
        
        Args:
            order_id: 订单ID
            user_id: 用户ID
            amount: 订单金额
            product_id: 商品ID（可选）
        
        Returns:
            dict: 订单事件数据
        """
        event = {
            'orderId': order_id,
            'userId': user_id,
            'amount': amount,
            'productId': product_id or f'PROD{random.randint(1000, 9999)}',
            'eventType': 'ORDER_CREATED',
            'timestamp': datetime.now().isoformat(),
            'paymentMethod': random.choice(['alipay', 'wechat', 'credit_card']),
        }
        return event
    
    def send_order_event(self, order_id, user_id, amount, product_id=None):
        """
        发送订单事件到 Kafka
        
        Args:
            order_id: 订单ID
            user_id: 用户ID
            amount: 订单金额
            product_id: 商品ID（可选）
        
        Returns:
            Future: Kafka 发送结果
        """
        event = self.create_order_event(order_id, user_id, amount, product_id)
        
        # 使用 order_id 作为 key，确保同一订单的消息发送到同一分区
        future = self.producer.send(
            self.topic,
            key=order_id,
            value=event
        )
        
        return future
    
    def send_batch_events(self, count=10):
        """
        批量发送订单事件
        
        Args:
            count: 发送的事件数量
        """
        print(f"开始发送 {count} 条订单事件...")
        
        for i in range(count):
            order_id = f'ORD{datetime.now().strftime("%Y%m%d")}{i+1:04d}'
            user_id = f'U{random.randint(1000, 9999)}'
            amount = round(random.uniform(10.0, 1000.0), 2)
            
            try:
                future = self.send_order_event(order_id, user_id, amount)
                # 等待发送结果
                record_metadata = future.get(timeout=10)
                print(f"✓ [{i+1}/{count}] 订单事件已发送: {order_id} -> "
                      f"Topic: {record_metadata.topic}, "
                      f"Partition: {record_metadata.partition}, "
                      f"Offset: {record_metadata.offset}")
                
                # 模拟真实场景，稍微延迟
                time.sleep(0.1)
                
            except KafkaError as e:
                print(f"✗ 发送失败: {order_id}, 错误: {e}")
        
        # 确保所有消息都发送完成
        self.producer.flush()
        print(f"\n所有事件发送完成！")
    
    def close(self):
        """关闭生产者"""
        self.producer.close()


def main():
    """主函数"""
    # Kafka 服务器地址（根据你的 docker-compose 配置）
    # 如果在 WSL 中运行，使用 localhost
    # 如果在 Windows 中运行，可能需要使用 WSL 的 IP 地址
    bootstrap_servers = [
        'localhost:19092',
        'localhost:19093',
        'localhost:19094'
    ]
    
    print("=" * 60)
    print("电商场景 Kafka 生产者示例")
    print("=" * 60)
    print(f"Kafka 服务器: {bootstrap_servers}")
    print(f"主题: order-events")
    print("=" * 60)
    print()
    
    # 创建生产者
    producer = OrderEventProducer(bootstrap_servers)
    
    try:
        # 发送 10 条测试事件
        producer.send_batch_events(count=10)
        
    except Exception as e:
        print(f"发生错误: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 关闭生产者
        producer.close()
        print("\n生产者已关闭")


if __name__ == '__main__':
    main()

