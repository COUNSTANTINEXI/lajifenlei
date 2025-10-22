# 🗂️ 智能垃圾分类系统

一个基于 Flask 构建的智能垃圾分类系统，支持文本识别、图片识别、规则管理和数据统计分析。

## ✨ 功能特性

- **🔍 文本分类**：输入物品名称，快速识别垃圾类型
- **📸 图片识别**：上传图片，智能识别垃圾分类
- **⚙️ 规则管理**：灵活管理垃圾分类规则，支持增删改查
- **📊 统计分析**：可视化展示垃圾分类数据统计
- **🚀 批量处理**：支持批量分类多个物品
- **📱 响应式设计**：完美适配各种设备和屏幕尺寸
- **📖 API 文档**：自动生成的 Swagger API 文档

## 🎯 垃圾分类类型

系统支持四种垃圾分类：

- **可回收垃圾** 🔄：塑料瓶、纸箱、玻璃瓶、易拉罐等
- **有害垃圾** ☢️：电池、灯管、药品、油漆等
- **厨余垃圾** 🍎：果皮、剩菜、茶叶渣等
- **其他垃圾** 🗑️：烟头、陶瓷、卫生纸等

## 📋 系统要求

- Python 3.7 或更高版本
- pip（Python 包管理器）
- 推荐使用虚拟环境

## 🚀 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/COUNSTANTINEXI/lajifenlei.git
cd lajifenlei
```

### 2. 创建虚拟环境（推荐）

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 运行应用

```bash
python run.py
```

### 5. 访问应用

打开浏览器访问：

- **Web 界面**：http://localhost:5000
- **API 文档**：http://localhost:5000/apidocs/

## 🔧 配置说明

### 环境变量

可以通过环境变量自定义配置：

```bash
# 运行环境（development/production/testing）
set FLASK_CONFIG=development

# 服务器地址
set FLASK_HOST=localhost

# 服务器端口
set FLASK_PORT=5000

```

### 配置文件

编辑 `config.py` 可以修改更多配置：

- `MAX_CONTENT_LENGTH`：上传文件大小限制（默认 16MB）
- `DATA_FILE`：垃圾分类规则数据文件路径

## 📚 API 接口

系统提供 RESTful API 接口，详细文档请访问 http://localhost:5000/apidocs/

### 主要接口

#### 1. 文本分类

```http
GET /api/classify?item=塑料瓶
```

**响应示例：**

```json
{
  "item_name": "塑料瓶",
  "garbage_type": "可回收垃圾",
  "reason": "塑料材质可回收再利用",
  "timestamp": "2025-10-22 10:30:45"
}
```

#### 2. 批量分类

```http
POST /api/classify/batch
Content-Type: application/json

{
  "items": ["塑料瓶", "电池", "苹果核"]
}
```

#### 3. 图片识别

```http
POST /api/classify/image
Content-Type: multipart/form-data

image: [图片文件]
confidence_threshold: 10
```

#### 4. 规则管理

```http
# 获取所有规则
GET /api/rules

# 添加规则
POST /api/rules

# 更新规则
PUT /api/rules

# 删除规则
DELETE /api/rules?item=物品名称
```

#### 5. 统计分析

```http
GET /api/statistics
```

## 🗂️ 项目结构

```
lajifenlei/
│
├── app/                        # 应用主目录
│   ├── __init__.py            # Flask 应用工厂
│   ├── models/                # 数据模型
│   │   ├── classifier.py      # 分类器模型
│   │   └── data_manager.py    # 数据管理
│   ├── routes/                # 路由模块
│   │   ├── api.py            # API 路由
│   │   └── main.py           # 主路由
│   ├── services/              # 服务层
│   │   └── image_classifier.py # 图片识别服务
│   └── static/                # 静态文件
│       ├── index.html         # 前端页面
│       └── app.js            # 前端脚本
│
├── config.py                  # 配置文件
├── run.py                     # 应用启动脚本
├── requirements.txt           # 项目依赖
├── garbage_rules.csv          # 垃圾分类规则数据
└── README.md                  # 项目说明文档
```

## 🎨 使用说明

### Web 界面使用

1. **文本分类**
   - 在输入框中输入物品名称
   - 点击"分类"按钮或按回车键
   - 查看分类结果和依据

2. **图片识别**
   - 切换到"图片识别"标签页
   - 点击上传区域或拖拽图片
   - 调整置信度阈值
   - 点击"开始识别"按钮

3. **批量分类**
   - 点击"批量分类"按钮
   - 每行输入一个物品名称
   - 点击"开始分类"查看结果

4. **规则管理**
   - 导航栏选择"规则管理"
   - 可以添加、编辑、删除分类规则
   - 支持搜索和筛选

5. **统计分析**
   - 导航栏选择"统计分析"
   - 查看各类垃圾的数量统计
   - 查看可视化图表

### API 调用示例

#### Python 示例

```python
import requests

# 文本分类
response = requests.get('http://localhost:5000/api/classify', 
                       params={'item': '塑料瓶'})
print(response.json())

# 批量分类
response = requests.post('http://localhost:5000/api/classify/batch',
                        json={'items': ['塑料瓶', '电池', '苹果核']})
print(response.json())

# 图片识别
with open('garbage.jpg', 'rb') as f:
    files = {'image': f}
    data = {'confidence_threshold': 10}
    response = requests.post('http://localhost:5000/api/classify/image',
                           files=files, data=data)
    print(response.json())
```

#### JavaScript 示例

```javascript
// 文本分类
fetch('/api/classify?item=塑料瓶')
  .then(response => response.json())
  .then(data => console.log(data));

// 批量分类
fetch('/api/classify/batch', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({items: ['塑料瓶', '电池', '苹果核']})
})
  .then(response => response.json())
  .then(data => console.log(data));
```

## 📦 依赖说明

主要依赖包：

- **Flask 2.3.3**：Web 框架
- **Flask-CORS 4.0.0**：跨域支持
- **Flask-RESTful 0.3.10**：RESTful API 支持
- **Flasgger 0.9.7.1**：Swagger API 文档
- **Pillow 10.0.0**：图像处理
- **NumPy 1.24.3**：数值计算
- **Gunicorn 21.2.0**：生产服务器

可选依赖（图像识别增强功能）：

- PyTorch
- TorchVision
- Transformers

## 🚀 生产部署

### 使用 Gunicorn

```bash
# 设置生产环境
set FLASK_CONFIG=production

# 启动 Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app('production')"
```

### 使用 Docker（可选）

```dockerfile
# 创建 Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

ENV FLASK_CONFIG=production
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:create_app('production')"]
```

## 🧪 测试

```bash
# 设置测试环境
set FLASK_CONFIG=testing

# 运行测试（需要先安装 pytest）
pytest
```

## 📝 数据管理

### 自定义分类规则

编辑 `garbage_rules.csv` 文件，格式如下：

```csv
物品名称,垃圾类型,分类依据
塑料瓶,可回收垃圾,塑料材质可回收再利用
电池,有害垃圾,含有害物质需特殊处理
苹果核,厨余垃圾,易腐烂的有机物
烟头,其他垃圾,难以回收且污染环境
```

### 通过 API 管理

也可以通过 Web 界面或 API 接口在线管理规则。

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📮 联系方式

如有问题或建议，欢迎通过以下方式联系：

- 提交 Issue：[GitHub Issues](https://github.com/COUNSTANTINEXI/lajifenlei/issues)
- Email：zhou_su@126.com
## 🙏 致谢

感谢所有为垃圾分类事业做出贡献的开发者！

---

**让我们一起为环保事业贡献力量！** 🌍💚

