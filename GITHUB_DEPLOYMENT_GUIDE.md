# GitHub 部署指南

本指南将帮助您将QDII LOF基金监控系统部署到GitHub仓库并配置GitHub Actions。

## 第一步：在GitHub上创建仓库

1. 登录您的GitHub账户
2. 点击右上角的"+"号，选择"New repository"
3. 输入仓库名称（例如：qdii-monitor）
4. 选择仓库为Public（公开）或Private（私有）
5. 不要初始化README、.gitignore或license
6. 点击"Create repository"

## 第二步：配置本地仓库与GitHub仓库的连接

1. 复制新创建仓库的HTTPS或SSH URL
   - HTTPS示例：`https://github.com/yourusername/qdii-monitor.git`
   - SSH示例：`git@github.com:yourusername/qdii-monitor.git`

2. 在本地qdii目录中打开终端，执行以下命令：
   ```bash
   # 添加远程仓库地址
   git remote add origin YOUR_REPOSITORY_URL
   
   # 验证远程仓库是否添加成功
   git remote -v
   ```

## 第三步：推送代码到GitHub

```bash
# 推送master分支到GitHub
git push -u origin master
```

## 第四步：配置GitHub Secrets

为了使GitHub Actions能够正常工作，您需要配置以下Secrets：

1. 进入GitHub仓库页面
2. 点击"Settings"选项卡
3. 在左侧菜单中点击"Secrets and variables" → "Actions"
4. 点击"New repository secret"按钮
5. 添加以下两个Secrets：
   - Name: `WPUSH_API_KEY`
     Value: 您的WPush API密钥
   - Name: `WPUSH_TOPIC_CODE`
     Value: 您的WPush主题代码

## 第五步：验证GitHub Actions

1. 在GitHub仓库页面，点击"Actions"选项卡
2. 您应该能看到"QDII LOF Fund Monitor"工作流
3. 工作流将按照以下时间自动运行：
   - 周一到周五 早上九点半 (北京时间)
   - 周一到周五 下午一点 (北京时间)
   - 周一到周五 下午两点 (北京时间)
   - 周一到周五 下午四点 (北京时间)

您也可以通过点击"Run workflow"按钮手动触发工作流进行测试。

## 故障排除

如果遇到问题，请检查：

1. GitHub Secrets是否正确配置
2. 网络连接是否正常
3. GitHub Actions日志中的错误信息