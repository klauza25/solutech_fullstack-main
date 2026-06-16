/**
 * =============================================================================
 * LAYOUT PRINCIPAL
 * Navigation adaptative : sidebar sur desktop, bottom nav sur mobile
 * Optimisé pour écrans tactiles et terminaux Android milieu de gamme
 * =============================================================================
 */

import { useState } from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import {
  LayoutDashboard,
  Users,
  GraduationCap,
  BookOpen,
  CalendarCheck,
  Settings,
  LogOut,
  Menu,
  X,
  School,
  BarChart3,
} from 'lucide-react';
import { useApp } from '@/context/AppContext';
import { OfflineIndicator } from './OfflineIndicator';

interface NavItem {
  to: string;
  label: string;
  icon: React.ReactNode;
  roles: string[];
}

const NAV_ITEMS: NavItem[] = [
  { to: '/', label: 'Tableau', icon: <LayoutDashboard className="w-5 h-5" />, roles: ['ADMIN', 'DIRECTEUR', 'ENSEIGNANT', 'ELEVE', 'PARENT'] },
  { to: '/eleves', label: 'Élèves', icon: <Users className="w-5 h-5" />, roles: ['ADMIN', 'DIRECTEUR', 'ENSEIGNANT'] },
  { to: '/enseignants', label: 'Enseignants', icon: <GraduationCap className="w-5 h-5" />, roles: ['ADMIN', 'DIRECTEUR'] },
  { to: '/notes', label: 'Notes', icon: <BookOpen className="w-5 h-5" />, roles: ['ADMIN', 'DIRECTEUR', 'ENSEIGNANT', 'ELEVE', 'PARENT'] },
  { to: '/presences', label: 'Présences', icon: <CalendarCheck className="w-5 h-5" />, roles: ['ADMIN', 'DIRECTEUR', 'ENSEIGNANT'] },
  { to: '/statistiques', label: 'Stats', icon: <BarChart3 className="w-5 h-5" />, roles: ['ADMIN', 'DIRECTEUR'] },
  { to: '/parametres', label: 'Paramètres', icon: <Settings className="w-5 h-5" />, roles: ['ADMIN', 'DIRECTEUR'] },
];

export function Layout({ children }: { children: React.ReactNode }) {
  const { utilisateur, logout, etablissement } = useApp();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();

  const filteredNav = NAV_ITEMS.filter((item) =>
    item.roles.includes(utilisateur?.role ?? '')
  );

  const currentLabel = NAV_ITEMS.find((n) => n.to === location.pathname)?.label ?? 'SOLUTECH';

  return (
    <div className="min-h-screen bg-base-200 flex">
      {/* Sidebar Desktop */}
      <aside className="hidden lg:flex flex-col w-64 bg-base-100 border-r border-base-300 fixed h-full z-30">
        <div className="p-4 border-b border-base-300">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-primary rounded-xl flex items-center justify-center">
              <School className="w-5 h-5 text-primary-content" />
            </div>
            <div className="min-w-0">
              <h1 className="font-bold text-base leading-tight truncate">SOLUTECH</h1>
              <p className="text-[10px] text-base-content/60 truncate">
                {etablissement?.nom ?? 'Chargement...'}
              </p>
            </div>
          </div>
        </div>

        <nav className="flex-1 overflow-y-auto p-3 space-y-1">
          {filteredNav.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors ${
                  isActive
                    ? 'bg-primary text-primary-content font-medium'
                    : 'text-base-content/70 hover:bg-base-200 hover:text-base-content'
                }`
              }
            >
              {item.icon}
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="p-3 border-t border-base-300 space-y-2">
          <div className="px-3">
            <OfflineIndicator />
          </div>
          <div className="flex items-center gap-3 px-3 py-2">
            <div className="w-8 h-8 rounded-full bg-secondary flex items-center justify-center text-secondary-content text-xs font-bold">
              {utilisateur?.prenom?.charAt(0)}{utilisateur?.nom?.charAt(0)}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">
                {utilisateur?.prenom} {utilisateur?.nom}
              </p>
              <p className="text-[10px] text-base-content/50 truncate">{utilisateur?.role}</p>
            </div>
            <button
              onClick={logout}
              className="btn btn-ghost btn-xs btn-circle"
              aria-label="Déconnexion"
              title="Déconnexion"
            >
              <LogOut className="w-4 h-4" />
            </button>
          </div>
        </div>
      </aside>

      {/* Contenu principal */}
      <div className="flex-1 lg:ml-64 flex flex-col min-h-screen">
        {/* Header Mobile */}
        <header className="lg:hidden sticky top-0 z-20 bg-base-100 border-b border-base-300 px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setSidebarOpen(true)}
              className="btn btn-ghost btn-sm btn-circle"
              aria-label="Ouvrir le menu"
            >
              <Menu className="w-5 h-5" />
            </button>
            <div>
              <h1 className="font-bold text-sm">{currentLabel}</h1>
              <p className="text-[10px] text-base-content/60 truncate max-w-[180px]">
                {etablissement?.nom}
              </p>
            </div>
          </div>
          <OfflineIndicator />
        </header>

        {/* Zone de contenu scrollable */}
        <main className="flex-1 p-4 pb-24 lg:pb-6 overflow-x-hidden">
          <div className="max-w-6xl mx-auto">
            {children}
          </div>
        </main>

        {/* Bottom Navigation Mobile */}
        <nav className="lg:hidden fixed bottom-0 left-0 right-0 bg-base-100 border-t border-base-300 z-20 safe-area-pb">
          <div className="flex justify-around items-center h-16">
            {filteredNav.slice(0, 5).map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  `flex flex-col items-center justify-center gap-0.5 w-full h-full text-[10px] transition-colors ${
                    isActive ? 'text-primary font-medium' : 'text-base-content/50'
                  }`
                }
              >
                {item.icon}
                <span>{item.label}</span>
              </NavLink>
            ))}
          </div>
        </nav>
      </div>

      {/* Drawer Mobile Overlay */}
      {sidebarOpen && (
        <>
          <div
            className="lg:hidden fixed inset-0 bg-black/50 z-40"
            onClick={() => setSidebarOpen(false)}
          />
          <div className="lg:hidden fixed inset-y-0 left-0 w-72 bg-base-100 z-50 flex flex-col shadow-2xl">
            <div className="p-4 border-b border-base-300 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-primary rounded-xl flex items-center justify-center">
                  <School className="w-5 h-5 text-primary-content" />
                </div>
                <div>
                  <h1 className="font-bold text-base">SOLUTECH</h1>
                </div>
              </div>
              <button
                onClick={() => setSidebarOpen(false)}
                className="btn btn-ghost btn-sm btn-circle"
                aria-label="Fermer le menu"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            <nav className="flex-1 overflow-y-auto p-3 space-y-1">
              {filteredNav.map((item) => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  onClick={() => setSidebarOpen(false)}
                  className={({ isActive }) =>
                    `flex items-center gap-3 px-3 py-3 rounded-lg text-sm transition-colors ${
                      isActive
                        ? 'bg-primary text-primary-content font-medium'
                        : 'text-base-content/70 hover:bg-base-200'
                    }`
                  }
                >
                  {item.icon}
                  <span>{item.label}</span>
                </NavLink>
              ))}
            </nav>
            <div className="p-4 border-t border-base-300">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-8 h-8 rounded-full bg-secondary flex items-center justify-center text-secondary-content text-xs font-bold">
                  {utilisateur?.prenom?.charAt(0)}{utilisateur?.nom?.charAt(0)}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">
                    {utilisateur?.prenom} {utilisateur?.nom}
                  </p>
                  <p className="text-[10px] text-base-content/50">{utilisateur?.role}</p>
                </div>
              </div>
              <button onClick={logout} className="btn btn-outline btn-sm w-full gap-2">
                <LogOut className="w-4 h-4" />
                Déconnexion
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
