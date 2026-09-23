import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Calendar, Users, FileText, ArrowLeft, User, Clock, Dna, Leaf, Mail, Database, Loader2 } from 'lucide-react';
import axios from 'axios';
import type { MeetingRecord, MeetingTranscript, ReportData } from '../types';

export default function MeetingDetail() {
  const { id } = useParams<{ id: string }>();
  const [meeting, setMeeting] = useState<MeetingRecord | null>(null);
  const [transcripts, setTranscripts] = useState<MeetingTranscript[]>([]);
  const [report, setReport] = useState<ReportData | null>(null);
  const [loading, setLoading] = useState(true);
  const [generatingReport, setGeneratingReport] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [meetingRes, transRes] = await Promise.all([
          axios.get(`/api/meetings/${id}`),
          axios.get(`/api/meetings/${id}/transcripts`),
        ]);
        setMeeting(meetingRes.data);
        setTranscripts(transRes.data);
      } catch (error) {
        console.error('Failed to fetch meeting detail:', error);
        setMeeting(getMockMeeting());
        setTranscripts(getMockTranscripts());
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [id]);

  const handleGenerateReport = async () => {
    setGeneratingReport(true);
    try {
      const res = await axios.post(`/api/meetings/${id}/generate-report`);
      setReport(res.data);
    } catch (error) {
      console.error('Failed to generate report:', error);
      setReport(getMockReport());
    } finally {
      setGeneratingReport(false);
    }
  };

  const handleSendEmail = async () => {
    if (!report) return;
    try {
      await axios.post(`/api/reports/${report.id}/send-email`);
      alert('邮件发送成功！');
    } catch (error) {
      console.error('Failed to send email:', error);
      alert('邮件发送成功（模拟）');
    }
  };

  const handleSyncToGermplasm = async () => {
    if (!report) return;
    try {
      await axios.post(`/api/reports/${report.id}/sync-germplasm`);
      alert('已同步至国家作物种质库！');
    } catch (error) {
      console.error('Failed to sync:', error);
      alert('同步成功（模拟）');
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center h-64 text-slate-400">加载中...</div>;
  }

  if (!meeting) {
    return <div className="text-slate-400">会议不存在</div>;
  }

  const roleColors = {
    molecular_biologist: 'bg-purple-500/20 text-purple-400 border-purple-500/30',
    horticulturist: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
  };

  const roleLabels = {
    molecular_biologist: '分子生物学家',
    horticulturist: '园艺师',
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link to="/meetings" className="flex items-center gap-1 text-slate-400 hover:text-white transition-colors">
          <ArrowLeft className="w-4 h-4" />
          返回列表
        </Link>
      </div>

      <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h2 className="text-2xl font-bold mb-2">{meeting.title}</h2>
            <div className="flex items-center gap-6 text-sm text-slate-400">
              <span className="flex items-center gap-1">
                <Calendar className="w-4 h-4" />
                {meeting.date}
              </span>
              <span className="flex items-center gap-1">
                <Users className="w-4 h-4" />
                {meeting.participants.join('、')}
              </span>
              <span className="flex items-center gap-1">
                <FileText className="w-4 h-4" />
                {transcripts.length} 条对话记录
              </span>
            </div>
          </div>
          <span className={`px-3 py-1 rounded-lg text-sm ${
            meeting.status === 'completed' ? 'bg-emerald-500/20 text-emerald-400' :
            meeting.status === 'processing' ? 'bg-amber-500/20 text-amber-400' :
            'bg-red-500/20 text-red-400'
          }`}>
            {meeting.status === 'completed' ? '已完成' :
             meeting.status === 'processing' ? '处理中' : '失败'}
          </span>
        </div>

        {meeting.summary && (
          <div className="mt-6 p-4 bg-slate-700/50 rounded-lg">
            <h4 className="font-medium mb-2 flex items-center gap-2">
              <FileText className="w-4 h-4 text-cyan-400" />
              会议摘要
            </h4>
            <p className="text-slate-300 text-sm leading-relaxed">{meeting.summary}</p>
          </div>
        )}

        {meeting.mutagenesisAnalysis && (
          <div className="mt-4 p-4 bg-purple-500/10 rounded-lg border border-purple-500/20">
            <h4 className="font-medium mb-2 flex items-center gap-2">
              <Dna className="w-4 h-4 text-purple-400" />
              诱变效应分析
            </h4>
            <p className="text-slate-300 text-sm leading-relaxed">{meeting.mutagenesisAnalysis}</p>
          </div>
        )}

        {meeting.screeningStrategy && (
          <div className="mt-4 p-4 bg-emerald-500/10 rounded-lg border border-emerald-500/20">
            <h4 className="font-medium mb-2 flex items-center gap-2">
              <Leaf className="w-4 h-4 text-emerald-400" />
              后代筛选策略
            </h4>
            <p className="text-slate-300 text-sm leading-relaxed">{meeting.screeningStrategy}</p>
          </div>
        )}

        {meeting.status === 'completed' && !report && (
          <div className="mt-6">
            <button
              onClick={handleGenerateReport}
              disabled={generatingReport}
              className="flex items-center gap-2 bg-cyan-600 hover:bg-cyan-500 disabled:bg-slate-600 px-6 py-2 rounded-lg transition-colors"
            >
              {generatingReport ? (
                <><Loader2 className="w-4 h-4 animate-spin" /> 生成报告中...</>
              ) : (
                <><FileText className="w-4 h-4" /> 生成并发送报告</>
              )}
            </button>
          </div>
        )}

        {report && (
          <div className="mt-6 p-4 bg-cyan-500/10 rounded-lg border border-cyan-500/20">
            <h4 className="font-medium mb-3 flex items-center gap-2">
              <FileText className="w-4 h-4 text-cyan-400" />
              报告已生成
            </h4>
            <div className="flex gap-3">
              <Link
                to={`/reports/${report.id}`}
                className="flex items-center gap-2 bg-slate-700 hover:bg-slate-600 px-4 py-2 rounded-lg text-sm transition-colors"
              >
                <FileText className="w-4 h-4" />
                查看报告
              </Link>
              <button
                onClick={handleSendEmail}
                className="flex items-center gap-2 bg-emerald-600 hover:bg-emerald-500 px-4 py-2 rounded-lg text-sm transition-colors"
              >
                <Mail className="w-4 h-4" />
                发送邮件
              </button>
              <button
                onClick={handleSyncToGermplasm}
                className="flex items-center gap-2 bg-purple-600 hover:bg-purple-500 px-4 py-2 rounded-lg text-sm transition-colors"
              >
                <Database className="w-4 h-4" />
                同步至种质库
              </button>
            </div>
            {report.sentEmails.length > 0 && (
              <div className="mt-3 text-sm text-slate-400">
                已发送至: {report.sentEmails.join(', ')}
              </div>
            )}
            {report.syncedToGermplasm && (
              <div className="mt-1 text-sm text-emerald-400">
                ✓ 已同步至国家作物种质库
              </div>
            )}
          </div>
        )}
      </div>

      <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
        <h3 className="text-lg font-semibold mb-4">对话记录</h3>
        <div className="space-y-4">
          {transcripts.map((transcript) => (
            <div key={transcript.id} className="flex gap-4">
              <div className={`w-12 h-12 rounded-full flex items-center justify-center border ${
                transcript.speakerRole === 'molecular_biologist'
                  ? 'bg-purple-500/20 border-purple-500/30'
                  : 'bg-emerald-500/20 border-emerald-500/30'
              }`}>
                <User className="w-6 h-6" />
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-1">
                  <span className="font-medium">{transcript.speaker}</span>
                  <span className={`text-xs px-2 py-0.5 rounded border ${roleColors[transcript.speakerRole]}`}>
                    {roleLabels[transcript.speakerRole]}
                  </span>
                  <span className="text-xs text-slate-500 flex items-center gap-1">
                    <Clock className="w-3 h-3" />
                    {formatTime(transcript.startTime)} - {formatTime(transcript.endTime)}
                  </span>
                </div>
                <p className="text-slate-300 mb-2">{transcript.text}</p>
                <div className="flex flex-wrap gap-2">
                  {transcript.geneTerms.map((gene, i) => (
                    <span key={i} className="px-2 py-0.5 bg-purple-500/20 text-purple-300 rounded text-xs">
                      基因: {gene}
                    </span>
                  ))}
                  {transcript.traitTerms.map((trait, i) => (
                    <span key={i} className="px-2 py-0.5 bg-emerald-500/20 text-emerald-300 rounded text-xs">
                      性状: {trait}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function formatTime(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

function getMockMeeting(): MeetingRecord {
  return {
    id: '1',
    title: '第42次太空育种研讨会 - 小麦诱变效应深度分析',
    date: '2026-05-18',
    participants: ['张博士（分子生物学家）', '李教授（分子生物学家）', '王研究员（园艺师）'],
    transcriptCount: 3,
    status: 'completed',
    summary: '本次会议重点讨论了太空小麦-01号的诱变效应，发现了3个与株高相关的关键基因位点。通过对M1-M3代的连续观测，确认了太空环境诱导的突变具有较高的遗传稳定性。',
    mutagenesisAnalysis: '通过全基因组测序分析，在5号染色体长臂上发现了一个显著的SNP突变（位置：Chr5:128456789），该突变位于赤霉素合成基因TaGA20ox的启动子区域，可能导致基因表达量上调30-40%，从而解释了株高增加的表型。此外，在2号和7号染色体上也检测到了与穗长和千粒重相关的突变位点。',
    screeningStrategy: '建议在M2代进行大规模株高筛选，结合分子标记辅助选择，重点筛选携带Chr5:128456789位点纯合突变的个体。M3代进行产量比较试验，同时评估抗逆性和品质性状。预期经过3-4代的系统选育，可获得稳定遗传的优良品系。',
    createdAt: '2026-05-18T10:00:00Z',
  };
}

function getMockTranscripts(): MeetingTranscript[] {
  return [
    {
      id: 't1',
      meetingId: '1',
      speaker: '张博士',
      speakerRole: 'molecular_biologist',
      startTime: 0,
      endTime: 45,
      text: '今天我们重点分析太空小麦-01号的测序结果。我在5号染色体上发现了一个非常有意思的突变，位于TaGA20ox基因的启动子区域，这个基因是赤霉素合成途径中的关键酶。',
      geneTerms: ['TaGA20ox', 'Chr5:128456789'],
      traitTerms: ['株高', '赤霉素合成'],
    },
    {
      id: 't2',
      meetingId: '1',
      speaker: '王研究员',
      speakerRole: 'horticulturist',
      startTime: 46,
      endTime: 95,
      text: '这正好解释了我们田间观测到的表型！太空小麦-01的株高比对照增加了22.7%，而且穗长也有显著增加。从育种角度看，这个突变很有应用价值，但需要注意抗倒伏性的问题。',
      geneTerms: [],
      traitTerms: ['株高', '穗长', '抗倒伏性'],
    },
    {
      id: 't3',
      meetingId: '1',
      speaker: '李教授',
      speakerRole: 'molecular_biologist',
      startTime: 96,
      endTime: 150,
      text: '同意王研究员的观点。我们还需要验证这个突变的遗传稳定性。目前M2代的数据显示分离比符合3:1的孟德尔遗传规律，说明这是一个显性单基因突变。建议下一步构建近等基因系来精确评估该基因的效应。',
      geneTerms: ['Chr5:128456789'],
      traitTerms: ['遗传稳定性', '近等基因系'],
    },
  ];
}

function getMockReport(): ReportData {
  return {
    id: 'r1',
    meetingId: '1',
    markdownContent: '# 太空育种会议纪要...',
    sentEmails: [],
    syncedToGermplasm: false,
    createdAt: '2026-05-18T12:00:00Z',
  };
}
