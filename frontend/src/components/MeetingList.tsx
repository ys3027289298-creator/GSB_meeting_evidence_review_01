import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Calendar, Users, FileText, Clock, ChevronRight, Search } from 'lucide-react';
import axios from 'axios';
import type { MeetingRecord } from '../types';

export default function MeetingList() {
  const [meetings, setMeetings] = useState<MeetingRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await axios.get('/api/meetings');
        setMeetings(res.data);
      } catch (error) {
        console.error('Failed to fetch meetings:', error);
        setMeetings(getMockMeetings());
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const filteredMeetings = meetings.filter((m) =>
    m.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    m.participants.some((p) => p.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  if (loading) {
    return <div className="flex items-center justify-center h-64 text-slate-400">加载中...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">会议记录</h2>
        <div className="relative">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            placeholder="搜索会议或参与者..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="bg-slate-800 border border-slate-700 rounded-lg pl-10 pr-4 py-2 text-sm focus:outline-none focus:border-cyan-500 w-80"
          />
        </div>
      </div>

      <div className="space-y-4">
        {filteredMeetings.map((meeting) => (
          <Link
            key={meeting.id}
            to={`/meetings/${meeting.id}`}
            className="block bg-slate-800 rounded-xl p-5 border border-slate-700 hover:border-cyan-500/50 transition-colors group"
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <h3 className="text-lg font-semibold group-hover:text-cyan-400 transition-colors">
                    {meeting.title}
                  </h3>
                  <span className={`px-2 py-1 rounded text-xs ${
                    meeting.status === 'completed' ? 'bg-emerald-500/20 text-emerald-400' :
                    meeting.status === 'processing' ? 'bg-amber-500/20 text-amber-400' :
                    'bg-red-500/20 text-red-400'
                  }`}>
                    {meeting.status === 'completed' ? '已完成' :
                     meeting.status === 'processing' ? '处理中' : '失败'}
                  </span>
                </div>
                <div className="flex items-center gap-6 text-sm text-slate-400">
                  <span className="flex items-center gap-1">
                    <Calendar className="w-4 h-4" />
                    {meeting.date}
                  </span>
                  <span className="flex items-center gap-1">
                    <Users className="w-4 h-4" />
                    {meeting.participants.length} 位参与者
                  </span>
                  <span className="flex items-center gap-1">
                    <FileText className="w-4 h-4" />
                    {meeting.transcriptCount} 条记录
                  </span>
                </div>
                <div className="mt-3 flex flex-wrap gap-2">
                  {meeting.participants.map((p, i) => (
                    <span key={i} className="px-2 py-1 bg-slate-700 rounded text-xs">
                      {p}
                    </span>
                  ))}
                </div>
              </div>
              <ChevronRight className="w-5 h-5 text-slate-500 group-hover:text-cyan-400 transition-colors" />
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}

function getMockMeetings(): MeetingRecord[] {
  return [
    {
      id: '1',
      title: '第42次太空育种研讨会 - 小麦诱变效应深度分析',
      date: '2026-05-18',
      participants: ['张博士（分子生物学家）', '李教授（分子生物学家）', '王研究员（园艺师）'],
      transcriptCount: 45,
      status: 'completed',
      summary: '本次会议重点讨论了太空小麦-01号的诱变效应，发现了3个与株高相关的关键基因位点...',
      mutagenesisAnalysis: '通过全基因组测序分析，在5号染色体长臂上发现了一个显著的SNP突变...',
      screeningStrategy: '建议在M2代进行大规模株高筛选，结合分子标记辅助选择...',
      createdAt: '2026-05-18T10:00:00Z',
    },
    {
      id: '2',
      title: '水稻空间诱变后代筛选策略讨论会',
      date: '2026-05-15',
      participants: ['张博士（分子生物学家）', '陈园艺师', '刘技术员'],
      transcriptCount: 32,
      status: 'completed',
      summary: '会议确定了太空水稻-03号的后代筛选方案，重点关注千粒重和结实率性状...',
      createdAt: '2026-05-15T14:30:00Z',
    },
    {
      id: '3',
      title: '番茄品质性状基因定位会议',
      date: '2026-05-12',
      participants: ['李教授（分子生物学家）', '赵研究员（园艺师）'],
      transcriptCount: 28,
      status: 'completed',
      createdAt: '2026-05-12T09:00:00Z',
    },
    {
      id: '4',
      title: '辣椒辣度调控机制研究进展汇报',
      date: '2026-05-10',
      participants: ['王研究员（园艺师）', '陈园艺师'],
      transcriptCount: 0,
      status: 'processing',
      createdAt: '2026-05-10T16:00:00Z',
    },
  ];
}
