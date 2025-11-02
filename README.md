# QDII LOF基金监控系统

这是一个基于集思录网站数据的QDII LOF基金溢价率监控系统，能够定时获取基金数据并通过WPush推送至微信。

## 功能特点

- 自动抓取集思录QDII LOF基金数据
- 计算并排序基金溢价率
- 通过WPush将结果推送至微信
- 支持GitHub Actions定时执行

## 本地运行

```bash
python 7.py
```

## GitHub Actions 配置

### 1. 创建工作流目录
在项目根目录下创建以下目录结构：
```
.github/
└── workflows/
```

### 2. 创建工作流文件
在 `.github/workflows/` 目录下创建 `qdii-monitor.yml` 文件，内容如上所示。

### 3. 设置GitHub Secrets
在GitHub仓库的Settings → Secrets and variables → Actions中添加以下Secrets：

- `WPUSH_API_KEY`: 你的WPush API密钥
- `WPUSH_TOPIC_CODE`: 你的WPush主题代码

## 依赖安装

```bash
pip install -r requirements.txt
```

## 配置说明

可以通过环境变量或修改 `load_config()` 函数来配置以下参数：

- `WPUSH_API_KEY`: WPush API密钥
- `WPUSH_TOPIC_CODE`: WPush主题代码

## 文件说明

- `7.py`: 主程序文件
- `requirements.txt`: 依赖包列表
- `qdii_wpush.log`: 日志文件
- `monitor_data_*.json`: 监控数据保存文件