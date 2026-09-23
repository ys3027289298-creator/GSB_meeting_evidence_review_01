import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { TrendingUp, Users, FileText, Activity, ArrowRight } from 'lucide-react';
import axios from 'axios';
import type { PhenotypeData, MeetingRecord } from '../types';

export default function Dashboard() {
  const [phenotypeData, setPhenotypeData] = useState<PhenotypeData[]>([]);
  const [recentMeetings, setRecentMeetings] = useState<MeetingRecord[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [phenoRes, meetingsRes] = await Promise.all([
          axios.get('/api/phenotype'),
          axios.get('/api/meetings?limit=5'),
        ]);
        setPhenotypeData(phenoRes.data);
        setRecentMeetings(meetingsRes.data);
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error);
        setPhenotypeData(getMockPhenotypeData());
        setRecentMeetings(getMockMeetings());
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const stats = [
    { label: '已分析种子', value: '42', icon: TrendingUp, color: 'text-cyan-400' },
    { label: '记录会议', value: '156', icon: FileText, color: 'text-emerald-400' },
    { label: '科研人员', value: '28', icon: Users, color: 'text-purple-400' },
    { label: '显著突变', value: '128', icon: Activity, color: 'text-amber-400' },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-slate-400">加载中...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">总览</h2>

      <div className="grid grid-cols-4 gap-4">
        {stats.map((stat) => (
          <div key={stat.label} className="bg-slate-800 rounded-xl p-5 border border-slate-700">
            <div className="flex items-center justify-between">
              <stat.icon className={`w-8 h-8 ${stat.color}`} />
              <span className="text-3xl font-bold">{stat.value}</span>
            </div>
            <div className="mt-2 text-slate-400">{stat.label}</div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">显著表型变化</h3>
            <Link to="/phenotype" className="text-cyan-400 text-sm flex items-center gap-1 hover:text-cyan-300">
              查看全部 <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
          <div className="space-y-3">
            {phenotypeData.slice(0, 4).map((item) => (
              <div key={item.id} className="flex items-center justify-between py-2 border-b border-slate-700 last:border-0">
                <div>
                  <div className="font-medium">{item.seedName}</div>
                  <div className="text-sm text-slate-400">{item.traitName}</div>
                </div>
                <div className={`text-lg font-semibold ${
                  item.changePercentage > 0 ? 'text-emerald-400' : 'text-red-400'
                }`}>
                  {item.changePercentage > 0 ? '+' : ''}{item.changePercentage.toFixed(1)}%
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">最近会议</h3>
            <Link to="/meetings" className="text-cyan-400 text-sm flex items-center gap-1 hover:text-cyan-300">
              查看全部 <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
          <div className="space-y-3">
            {recentMeetings.map((meeting) => (
              <Link key={meeting.id} to={`/meetings/${meeting.id}`} className="block">
                <div className="flex items-center justify-between py-2 border-b border-slate-700 last:border-0 hover:bg-slate-700/50 px-2 -mx-2 rounded">
                  <div>
                    <div className="font-medium">{meeting.title}</div>
                    <div className="text-sm text-slate-400">{meeting.date}</div>
                  </div>
                  <span className={`px-2 py-1 rounded text-xs ${
                    meeting.status === 'completed' ? 'bg-emerald-500/20 text-emerald-400' :
                    meeting.status === 'processing' ? 'bg-amber-500/20 text-amber-400' :
                    'bg-red-500/20 text-red-400'
                  }`}>
                    {meeting.status === 'completed' ? '已完成' :
                     meeting.status === 'processing' ? '处理中' : '失败'}
                  </span>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function getMockPhenotypeData(): PhenotypeData[] {
  return [
    { id: '1', seedId: 'S001', seedName: '太空小麦-01', traitName: '株高', groundControl: 75, spaceFlight: 92, unit: 'cm', changePercentage: 22.7, significant: true },
    { id: '2', seedId: 'S002', seedName: '太空水稻-03', traitName: '千粒重', groundControl: 28, spaceFlight: 35, unit: 'g', changePercentage: 25.0, significant: true },
    { id: '3', seedId: 'S003', seedName: '太空番茄-07', traitName: '维生素C含量', groundControl: 15, spaceFlight: 22, unit: 'mg/100g', changePercentage: 46.7, significant: true },
    { id: '4', seedId: 'S004', seedName: '太空辣椒-02', traitName: '辣度', groundControl: 3000, spaceFlight: 4500, unit: 'SHU', changePercentage: 50.0, significant: true },
  ];
}

function getMockMeetings(): MeetingRecord[] {
  return [
    { id: '1', title: '第42次太空育种研讨会', date: '2026-05-18', participants: ['张博士', '李教授', '王研究员'], transcriptCount: 45, status: 'completed', createdAt: '2026-05-18T10:00:00Z' },
    { id: '2', title: '诱变效应分析会议', date: '2026-05-15', participants: ['张博士', '陈园艺师'], transcriptCount: 32, status: 'completed', createdAt: '2026-05-15T14:30:00Z' },
    { id: '3', title: '后代筛选策略讨论', date: '2026-05-12', participants: ['李教授', '赵研究员'], transcriptCount: 28, status: 'completed', createdAt: '2026-05-12T09:00:00Z' },
  ];
}
