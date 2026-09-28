import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  Scale, Shield, Search, User, LogOut, CheckCircle2, 
  FileText, ClipboardCheck, Sparkles, BookOpen, Layers, Menu, X, Smartphone, Award, LayoutDashboard
} from 'lucide-react';

export const Navbar: React.FC = () => {
  const { user, logout, quickLogin } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [searchCert, setSearchCert] = useState('');
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [switchingRole, setSwitchingRole] = useState<string | null>(null);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchCert.trim()) {
      navigate(`/verify/${encodeURIComponent(searchCert.trim())}`);
      setSearchCert('');
      setMobileMenuOpen(false);
    }
  };

  const handleRoleSwitch = async (role: 'ADMIN' | 'LMO' | 'TRADER', targetPath: string) => {
    setSwitchingRole(role);
    try {
      await quickLogin(role);
      navigate(targetPath);
      setMobileMenuOpen(false);
    } catch (err) {
      console.error('Role switch failed:', err);
    } finally {
      setSwitchingRole(null);
    }
  };

  const isActive = (path: string) => location.pathname === path;

  return (
    <header className="bg-[#0F2942] text-white sticky top-0 z-50 shadow-md">
      {/* Top Tricolor Strip */}
      <div className="h-1 w-full bg-gradient-to-r from-orange-500 via-white to-emerald-600"></div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand */}
          <div className="flex items-center space-x-3">
            <Link to="/" className="flex items-center space-x-3 group">
              <div className="p-2 bg-slate-800/80 rounded-lg border border-slate-700 group-hover:border-amber-500 transition-colors">
                <Scale className="h-6 w-6 text-amber-400" />
              </div>
              <div>
                <span className="font-bold text-lg tracking-tight text-white flex items-center gap-1.5">
                  LegalMet <span className="text-amber-400 font-extrabold">Verify</span>
                </span>
                <span className="text-[10px] block text-slate-300 tracking-wider uppercase font-medium">
                  National Legal Metrology Portal • Govt. of India
                </span>
              </div>
            </Link>
          </div>

          {/* Quick Search */}
          <form onSubmit={handleSearch} className="hidden md:flex items-center relative max-w-xs w-full mx-4">
            <input
              type="text"
              placeholder="Search Certificate / QR / ID..."
              value={searchCert}
              onChange={(e) => setSearchCert(e.target.value)}
              className="w-full bg-slate-800/90 text-sm text-white placeholder-slate-400 rounded-lg pl-9 pr-3 py-1.5 border border-slate-700 focus:outline-none focus:border-amber-400 focus:ring-1 focus:ring-amber-400"
            />
            <Search className="h-4 w-4 text-slate-400 absolute left-2.5 top-2.5" />
          </form>

          {/* Navigation Links based on Role */}
          <nav className="hidden lg:flex items-center space-x-1">
            <Link
              to="/"
              className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                isActive('/') ? 'bg-slate-800 text-amber-400 font-bold' : 'text-slate-200 hover:text-white hover:bg-slate-800/50'
              }`}
            >
              Home
            </Link>

            {/* Trader Navigation */}
            {user?.role === 'TRADER' && (
              <>
                <Link
                  to="/trader/dashboard"
                  className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                    isActive('/trader/dashboard') ? 'bg-slate-800 text-amber-400 font-bold' : 'text-slate-200 hover:text-white hover:bg-slate-800/50'
                  }`}
                >
                  Dashboard
                </Link>
                <Link
                  to="/trader/instruments"
                  className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                    isActive('/trader/instruments') ? 'bg-slate-800 text-amber-400 font-bold' : 'text-slate-200 hover:text-white hover:bg-slate-800/50'
                  }`}
                >
                  My Instruments
                </Link>
                <Link
                  to="/trader/applications"
                  className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                    isActive('/trader/applications') ? 'bg-slate-800 text-amber-400 font-bold' : 'text-slate-200 hover:text-white hover:bg-slate-800/50'
                  }`}
                >
                  Applications
                </Link>
                <Link
                  to="/trader/certificates"
                  className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                    isActive('/trader/certificates') ? 'bg-slate-800 text-amber-400 font-bold' : 'text-slate-200 hover:text-white hover:bg-slate-800/50'
                  }`}
                >
                  Vault
                </Link>
              </>
            )}

            {/* Admin Navigation */}
            {user?.role === 'ADMIN' && (
              <>
                <Link
                  to="/admin/dashboard"
                  className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                    isActive('/admin/dashboard') ? 'bg-slate-800 text-amber-400 font-bold' : 'text-slate-200 hover:text-white hover:bg-slate-800/50'
                  }`}
                >
                  Admin Portal
                </Link>
                <Link
                  to="/trader/dashboard"
                  className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                    isActive('/trader/dashboard') ? 'bg-slate-800 text-amber-400 font-bold' : 'text-slate-200 hover:text-white hover:bg-slate-800/50'
                  }`}
                  title="Supervise Trader Portal"
                >
                  Trader View
                </Link>
                <Link
                  to="/lmo/dashboard"
                  className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                    isActive('/lmo/dashboard') ? 'bg-slate-800 text-amber-400 font-bold' : 'text-slate-200 hover:text-white hover:bg-slate-800/50'
                  }`}
                  title="Supervise LMO Field View"
                >
                  LMO View
                </Link>
                <Link
                  to="/admin/models"
                  className={`px-2.5 py-1.5 rounded-md text-xs font-medium transition-colors ${
                    isActive('/admin/models') ? 'bg-slate-800 text-amber-400' : 'text-slate-300 hover:text-white hover:bg-slate-800/50'
                  }`}
                >
                  Catalog
                </Link>
                <Link
                  to="/admin/applications"
                  className={`px-2.5 py-1.5 rounded-md text-xs font-medium transition-colors ${
                    isActive('/admin/applications') ? 'bg-slate-800 text-amber-400' : 'text-slate-300 hover:text-white hover:bg-slate-800/50'
                  }`}
                >
                  Scrutiny
                </Link>
                <Link
                  to="/admin/rules"
                  className={`px-2.5 py-1.5 rounded-md text-xs font-medium transition-colors ${
                    isActive('/admin/rules') ? 'bg-slate-800 text-amber-400' : 'text-slate-300 hover:text-white hover:bg-slate-800/50'
                  }`}
                >
                  Rules
                </Link>
                <Link
                  to="/admin/ocr"
                  className={`px-2.5 py-1.5 rounded-md text-xs font-medium transition-colors ${
                    isActive('/admin/ocr') ? 'bg-slate-800 text-amber-400' : 'text-slate-300 hover:text-white hover:bg-slate-800/50'
                  }`}
                >
                  OCR
                </Link>
                <Link
                  to="/admin/audit"
                  className={`px-2.5 py-1.5 rounded-md text-xs font-medium transition-colors ${
                    isActive('/admin/audit') ? 'bg-slate-800 text-amber-400' : 'text-slate-300 hover:text-white hover:bg-slate-800/50'
                  }`}
                >
                  Audit
                </Link>
              </>
            )}

            {/* LMO Navigation */}
            {user?.role === 'LMO' && (
              <>
                <Link
                  to="/lmo/dashboard"
                  className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                    isActive('/lmo/dashboard') ? 'bg-slate-800 text-amber-400 font-bold' : 'text-slate-200 hover:text-white hover:bg-slate-800/50'
                  }`}
                >
                  Field Inspections Queue
                </Link>
              </>
            )}
          </nav>

          {/* User Controls & Instant Role Switcher */}
          <div className="flex items-center space-x-2 sm:space-x-3">
            {/* Quick Demo Switcher */}
            <div className="hidden sm:flex items-center bg-slate-800/90 rounded-lg p-1 border border-slate-700 text-xs">
              <span className="text-slate-400 px-1.5 font-medium">Switch Role:</span>
              <button
                onClick={() => handleRoleSwitch('TRADER', '/trader/dashboard')}
                disabled={switchingRole !== null}
                className={`px-2.5 py-1 rounded transition-colors ${
                  user?.role === 'TRADER' ? 'bg-amber-500 text-slate-950 font-bold shadow-xs' : 'text-slate-300 hover:text-white'
                }`}
                title="Log in as Ramesh Patel (Patel Agro Commodities)"
              >
                {switchingRole === 'TRADER' ? 'Switching...' : 'Trader'}
              </button>
              <button
                onClick={() => handleRoleSwitch('ADMIN', '/admin/dashboard')}
                disabled={switchingRole !== null}
                className={`px-2.5 py-1 rounded transition-colors ${
                  user?.role === 'ADMIN' ? 'bg-amber-500 text-slate-950 font-bold shadow-xs' : 'text-slate-300 hover:text-white'
                }`}
                title="Log in as Rajesh Verma (Senior Inspector / Admin)"
              >
                {switchingRole === 'ADMIN' ? 'Switching...' : 'Admin'}
              </button>
              <button
                onClick={() => handleRoleSwitch('LMO', '/lmo/dashboard')}
                disabled={switchingRole !== null}
                className={`px-2.5 py-1 rounded transition-colors ${
                  user?.role === 'LMO' ? 'bg-amber-500 text-slate-950 font-bold shadow-xs' : 'text-slate-300 hover:text-white'
                }`}
                title="Log in as Amit Sharma (Legal Metrology Officer)"
              >
                {switchingRole === 'LMO' ? 'Switching...' : 'LMO Officer'}
              </button>
            </div>

            {user ? (
              <div className="flex items-center space-x-2">
                <div className="text-right hidden md:block">
                  <div className="text-xs font-semibold text-white leading-tight">{user.full_name}</div>
                  <div className="text-[10px] text-amber-400 uppercase font-medium">{user.role}</div>
                </div>
                <button
                  onClick={() => { logout(); navigate('/'); }}
                  title="Logout"
                  className="p-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white rounded-lg border border-slate-700"
                >
                  <LogOut className="h-4 w-4" />
                </button>
              </div>
            ) : (
              <div className="flex items-center space-x-2">
                <Link
                  to="/login"
                  className="px-3 py-1.5 bg-amber-500 hover:bg-amber-400 text-slate-950 text-xs font-bold rounded-lg shadow transition-colors"
                >
                  Sign In
                </Link>
              </div>
            )}

            {/* Mobile Hamburger Button */}
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="lg:hidden p-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white rounded-lg border border-slate-700"
              aria-label="Toggle navigation menu"
            >
              {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Drawer Menu */}
      {mobileMenuOpen && (
        <div className="lg:hidden bg-slate-900 border-t border-slate-800 px-4 py-4 space-y-4">
          {/* Mobile Search */}
          <form onSubmit={handleSearch} className="flex items-center relative w-full">
            <input
              type="text"
              placeholder="Search Certificate / QR..."
              value={searchCert}
              onChange={(e) => setSearchCert(e.target.value)}
              className="w-full bg-slate-800 text-sm text-white placeholder-slate-400 rounded-lg pl-9 pr-3 py-2 border border-slate-700 focus:outline-none focus:border-amber-400"
            />
            <Search className="h-4 w-4 text-slate-400 absolute left-2.5 top-3" />
          </form>

          {/* Quick Role Switcher for Mobile */}
          <div className="bg-slate-800 p-2.5 rounded-xl border border-slate-700">
            <div className="text-[11px] font-semibold text-slate-400 uppercase mb-2">Switch Active Portal:</div>
            <div className="grid grid-cols-3 gap-1.5">
              <button
                onClick={() => handleRoleSwitch('TRADER', '/trader/dashboard')}
                className={`py-1.5 rounded text-xs font-bold text-center ${
                  user?.role === 'TRADER' ? 'bg-amber-500 text-slate-950' : 'bg-slate-700 text-slate-200'
                }`}
              >
                Trader
              </button>
              <button
                onClick={() => handleRoleSwitch('ADMIN', '/admin/dashboard')}
                className={`py-1.5 rounded text-xs font-bold text-center ${
                  user?.role === 'ADMIN' ? 'bg-amber-500 text-slate-950' : 'bg-slate-700 text-slate-200'
                }`}
              >
                Admin
              </button>
              <button
                onClick={() => handleRoleSwitch('LMO', '/lmo/dashboard')}
                className={`py-1.5 rounded text-xs font-bold text-center ${
                  user?.role === 'LMO' ? 'bg-amber-500 text-slate-950' : 'bg-slate-700 text-slate-200'
                }`}
              >
                LMO
              </button>
            </div>
          </div>

          {/* Mobile Navigation Links */}
          <div className="space-y-1 text-sm font-medium">
            <Link
              to="/"
              onClick={() => setMobileMenuOpen(false)}
              className="block px-3 py-2 rounded-lg text-slate-200 hover:bg-slate-800"
            >
              Home
            </Link>
            <Link
              to="/trader/dashboard"
              onClick={() => setMobileMenuOpen(false)}
              className="block px-3 py-2 rounded-lg text-slate-200 hover:bg-slate-800"
            >
              Trader Dashboard
            </Link>
            <Link
              to="/admin/dashboard"
              onClick={() => setMobileMenuOpen(false)}
              className="block px-3 py-2 rounded-lg text-slate-200 hover:bg-slate-800"
            >
              Admin Portal
            </Link>
            <Link
              to="/lmo/dashboard"
              onClick={() => setMobileMenuOpen(false)}
              className="block px-3 py-2 rounded-lg text-slate-200 hover:bg-slate-800"
            >
              LMO Field Inspections
            </Link>
          </div>
        </div>
      )}
    </header>
  );
};
