# Kafka 电商场景最佳实践

本目录包含 Kafka 在电商场景下的最佳实践和配置示例。

## 目录结构

- `docker-compose.yml` - Kafka 集群 Docker Compose 配置文件
- `README.md` - 本文件，使用说明

## Kafka 集群配置说明

### 架构

本配置使用 **KRaft 模式**（Kafka Raft），无需 Zookeeper，包含：

- **3 个 Kafka Broker**：实现高可用性
- **Kafka UI**：可视化管理界面
- **Schema Registry**：Schema 管理（Avro/Protobuf）

### 端口映射

| 服务 | 容器端口 | 主机端口 | 说明 |
|------|---------|---------|------|
| kafka-1 | 9092 | 19092 | Broker 1 外部访问端口 |
| kafka-2 | 9092 | 19093 | Broker 2 外部访问端口 |
| kafka-3 | 9092 | 19094 | Broker 3 外部访问端口 |
| kafka-ui | 8080 | 8080 | Kafka UI 管理界面 |
| schema-registry | 8081 | 8081 | Schema Registry API |

### 关键配置

- **副本因子**：3（高可用）
- **最小同步副本**：2（允许 1 个 Broker 故障）
- **默认分区数**：3
- **数据保留**：7 天（168 小时）
- **集群 ID**：`MkU3OEVBNTcwNTJENDM2Qk`（所有 Broker 共享）

## 快速开始

### 1. 启动集群

```bash
# 在 WSL Ubuntu 中执行
cd ecommerce-practices
docker compose up -d
```

### 2. 检查服务状态

```bash
# 查看所有容器状态
docker compose ps

# 查看日志
docker compose logs -f kafka-1
```

### 3. 访问 Kafka UI

打开浏览器访问：http://localhost:8080

### 4. 验证集群

```bash
# 进入 Kafka 容器
docker exec -it kafka-1 bash

# 列出所有主题
kafka-topics.sh --bootstrap-server localhost:9092 --list

# 创建测试主题
kafka-topics.sh --bootstrap-server localhost:9092 \
  --create --topic test-topic \
  --partitions 3 \
  --replication-factor 3

# 查看主题详情
kafka-topics.sh --bootstrap-server localhost:9092 \
  --describe --topic test-topic
```

## 常用命令

### 主题管理

```bash
# 创建主题（电商订单事件）
docker exec -it kafka-1 kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --create --topic order-events \
  --partitions 6 \
  --replication-factor 3

# 列出所有主题
docker exec -it kafka-1 kafka-topics.sh \
  --bootstrap-server localhost:9092 --list

# 查看主题详情
docker exec -it kafka-1 kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --describe --topic order-events

# 删除主题
docker exec -it kafka-1 kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --delete --topic order-events
```

### 生产消息

```bash
# 使用控制台生产者
docker exec -it kafka-1 kafka-console-producer.sh \
  --bootstrap-server localhost:9092 \
  --topic order-events

# 输入消息（每行一条，Ctrl+C 退出）
# {"orderId":"ORD001","userId":"U123","amount":299.00}
```

### 消费消息

```bash
# 从最新位置消费
docker exec -it kafka-1 kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic order-events \
  --from-beginning

# 显示 Key 和 Value
docker exec -it kafka-1 kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic order-events \
  --from-beginning \
  --property print.key=true \
  --property print.timestamp=true
```

### 消费者组管理

```bash
# 列出所有消费者组
docker exec -it kafka-1 kafka-consumer-groups.sh \
  --bootstrap-server localhost:9092 --list

# 查看消费者组详情
docker exec -it kafka-1 kafka-consumer-groups.sh \
  --bootstrap-server localhost:9092 \
  --describe --group my-consumer-group

# 查看消费者 Lag
docker exec -it kafka-1 kafka-consumer-groups.sh \
  --bootstrap-server localhost:9092 \
  --describe --group my-consumer-group \
  --members --verbose
```

## 应用连接配置

### Java 应用配置

```properties
# bootstrap.servers
spring.kafka.bootstrap-servers=localhost:19092,localhost:19093,localhost:19094

# 或者使用容器内地址（如果应用也在 Docker 中）
spring.kafka.bootstrap-servers=kafka-1:9092,kafka-2:9092,kafka-3:9092
```

### Python 应用配置

```python
from kafka import KafkaProducer, KafkaConsumer

# 生产者
producer = KafkaProducer(
    bootstrap_servers=['localhost:19092', 'localhost:19093', 'localhost:19094']
)

# 消费者
consumer = KafkaConsumer(
    'order-events',
    bootstrap_servers=['localhost:19092', 'localhost:19093', 'localhost:19094'],
    group_id='order-processor'
)
```

## 电商场景主题示例

### 创建电商相关主题

```bash
# 订单事件
docker exec -it kafka-1 kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --create --topic order-events \
  --partitions 6 --replication-factor 3

# 支付事件
docker exec -it kafka-1 kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --create --topic payment-events \
  --partitions 6 --replication-factor 3

# 用户行为事件
docker exec -it kafka-1 kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --create --topic user-behavior-events \
  --partitions 12 --replication-factor 3

# 库存变更事件
docker exec -it kafka-1 kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --create --topic inventory-events \
  --partitions 3 --replication-factor 3
```

## 监控和运维

### 查看集群状态

```bash
# 查看 Broker 信息
docker exec -it kafka-1 kafka-broker-api-versions.sh \
  --bootstrap-server localhost:9092

# 查看集群 ID
docker exec -it kafka-1 kafka-metadata-shell.sh \
  --snapshot /var/lib/kafka/data/__cluster_metadata-0/00000000000000000000.log
```

### 日志查看

```bash
# 查看所有服务日志
docker compose logs -f

# 查看特定服务日志
docker compose logs -f kafka-1
docker compose logs -f kafka-ui
```

### 停止和清理

```bash
# 停止所有服务
docker compose down

# 停止并删除数据卷（谨慎使用，会删除所有数据）
docker compose down -v

# 重启服务
docker compose restart kafka-1
```

## 性能调优建议

### 生产环境配置

1. **增加分区数**：根据吞吐量需求调整
2. **调整 JVM 参数**：在 docker-compose.yml 中添加环境变量
3. **数据保留策略**：根据业务需求调整 `KAFKA_LOG_RETENTION_HOURS`
4. **压缩配置**：启用消息压缩（snappy、lz4、zstd）

### 资源限制

可以在 docker-compose.yml 中为每个服务添加资源限制：

```yaml
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 2G
    reservations:
      cpus: '1'
      memory: 1G
```

## 故障排查

### 容器无法启动

```bash
# 检查端口占用
netstat -tulpn | grep 19092

# 检查 Docker 日志
docker compose logs kafka-1
```

### 连接失败

1. 确认所有容器都在运行：`docker compose ps`
2. 检查网络连接：`docker network ls`
3. 验证端口映射是否正确

### 数据丢失

1. 检查副本因子配置
2. 确认 `min.insync.replicas` 设置
3. 查看 Broker 日志

## 安全配置

当前配置为开发环境，生产环境需要：

1. **启用 SASL/SSL 认证**
2. **配置 ACL 权限控制**
3. **使用加密传输**
4. **限制网络访问**

## 相关资源

- [Kafka 官方文档](https://kafka.apache.org/documentation/)
- [Kafka UI 文档](https://github.com/provectus/kafka-ui)
- [Schema Registry 文档](https://docs.confluent.io/platform/current/schema-registry/index.html)

## 下一步

- 配置电商业务主题
- 设置消息格式（Avro/Protobuf）
- 配置消费者组
- 实现监控告警

