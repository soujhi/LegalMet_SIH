import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Scale, Lock, Mail, ArrowRight, UserCheck, ShieldAlert } from 'lucide-react';

export const Login: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const { login, quickLogin } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsSubmitting(true);
    try {
      await login(email, password);
      // Route appropriately based on saved user state
      navigate('/');
    } catch (err: any) {
      setError(err.message || 'Login failed. Please verify credentials.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleQuick = async (role: 'ADMIN' | 'LMO' | 'TRADER') => {
    setError('');
    setIsSubmitting(true);
    try {
      await quickLogin(role);
      if (role === 'TRADER') navigate('/trader/dashboard');
      else if (role === 'ADMIN') navigate('/admin/dashboard');
      else if (role === 'LMO') navigate('/lmo/dashboard');
    } catch (err: any) {
      setError(err.message || 'Quick login failed.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-100 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="flex justify-center">
          <div className="p-3 bg-[#0F2942] rounded-2xl shadow-lg">
            <Scale className="h-10 w-10 text-amber-400" />
          </div>
        </div>
        <h2 className="mt-4 text-center text-2xl font-black tracking-tight text-slate-900">
          LegalMet <span className="text-amber-500">Verify</span>
        </h2>
        <p className="mt-1 text-center text-xs text-slate-600 font-medium uppercase tracking-wider">
          Official Legal Metrology Verification System (SIH26036)
        </p>
      </div>

      <div className="mt-6 sm:mx-auto sm:w-full sm:max-w-md px-4">
        {/* Quick Demo Login Bar */}
        <div className="bg-amber-50 border border-amber-200 rounded-2xl p-4 mb-4 shadow-sm">
          <div className="flex items-center gap-2 mb-2 text-xs font-bold text-amber-900 uppercase">
            <UserCheck className="h-4 w-4 text-amber-600" /> Instant Demo Role Access
          </div>
          <div className="grid grid-cols-3 gap-2">
            <button
              onClick={() => handleQuick('TRADER')}
              disabled={isSubmitting}
              className="py-2 px-3 bg-white hover:bg-orange-50 border border-amber-300 rounded-xl text-xs font-bold text-orange-800 shadow-xs hover:border-orange-500 transition-all text-center"
            >
              Trader (Patel Agro)
            </button>
            <button
              onClick={() => handleQuick('ADMIN')}
              disabled={isSubmitting}
              className="py-2 px-3 bg-white hover:bg-blue-50 border border-amber-300 rounded-xl text-xs font-bold text-blue-800 shadow-xs hover:border-blue-500 transition-all text-center"
            >
              Admin (Rajesh V.)
            </button>
            <button
              onClick={() => handleQuick('LMO')}
              disabled={isSubmitting}
              className="py-2 px-3 bg-white hover:bg-emerald-50 border border-amber-300 rounded-xl text-xs font-bold text-emerald-800 shadow-xs hover:border-emerald-500 transition-all text-center"
            >
              LMO (Inspector)
            </button>
          </div>
        </div>

        <div className="bg-white py-8 px-6 shadow-xl rounded-2xl border border-slate-200 sm:px-8">
          {error && (
            <div className="mb-4 p-3 bg-rose-50 border border-rose-200 text-rose-700 text-xs font-semibold rounded-xl flex items-center gap-2">
              <ShieldAlert className="h-4 w-4 shrink-0" /> {error}
            </div>
          )}

          <form className="space-y-4" onSubmit={handleSubmit}>
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">
                Official Email Address
              </label>
              <div className="relative">
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@domain.gov.in"
                  className="w-full pl-9 pr-3 py-2 text-sm rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-amber-500"
                />
                <Mail className="h-4 w-4 text-slate-400 absolute left-3 top-3" />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">
                Password
              </label>
              <div className="relative">
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full pl-9 pr-3 py-2 text-sm rounded-xl border border-slate-300 focus:outline-none focus:ring-2 focus:ring-amber-500"
                />
                <Lock className="h-4 w-4 text-slate-400 absolute left-3 top-3" />
              </div>
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full mt-2 py-2.5 px-4 bg-[#0F2942] hover:bg-slate-800 text-white font-bold text-sm rounded-xl shadow transition-all flex items-center justify-center gap-2"
            >
              {isSubmitting ? 'Authenticating...' : 'Sign In'} <ArrowRight className="h-4 w-4" />
            </button>
          </form>

          <div className="mt-6 text-center text-xs text-slate-500">
            Need to register a new trader account?{' '}
            <Link to="/register" className="font-bold text-blue-600 hover:text-blue-800 underline">
              Register Establishment
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};
