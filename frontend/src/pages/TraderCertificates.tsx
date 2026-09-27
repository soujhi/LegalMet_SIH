import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ApiClient } from '../api/client';
import { Certificate } from '../types';
import { Award, Download, QrCode, Calendar, Scale, MapPin, CheckCircle2, Lock } from 'lucide-react';

export const TraderCertificates: React.FC = () => {
  const [certificates, setCertificates] = useState<Certificate[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadCerts = async () => {
      try {
        const certs = await ApiClient.getCertificates();
        setCertificates(certs);
      } catch (err) {
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    };
    loadCerts();
  }, []);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      <div>
        <h1 className="text-2xl font-black text-slate-900 flex items-center gap-2">
          <Award className="h-6 w-6 text-amber-500" /> Digital Certificate Vault
        </h1>
        <p className="text-xs text-slate-500 mt-1">
          Statutory Legal Metrology Certificates with cryptographic SHA-256 signatures and QR verification codes.
        </p>
      </div>

      {certificates.length === 0 ? (
        <div className="bg-white rounded-2xl border border-slate-200 p-12 text-center shadow-sm">
          <Award className="h-12 w-12 text-slate-300 mx-auto mb-3" />
          <h3 className="font-bold text-slate-700 text-base">No Certificates Issued Yet</h3>
          <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
            Once an LMO conducts field verification and test observations pass statutory MPE tolerance, verified certificates will appear here.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {certificates.map(cert => (
            <div key={cert.id} className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm hover:shadow-md transition-all flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between pb-3 border-b border-slate-100 mb-4">
                  <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-800 border border-emerald-200 flex items-center gap-1">
                    <CheckCircle2 className="h-3 w-3" /> {cert.status}
                  </span>
                  <span className="text-[10px] text-slate-400 font-mono">Issued {new Date(cert.issue_date).toLocaleDateString()}</span>
                </div>

                <div className="font-mono font-black text-base text-blue-900 mb-1">
                  {cert.certificate_number}
                </div>
                <div className="text-xs text-slate-600 font-medium">
                  {cert.instrument?.model?.manufacturer || 'Standard Manufacturer'}
                </div>

                <div className="mt-4 bg-slate-50 p-3 rounded-xl border border-slate-100 space-y-1 text-xs text-slate-700">
                  <div className="flex justify-between">
                    <span className="text-slate-500">Serial No:</span>
                    <span className="font-mono font-bold text-slate-900">{cert.instrument?.serial_number}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Capacity:</span>
                    <span className="font-bold">{cert.instrument?.capacity} {cert.instrument?.unit}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Valid Until:</span>
                    <span className="font-bold text-emerald-800">{new Date(cert.valid_until).toLocaleDateString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Inspector:</span>
                    <span className="font-medium text-slate-900">{cert.issuing_officer_name}</span>
                  </div>
                </div>

                <div className="mt-3 p-2 bg-slate-900 text-slate-300 rounded-lg text-[10px] font-mono truncate flex items-center gap-1.5">
                  <Lock className="h-3 w-3 text-amber-400 shrink-0" />
                  <span className="truncate">Hash: {cert.certificate_hash}</span>
                </div>
              </div>

              <div className="mt-6 pt-3 border-t border-slate-100 flex items-center gap-2">
                <Link
                  to={`/verify/${encodeURIComponent(cert.certificate_number)}`}
                  className="flex-1 py-2 px-3 bg-amber-500 hover:bg-amber-600 text-slate-950 font-bold text-xs rounded-xl shadow-xs text-center flex items-center justify-center gap-1.5 transition-colors"
                >
                  <QrCode className="h-3.5 w-3.5" /> Scan / Verify
                </Link>
                {cert.pdf_url && (
                  <a
                    href={`/api/certificates/${cert.id}/pdf`}
                    target="_blank"
                    rel="noreferrer"
                    className="p-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl transition-colors"
                    title="Download Statutory PDF"
                  >
                    <Download className="h-4 w-4" />
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
