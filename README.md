# 太空育种基因轨迹纪要系统

面向太空育种实验记录会议的基因轨迹纪要全栈系统，集成音频处理、语音识别、AI分析和报告生成功能。

## 项目结构

```
auto101/
├── frontend/                          # 前端 React 应用
│   ├── src/
│   │   ├── components/                # React 组件
│   │   │   ├── Layout.tsx            # 布局组件
│   │   │   ├── Dashboard.tsx         # 总览仪表盘
│   │   │   ├── PhenotypeComparison.tsx  # 表型对比图
│   │   │   ├── MeetingList.tsx       # 会议列表
│   │   │   ├── MeetingDetail.tsx     # 会议详情
│   │   │   ├── AudioUpload.tsx       # 音频上传
│   │   │   └── ReportViewer.tsx      # 报告查看
│   │   ├── types/
│   │   │   └── index.ts              # TypeScript 类型定义
│   │   ├── main.tsx                  # 应用入口
│   │   ├── App.tsx                   # 路由配置
│   │   └── index.css                 # 全局样式
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── tsconfig.json
└── backend/                           # 后端 FastAPI 应用
    ├── app/
    │   ├── core/                     # 核心配置
    │   │   ├── config.py             # 配置管理
    │   │   └── database.py           # 数据库连接
    │   ├── models/                   # 数据模型
    │   │   ├── schemas.py            # Pydantic 模型
    │   │   └── db_models.py          # SQLAlchemy 模型
    │   ├── services/                 # 业务服务
    │   │   ├── audio_processor.py    # librosa 噪声过滤
    │   │   ├── transcriber.py        # Whisper 语音识别
    │   │   ├── speaker_diarization.py # pyannote 说话人分离
    │   │   ├── ai_analyzer.py        # OpenAI 摘要生成
    │   │   ├── email_sender.py       # smtplib 邮件发送
    │   │   ├── germplasm_syncer.py   # 种质库同步
    │   │   └── meeting_processor.py  # 会议处理编排
    │   ├── routers/                  # API 路由
    │   │   ├── phenotype.py          # 表型数据接口
    │   │   ├── meetings.py           # 会议管理接口
    │   │   ├── reports.py            # 报告管理接口
    │   │   └── upload.py             # 文件上传接口
    │   └── main.py                   # 应用入口
    ├── data/
    │   ├── uploads/                  # 上传文件目录
    │   ├── processed/                # 处理后文件目录
    │   └── reports/                  # 生成报告目录
    ├── requirements.txt
    ├── .env.example
    └── run.py
```

## 功能特性

### 1. 前端功能
- **表型对比分析**：柱状图展示地面对照与太空飞行组的性状对比
- **雷达图分析**：多维度展示突变影响幅度和显著性
- **会议管理**：会议列表、详情查看、对话记录展示
- **音频上传**：支持拖拽上传，实时显示处理进度
- **报告查看**：Markdown 格式报告预览、下载、邮件发送状态

### 2. 后端功能
- **librosa 噪声过滤**：谱减法去除实验室通风等背景噪声
- **Whisper 语音识别**：识别中文语音，自动提取基因位点和性状术语
- **pyannote 说话人分离**：基于内容关键词区分分子生物学家和园艺师
- **OpenAI 智能分析**：
  - 会议摘要生成
  - 诱变效应深度分析
  - 后代筛选策略制定
- **smtplib 邮件发送**：HTML 格式邮件，附带 Markdown 附件
- **种质库同步**：API 方式同步至国家作物种质库

## 快速开始

### 后端启动

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
copy .env.example .env  # 配置 API 密钥
python run.py
```

后端服务将在 http://localhost:8000 启动，API 文档：http://localhost:8000/docs

### 前端启动

```bash
cd frontend
npm install
npm run dev
```

前端应用将在 http://localhost:5173 启动

## 处理流程

1. **音频上传**：用户上传会议录音
2. **噪声过滤**：librosa 去除背景噪声
3. **语音识别**：Whisper 转录语音为文字
4. **术语提取**：正则匹配提取基因位点（如 Chr5:128456789）和性状术语
5. **说话人分离**：pyannote 区分不同发言人
6. **角色识别**：基于关键词区分分子生物学家和园艺师
7. **AI 分析**：OpenAI 生成摘要、诱变效应分析、筛选策略
8. **报告生成**：自动生成 Markdown 格式会议纪要
9. **邮件发送**：通过 smtplib 发送给项目组成员
10. **种质库同步**：同步至国家作物种质库

## API 接口

- `GET /api/phenotype` - 获取表型数据
- `POST /api/upload/audio` - 上传会议录音
- `GET /api/meetings` - 获取会议列表
- `GET /api/meetings/{id}` - 获取会议详情
- `GET /api/meetings/{id}/transcripts` - 获取对话记录
- `POST /api/meetings/{id}/generate-report` - 生成分析报告
- `POST /api/reports/{id}/send-email` - 发送邮件
- `POST /api/reports/{id}/sync-germplasm` - 同步种质库

## 技术栈

**前端**：React 18 + TypeScript + Vite + Tailwind CSS + Recharts + Axios

**后端**：FastAPI + Python 3.10 + SQLAlchemy + SQLite

**AI/ML**：
- librosa - 音频处理和噪声过滤
- openai-whisper - 语音识别
- pyannote.audio - 说话人分离
- OpenAI GPT-4 - 智能分析和摘要生成

**邮件**：smtplib + email
