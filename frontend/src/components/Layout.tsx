import { Outlet, NavLink } from 'react-router-dom';
import { Atom, Microscope, Calendar, Upload, FileText, Home } from 'lucide-react';

export default function Layout() {
  const navItems = [
    { to: '/', icon: Home, label: '总览' },
    { to: '/phenotype', icon: Microscope, label: '表型对比' },
    { to: '/meetings', icon: Calendar, label: '会议记录' },
    { to: '/upload', icon: Upload, label: '上传录音' },
  ];

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      <header className="bg-slate-800 border-b border-slate-700">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Atom className="w-8 h-8 text-cyan-400" />
            <h1 className="text-xl font-bold">太空育种基因轨迹纪要系统</h1>
          </div>
          <div className="text-sm text-slate-400">Space Breeding Gene Trajectory System</div>
        </div>
      </header>

      <div className="flex">
        <nav className="w-64 bg-slate-800 min-h-screen border-r border-slate-700 p-4">
          <ul className="space-y-2">
            {navItems.map((item) => (
              <li key={item.to}>
                <NavLink
                  to={item.to}
                  end={item.to === '/'}
                  className={({ isActive }) =>
                    `flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                      isActive
                        ? 'bg-cyan-600 text-white'
                        : 'text-slate-300 hover:bg-slate-700'
                    }`
                  }
                >
                  <item.icon className="w-5 h-5" />
                  <span>{item.label}</span>
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>

        <main className="flex-1 p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
