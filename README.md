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
在 `.github/workflows/` 目录下创建 `qdii-monitor.yml` 文件，内容如下：

```yaml
name: QDII LOF Fund Monitor

on:
  schedule:
    # 周一到周五 早上九点半 (UTC时间1:30，对应北京时间9:30)
    - cron: '30 1 * * 1-5'
    # 周一到周五 下午一点 (UTC时间5:00，对应北京时间13:00)
    - cron: '0 5 * * 1-5'
    # 周一到周五 下午两点 (UTC时间6:00，对应北京时间14:00)
    - cron: '0 6 * * 1-5'
    # 周一到周五 下午四点 (UTC时间8:00，对应北京时间16:00)
    - cron: '0 8 * * 1-5'
  workflow_dispatch: # 允许手动触发

jobs:
  monitor:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Install Chrome
      run: |
        sudo apt-get update
        sudo apt-get install -y chromium-browser chromium-chromedriver
        # 安全地创建符号链接，如果已存在则先删除
        sudo rm -f /usr/local/bin/chromedriver
        sudo rm -f /usr/bin/google-chrome
        sudo ln -s /usr/lib/chromium-browser/chromedriver /usr/local/bin/chromedriver
        sudo ln -s /usr/bin/chromium-browser /usr/bin/google-chrome
    
    - name: Run QDII Monitor
      env:
        WPUSH_API_KEY: ${{ secrets.WPUSH_API_KEY }}
        WPUSH_TOPIC_CODE: ${{ secrets.WPUSH_TOPIC_CODE }}
      run: |
        python 7.py
```

### GitHub Actions 环境说明

GitHub Actions使用Ubuntu环境运行此工作流，系统中预装了chromium-browser和chromium-chromedriver。工作流中的安装步骤会确保Chrome浏览器和驱动程序正确配置。

如果遇到"File exists"错误，工作流会先删除已存在的符号链接再重新创建，以确保环境配置正确。

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