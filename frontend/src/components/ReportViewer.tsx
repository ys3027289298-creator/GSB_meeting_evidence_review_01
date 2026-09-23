import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, Download, Mail, Database, CheckCircle } from 'lucide-react';
import axios from 'axios';
import type { ReportData } from '../types';

export default function ReportViewer() {
  const { id } = useParams<{ id: string }>();
  const [report, setReport] = useState<ReportData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await axios.get(`/api/reports/${id}`);
        setReport(res.data);
      } catch (error) {
        console.error('Failed to fetch report:', error);
        setReport(getMockReport());
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [id]);

  const handleDownload = () => {
    if (!report) return;
    const blob = new Blob([report.markdownContent], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `report-${report.id}.md`;
    a.click();
    URL.revokeObjectURL(url);
  };

  if (loading) {
    return <div className="flex items-center justify-center h-64 text-slate-400">加载中...</div>;
  }

  if (!report) {
    return <div className="text-slate-400">报告不存在</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <Link to="/meetings" className="flex items-center gap-1 text-slate-400 hover:text-white transition-colors">
          <ArrowLeft className="w-4 h-4" />
          返回会议列表
        </Link>
        <div className="flex gap-3">
          <button
            onClick={handleDownload}
            className="flex items-center gap-2 bg-slate-700 hover:bg-slate-600 px-4 py-2 rounded-lg text-sm transition-colors"
          >
            <Download className="w-4 h-4" />
            下载 Markdown
          </button>
        </div>
      </div>

      <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
        <div className="flex items-center gap-4 mb-6 pb-4 border-b border-slate-700">
          <h2 className="text-2xl font-bold">会议纪要报告</h2>
          <span className="text-sm text-slate-400">报告ID: {report.id}</span>
        </div>

        <div className="flex gap-4 mb-6">
          <div className="flex-1 p-4 bg-slate-700/50 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <Mail className="w-4 h-4 text-emerald-400" />
              <span className="text-sm font-medium">邮件发送状态</span>
            </div>
            {report.sentEmails.length > 0 ? (
              <div className="space-y-1">
                {report.sentEmails.map((email, i) => (
                  <div key={i} className="flex items-center gap-2 text-sm">
                    <CheckCircle className="w-3 h-3 text-emerald-400" />
                    <span className="text-slate-300">{email}</span>
                  </div>
                ))}
              </div>
            ) : (
              <span className="text-sm text-slate-400">未发送</span>
            )}
          </div>
          <div className="flex-1 p-4 bg-slate-700/50 rounded-lg">
            <div className="flex items-center gap-2 mb-2">
              <Database className="w-4 h-4 text-purple-400" />
              <span className="text-sm font-medium">种质库同步</span>
            </div>
            <div className="flex items-center gap-2 text-sm">
              {report.syncedToGermplasm ? (
                <><CheckCircle className="w-4 h-4 text-emerald-400" /><span className="text-emerald-400">已同步</span></>
              ) : (
                <span className="text-slate-400">未同步</span>
              )}
            </div>
          </div>
        </div>

        <div className="bg-slate-900 rounded-lg p-6 font-mono text-sm whitespace-pre-wrap text-slate-300 leading-relaxed">
          {report.markdownContent}
        </div>
      </div>
    </div>
  );
}

function getMockReport(): ReportData {
  return {
    id: 'r1',
    meetingId: '1',
    markdownContent: `# 太空育种会议纪要

**会议主题**: 第42次太空育种研讨会 - 小麦诱变效应深度分析
**会议日期**: 2026-05-18
**参会人员**: 张博士（分子生物学家）、李教授（分子生物学家）、王研究员（园艺师）

---

## 1. 会议摘要

本次会议重点讨论了太空小麦-01号的诱变效应，发现了3个与株高相关的关键基因位点。通过对M1-M3代的连续观测，确认了太空环境诱导的突变具有较高的遗传稳定性。

---

## 2. 诱变效应分析

### 2.1 基因组突变分析

通过全基因组测序分析，在5号染色体长臂上发现了一个显著的SNP突变（位置：**Chr5:128456789**），该突变位于赤霉素合成基因**TaGA20ox**的启动子区域。

| 基因位点 | 染色体 | 突变类型 | 相关性状 | 效应预测 |
|---------|--------|----------|----------|----------|
| TaGA20ox | 5号 | SNP（启动子） | 株高 | 表达量上调30-40% |
| - | 2号 | 缺失突变 | 穗长 | 正调控 |
| - | 7号 | 插入突变 | 千粒重 | 正调控 |

### 2.2 表型验证

- **株高**: 太空飞行组比地面对照组增加22.7%（P<0.01）
- **穗长**: 增加30.0%，差异极显著
- **千粒重**: 增加15.6%，差异显著

---

## 3. 后代筛选策略

### 3.1 筛选路线图

1. **M2代**（当前）: 大规模株高筛选，种植5000株群体
2. **M3代**: 产量比较试验，结合分子标记辅助选择
3. **M4-M5代**: 稳定性鉴定，多点试验
4. **M6代**: 品系比较，提交审定

### 3.2 关键技术措施

- 利用**Chr5:128456789**位点开发KASP标记
- 苗期进行分子标记检测，提前淘汰非目标单株
- 重点关注抗倒伏性和抗病性的负相关选择
- 构建近等基因系（NIL）进行基因效应精细评估

### 3.3 预期目标

经过3-4代的系统选育，预期获得：
- 株高增加20%以上
- 千粒重增加15%以上
- 抗倒伏性不低于对照
- 遗传稳定的优良品系2-3个

---

## 4. 发言记录摘要

### 张博士（分子生物学家） 00:00-00:45
> "今天我们重点分析太空小麦-01号的测序结果。我在5号染色体上发现了一个非常有意思的突变，位于TaGA20ox基因的启动子区域，这个基因是赤霉素合成途径中的关键酶。"

### 王研究员（园艺师） 00:46-01:35
> "这正好解释了我们田间观测到的表型！太空小麦-01的株高比对照增加了22.7%，而且穗长也有显著增加。从育种角度看，这个突变很有应用价值，但需要注意抗倒伏性的问题。"

### 李教授（分子生物学家） 01:36-02:30
> "同意王研究员的观点。我们还需要验证这个突变的遗传稳定性。目前M2代的数据显示分离比符合3:1的孟德尔遗传规律，说明这是一个显性单基因突变。建议下一步构建近等基因系来精确评估该基因的效应。"

---

**报告生成时间**: 2026-05-18 12:00:00
**系统**: 太空育种基因轨迹纪要系统 v1.0
`,
    sentEmails: ['zhang@example.com', 'li@example.com', 'wang@example.com'],
    syncedToGermplasm: true,
    createdAt: '2026-05-18T12:00:00Z',
  };
}
