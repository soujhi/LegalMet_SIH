import React, { useState, useRef, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  Scale, Search, LogOut, Menu, X, ArrowRight,
  ChevronDown, LayoutDashboard, FileText, BookOpen,
  Sparkles, ClipboardCheck, Layers, Shield, Smartphone, Award
} from 'lucide-react';

export const Navbar: React.FC = () => {
  const { user, logout, quickLogin } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [searchCert, setSearchCert] = useState('');
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [switchingRole, setSwitchingRole] = useState<string | null>(null);
  const [adminDropdownOpen, setAdminDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setAdminDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchCert.trim()) {
      navigate(`/verify/${encodeURIComponent(searchCert.trim())}`);
      setSearchCert('');
      setMobileMenuOpen(false);
    }
  };

  const handleRoleSwitch = async (role: 'ADMIN' | 'LMO' | 'TRADER', targetPath: string) => {
    const storedUserStr = localStorage.getItem('legalmet_user');
    const storedRole = storedUserStr ? JSON.parse(storedUserStr)?.role : user?.role;
    if (storedRole === role) {
      navigate(targetPath);
      setMobileMenuOpen(false);
      return;
    }

    setSwitchingRole(role);
    try {
      await quickLogin(role);
      navigate(targetPath);
      setMobileMenuOpen(false);
    } catch (err) {
      console.error('Role switch failed:', err);
      navigate(targetPath);
    } finally {
      setSwitchingRole(null);
    }
  };

  const isActive = (path: string) => location.pathname === path;
  const isAdminSubPage = ['/admin/models', '/admin/data-quality', '/admin/applications', '/admin/rules', '/admin/ocr', '/admin/audit'].some(p => location.pathname === p);

  const adminSubLinks = [
    { path: '/admin/applications', label: 'Scrutiny', icon: ClipboardCheck },
    { path: '/admin/models', label: 'Model Catalog', icon: Layers },
    { path: '/admin/rules', label: 'Rules Engine', icon: BookOpen },
    { path: '/admin/ocr', label: 'OCR Hub', icon: Sparkles },
    { path: '/admin/audit', label: 'Audit Logs', icon: FileText },
  ];

  return (
    <header className="bg-[#0F2942] text-white sticky top-0 z-50 shadow-md">
      {/* Top Tricolor Strip */}
      <div className="h-1 w-full bg-gradient-to-r from-orange-500 via-white to-emerald-600"></div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-14">
          {/* Brand */}
          <Link to="/" className="flex items-center space-x-2.5 group shrink-0">
            <div className="p-1.5 bg-slate-800/80 rounded-lg border border-slate-700 group-hover:border-amber-500 transition-colors">
              <Scale className="h-5 w-5 text-amber-400" />
            </div>
            <div>
              <span className="font-bold text-base tracking-tight text-white flex items-center gap-1">
                LegalMet <span className="text-amber-400 font-extrabold">Verify</span>
              </span>
              <span className="text-[9px] block text-slate-400 tracking-wider uppercase font-medium leading-tight">
                National Legal Metrology Portal
              </span>
            </div>
          </Link>

          {/* Center: Navigation Links */}
          <nav className="hidden lg:flex items-center space-x-1 mx-4">
            <Link
              to="/"
              className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                isActive('/') ? 'bg-slate-800 text-amber-400 font-bold' : 'text-slate-300 hover:text-white hover:bg-slate-800/50'
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
                    isActive('/trader/dashboard') ? 'bg-slate-800 text-amber-400 font-bold' : 'text-slate-300 hover:text-white hover:bg-slate-800/50'
                  }`}
                >
                  Dashboard
                </Link>
                <Link
                  to="/trader/instruments"
                  className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                    isActive('/trader/instruments') ? 'bg-slate-800 text-amber-400 font-bold' : 'text-slate-300 hover:text-white hover:bg-slate-800/50'
                  }`}
                >
                  Instruments
                </Link>
                <Link
                  to="/trader/applications"
                  className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                    isActive('/trader/applications') ? 'bg-slate-800 text-amber-400 font-bold' : 'text-slate-300 hover:text-white hover:bg-slate-800/50'
                  }`}
                >
                  Applications
                </Link>
                <Link
                  to="/trader/certificates"
                  className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                    isActive('/trader/certificates') ? 'bg-slate-800 text-amber-400 font-bold' : 'text-slate-300 hover:text-white hover:bg-slate-800/50'
                  }`}
                >
                  Certificates
                </Link>
              </>
            )}

            {/* Admin Navigation — Dashboard + Dropdown */}
            {user?.role === 'ADMIN' && (
              <>
                <Link
                  to="/admin/dashboard"
                  className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                    isActive('/admin/dashboard') ? 'bg-slate-800 text-amber-400 font-bold' : 'text-slate-300 hover:text-white hover:bg-slate-800/50'
                  }`}
                >
                  Dashboard
                </Link>

                {/* Admin Sub-pages Dropdown */}
                <div className="relative" ref={dropdownRef}>
                  <button
                    onClick={() => setAdminDropdownOpen(!adminDropdownOpen)}
                    className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors flex items-center gap-1 ${
                      isAdminSubPage ? 'bg-slate-800 text-amber-400 font-bold' : 'text-slate-300 hover:text-white hover:bg-slate-800/50'
                    }`}
                  >
                    Manage <ChevronDown className={`h-3.5 w-3.5 transition-transform ${adminDropdownOpen ? 'rotate-180' : ''}`} />
                  </button>

                  {adminDropdownOpen && (
                    <div className="absolute top-full left-0 mt-1.5 w-52 bg-slate-900 border border-slate-700 rounded-xl shadow-2xl py-1.5 z-50">
                      {adminSubLinks.map((link) => (
                        <Link
                          key={link.path}
                          to={link.path}
                          onClick={() => setAdminDropdownOpen(false)}
                          className={`flex items-center gap-2.5 px-3.5 py-2 text-sm transition-colors ${
                            isActive(link.path)
                              ? 'bg-amber-500/10 text-amber-400 font-bold'
                              : 'text-slate-300 hover:bg-slate-800 hover:text-white'
                          }`}
                        >
                          <link.icon className="h-4 w-4 shrink-0" />
                          {link.label}
                        </Link>
                      ))}
                    </div>
                  )}
                </div>
              </>
            )}

            {/* LMO Navigation */}
            {user?.role === 'LMO' && (
              <Link
                to="/lmo/dashboard"
                className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                  isActive('/lmo/dashboard') ? 'bg-slate-800 text-amber-400 font-bold' : 'text-slate-300 hover:text-white hover:bg-slate-800/50'
                }`}
              >
                Inspections
              </Link>
            )}
          </nav>

          {/* Right: Search + Role Switcher + User */}
          <div className="flex items-center space-x-2">
            {/* Compact Search */}
            <form onSubmit={handleSearch} className="hidden md:flex items-center relative">
              <input
                type="text"
                placeholder="Verify certificate..."
                value={searchCert}
                onChange={(e) => setSearchCert(e.target.value)}
                className="w-40 bg-slate-800/90 text-xs text-white placeholder-slate-500 rounded-lg pl-8 pr-2 py-1.5 border border-slate-700 focus:outline-none focus:border-amber-400 focus:ring-1 focus:ring-amber-400 focus:w-56 transition-all"
              />
              <Search className="h-3.5 w-3.5 text-slate-500 absolute left-2.5 top-2" />
            </form>

            {/* Compact Role Switcher Pill */}
            <div className="hidden md:flex items-center bg-slate-800/80 rounded-lg p-0.5 border border-slate-700/80 text-[11px]">
              {(['TRADER', 'ADMIN', 'LMO'] as const).map((role) => (
                <button
                  key={role}
                  onClick={() => handleRoleSwitch(
                    role,
                    role === 'TRADER' ? '/trader/dashboard' : role === 'ADMIN' ? '/admin/dashboard' : '/lmo/dashboard'
                  )}
                  disabled={switchingRole !== null}
                  className={`px-2 py-1 rounded-md font-semibold transition-colors ${
                    user?.role === role
                      ? 'bg-amber-500 text-slate-950 shadow-xs'
                      : 'text-slate-400 hover:text-white'
                  }`}
                >
                  {switchingRole === role ? '...' : role === 'LMO' ? 'LMO' : role.charAt(0) + role.slice(1).toLowerCase()}
                </button>
              ))}
            </div>

            {/* User Info + Logout */}
            {user ? (
              <div className="flex items-center space-x-1.5">
                <div className="text-right hidden lg:block">
                  <div className="text-[11px] font-semibold text-white leading-tight truncate max-w-[100px]">{user.full_name}</div>
                  <div className="text-[9px] text-amber-400 uppercase font-bold">{user.role}</div>
                </div>
                <button
                  onClick={() => { logout(); navigate('/'); }}
                  title="Logout"
                  className="p-1.5 bg-slate-800 hover:bg-red-600/80 text-slate-400 hover:text-white rounded-lg border border-slate-700 hover:border-red-500 transition-colors"
                >
                  <LogOut className="h-3.5 w-3.5" />
                </button>
              </div>
            ) : (
              <Link
                to="/login"
                className="px-3 py-1.5 bg-amber-500 hover:bg-amber-400 text-slate-950 text-xs font-bold rounded-lg shadow transition-colors"
              >
                Sign In
              </Link>
            )}

            {/* Mobile Hamburger */}
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
        <div className="lg:hidden bg-slate-900 border-t border-slate-800 px-4 py-4 space-y-3">
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

          {/* Mobile Role Switcher */}
          <div className="grid grid-cols-3 gap-1.5 bg-slate-800 p-2 rounded-xl border border-slate-700">
            {(['TRADER', 'ADMIN', 'LMO'] as const).map((role) => (
              <button
                key={role}
                onClick={() => handleRoleSwitch(
                  role,
                  role === 'TRADER' ? '/trader/dashboard' : role === 'ADMIN' ? '/admin/dashboard' : '/lmo/dashboard'
                )}
                className={`py-1.5 rounded text-xs font-bold text-center transition-colors ${
                  user?.role === role ? 'bg-amber-500 text-slate-950' : 'bg-slate-700 text-slate-200 hover:bg-slate-600'
                }`}
              >
                {role === 'LMO' ? 'LMO' : role.charAt(0) + role.slice(1).toLowerCase()}
              </button>
            ))}
          </div>

          {/* Mobile Navigation Links */}
          <div className="space-y-1 text-sm font-medium">
            <Link to="/" onClick={() => setMobileMenuOpen(false)} className="block px-3 py-2 rounded-lg text-slate-200 hover:bg-slate-800">
              Home
            </Link>
            <Link to="/trader/dashboard" onClick={() => setMobileMenuOpen(false)} className="block px-3 py-2 rounded-lg text-slate-200 hover:bg-slate-800">
              Trader Dashboard
            </Link>
            <Link to="/admin/dashboard" onClick={() => setMobileMenuOpen(false)} className="block px-3 py-2 rounded-lg text-slate-200 hover:bg-slate-800">
              Admin Dashboard
            </Link>
            {user?.role === 'ADMIN' && adminSubLinks.map((link) => (
              <Link key={link.path} to={link.path} onClick={() => setMobileMenuOpen(false)} className="block px-3 py-2 pl-6 rounded-lg text-slate-300 hover:bg-slate-800 text-xs">
                {link.label}
              </Link>
            ))}
            <Link to="/lmo/dashboard" onClick={() => setMobileMenuOpen(false)} className="block px-3 py-2 rounded-lg text-slate-200 hover:bg-slate-800">
              LMO Inspections
            </Link>
          </div>
        </div>
      )}
    </header>
  );
};
