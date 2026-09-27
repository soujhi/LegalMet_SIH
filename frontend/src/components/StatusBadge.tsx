import React from 'react';
import { ApplicationStatus, VerificationResult, CertificateStatus } from '../types';

export const StatusBadge: React.FC<{ status: ApplicationStatus | VerificationResult | CertificateStatus | string }> = ({ status }) => {
  const getStyle = () => {
    switch (status) {
      case 'CERTIFICATE_ISSUED':
      case 'PASS':
      case 'VALID':
      case 'VERIFIED':
        return 'bg-emerald-50 text-emerald-700 border-emerald-200 ring-emerald-600/20';
      case 'SUBMITTED':
      case 'UNDER_REVIEW':
      case 'IN_PROGRESS':
        return 'bg-blue-50 text-blue-700 border-blue-200 ring-blue-600/20';
      case 'SCHEDULED':
      case 'ASSIGNED':
      case 'FIELD_VERIFICATION':
        return 'bg-indigo-50 text-indigo-700 border-indigo-200 ring-indigo-600/20';
      case 'APPROVED':
        return 'bg-teal-50 text-teal-700 border-teal-200 ring-teal-600/20';
      case 'QUERIED':
      case 'PAYMENT_PENDING':
        return 'bg-amber-50 text-amber-700 border-amber-200 ring-amber-600/20';
      case 'FAILED':
      case 'REJECTED':
      case 'REVOKED':
      case 'NOT_FOUND':
        return 'bg-rose-50 text-rose-700 border-rose-200 ring-rose-600/20';
      case 'EXPIRED':
        return 'bg-slate-100 text-slate-700 border-slate-300 ring-slate-600/20';
      default:
        return 'bg-slate-50 text-slate-700 border-slate-200 ring-slate-600/20';
    }
  };

  const getLabel = () => {
    return status.replace(/_/g, ' ');
  };

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border ring-1 ring-inset ${getStyle()}`}>
      {getLabel()}
    </span>
  );
};
