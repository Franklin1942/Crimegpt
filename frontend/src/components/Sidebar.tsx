'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Bot, FileSearch, LayoutDashboard, LogOut, ScrollText, ShieldCheck } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';

const NAV_ITEMS = [
  { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/cases', label: 'Cases', icon: FileSearch },
  { href: '/copilot', label: 'Investigator Copilot', icon: Bot },
  { href: '/audit', label: 'Audit Log', icon: ScrollText },
];

export default function Sidebar() {
  const pathname = usePathname();
  const { user, logout } = useAuth();

  return (
    <aside className="flex w-64 flex-col justify-between bg-slate-900 p-4 text-slate-200">
      <div>
        <div className="mb-8 flex items-center gap-2">
          <ShieldCheck className="h-7 w-7 text-brand-500" />
          <span className="text-lg font-bold text-white">CrimeGPT</span>
        </div>
        <nav className="space-y-1">
          {NAV_ITEMS.map((item) => {
            const active = pathname === item.href || pathname.startsWith(`${item.href}/`);
            const Icon = item.icon;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors ${
                  active ? 'bg-brand-600 text-white' : 'hover:bg-slate-800'
                }`}
              >
                <Icon className="h-4 w-4" />
                {item.label}
              </Link>
            );
          })}
        </nav>
      </div>

      <div className="border-t border-slate-800 pt-4 text-sm">
        <p className="font-medium text-white">{user?.full_name}</p>
        <p className="mb-3 text-xs capitalize text-slate-400">
          {user?.role.replace(/_/g, ' ')}
        </p>
        <button onClick={logout} className="flex items-center gap-2 text-slate-300 hover:text-white">
          <LogOut className="h-4 w-4" /> Sign out
        </button>
      </div>
    </aside>
  );
}
