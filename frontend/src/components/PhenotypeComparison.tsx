import { useState, useEffect } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  Cell,
} from 'recharts';
import { Search, Filter, ArrowUpDown, AlertTriangle } from 'lucide-react';
import axios from 'axios';
import type { PhenotypeData } from '../types';

export default function PhenotypeComparison() {
  const [phenotypeData, setPhenotypeData] = useState<PhenotypeData[]>([]);
  const [selectedSeed, setSelectedSeed] = useState<string>('all');
  const [sortBy, setSortBy] = useState<'name' | 'change'>('change');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await axios.get('/api/phenotype');
        setPhenotypeData(res.data);
      } catch (error) {
        console.error('Failed to fetch phenotype data:', error);
        setPhenotypeData(getMockData());
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const seeds = ['all', ...new Set(phenotypeData.map((d) => d.seedName))];

  const filteredData = phenotypeData
    .filter((d) => selectedSeed === 'all' || d.seedName === selectedSeed)
    .sort((a, b) => {
      if (sortBy === 'change') return Math.abs(b.changePercentage) - Math.abs(a.changePercentage);
      return a.seedName.localeCompare(b.seedName);
    });

  const chartData = filteredData.map((d) => ({
    name: `${d.seedName}\n${d.traitName}`,
    地面对照: d.groundControl,
    太空飞行: d.spaceFlight,
    变化率: d.changePercentage,
  }));

  const radarData = filteredData.slice(0, 8).map((d) => ({
    trait: `${d.seedName}-${d.traitName}`,
    变化幅度: Math.abs(d.changePercentage),
    显著性: d.significant ? 100 : 50,
  }));

  const COLORS = ['#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

  if (loading) {
    return <div className="flex items-center justify-center h-64 text-slate-400">加载中...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">表型对比分析</h2>
        <div className="flex items-center gap-4">
          <div className="relative">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              placeholder="搜索种子或性状..."
              className="bg-slate-800 border border-slate-700 rounded-lg pl-10 pr-4 py-2 text-sm focus:outline-none focus:border-cyan-500 w-64"
            />
          </div>
          <select
            value={selectedSeed}
            onChange={(e) => setSelectedSeed(e.target.value)}
            className="bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-sm focus:outline-none focus:border-cyan-500"
          >
            {seeds.map((seed) => (
              <option key={seed} value={seed}>
                {seed === 'all' ? '全部种子' : seed}
              </option>
            ))}
          </select>
          <button
            onClick={() => setSortBy(sortBy === 'change' ? 'name' : 'change')}
            className="flex items-center gap-2 bg-slate-800 border border-slate-700 rounded-lg px-4 py-2 text-sm hover:bg-slate-700"
          >
            <ArrowUpDown className="w-4 h-4" />
            {sortBy === 'change' ? '按变化率' : '按名称'}
          </button>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <BarChart className="w-5 h-5 text-cyan-400" />
            地面对照 vs 太空飞行
          </h3>
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="name" stroke="#94a3b8" fontSize={11} />
              <YAxis stroke="#94a3b8" />
              <Tooltip
                contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                labelStyle={{ color: '#f1f5f9' }}
              />
              <Legend />
              <Bar dataKey="地面对照" fill="#64748b" radius={[4, 4, 0, 0]} />
              <Bar dataKey="太空飞行" fill="#06b6d4" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <RadarChart className="w-5 h-5 text-purple-400" />
            突变影响雷达图
          </h3>
          <ResponsiveContainer width="100%" height={400}>
            <RadarChart data={radarData}>
              <PolarGrid stroke="#334155" />
              <PolarAngleAxis dataKey="trait" stroke="#94a3b8" fontSize={10} />
              <PolarRadiusAxis stroke="#475569" />
              <Radar name="变化幅度" dataKey="变化幅度" stroke="#06b6d4" fill="#06b6d4" fillOpacity={0.4} />
              <Radar name="显著性" dataKey="显著性" stroke="#10b981" fill="#10b981" fillOpacity={0.2} />
              <Legend />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="bg-slate-800 rounded-xl p-6 border border-slate-700">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Filter className="w-5 h-5 text-amber-400" />
          详细数据表
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-700">
                <th className="text-left py-3 px-4 font-medium text-slate-400">种子名称</th>
                <th className="text-left py-3 px-4 font-medium text-slate-400">性状</th>
                <th className="text-right py-3 px-4 font-medium text-slate-400">地面对照</th>
                <th className="text-right py-3 px-4 font-medium text-slate-400">太空飞行</th>
                <th className="text-right py-3 px-4 font-medium text-slate-400">变化率</th>
                <th className="text-center py-3 px-4 font-medium text-slate-400">显著性</th>
              </tr>
            </thead>
            <tbody>
              {filteredData.map((item, index) => (
                <tr key={item.id} className="border-b border-slate-700/50 hover:bg-slate-700/30">
                  <td className="py-3 px-4 font-medium">{item.seedName}</td>
                  <td className="py-3 px-4 text-slate-300">{item.traitName}</td>
                  <td className="py-3 px-4 text-right">{item.groundControl} {item.unit}</td>
                  <td className="py-3 px-4 text-right font-medium">{item.spaceFlight} {item.unit}</td>
                  <td className={`py-3 px-4 text-right font-semibold ${
                    item.changePercentage > 0 ? 'text-emerald-400' : 'text-red-400'
                  }`}>
                    {item.changePercentage > 0 ? '+' : ''}{item.changePercentage.toFixed(1)}%
                  </td>
                  <td className="py-3 px-4 text-center">
                    {item.significant ? (
                      <span className="inline-flex items-center gap-1 px-2 py-1 rounded bg-emerald-500/20 text-emerald-400 text-xs">
                        <AlertTriangle className="w-3 h-3" />
                        显著
                      </span>
                    ) : (
                      <span className="px-2 py-1 rounded bg-slate-600/50 text-slate-400 text-xs">
                        不显著
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function getMockData(): PhenotypeData[] {
  return [
    { id: '1', seedId: 'S001', seedName: '太空小麦-01', traitName: '株高', groundControl: 75, spaceFlight: 92, unit: 'cm', changePercentage: 22.7, significant: true },
    { id: '2', seedId: 'S001', seedName: '太空小麦-01', traitName: '穗长', groundControl: 10, spaceFlight: 13, unit: 'cm', changePercentage: 30.0, significant: true },
    { id: '3', seedId: 'S001', seedName: '太空小麦-01', traitName: '千粒重', groundControl: 45, spaceFlight: 52, unit: 'g', changePercentage: 15.6, significant: true },
    { id: '4', seedId: 'S002', seedName: '太空水稻-03', traitName: '株高', groundControl: 95, spaceFlight: 88, unit: 'cm', changePercentage: -7.4, significant: false },
    { id: '5', seedId: 'S002', seedName: '太空水稻-03', traitName: '千粒重', groundControl: 28, spaceFlight: 35, unit: 'g', changePercentage: 25.0, significant: true },
    { id: '6', seedId: 'S002', seedName: '太空水稻-03', traitName: '结实率', groundControl: 85, spaceFlight: 91, unit: '%', changePercentage: 7.1, significant: true },
    { id: '7', seedId: 'S003', seedName: '太空番茄-07', traitName: '单果重', groundControl: 150, spaceFlight: 210, unit: 'g', changePercentage: 40.0, significant: true },
    { id: '8', seedId: 'S003', seedName: '太空番茄-07', traitName: '维生素C含量', groundControl: 15, spaceFlight: 22, unit: 'mg/100g', changePercentage: 46.7, significant: true },
    { id: '9', seedId: 'S004', seedName: '太空辣椒-02', traitName: '单株结果数', groundControl: 25, spaceFlight: 32, unit: '个', changePercentage: 28.0, significant: true },
    { id: '10', seedId: 'S004', seedName: '太空辣椒-02', traitName: '辣度', groundControl: 3000, spaceFlight: 4500, unit: 'SHU', changePercentage: 50.0, significant: true },
  ];
}
