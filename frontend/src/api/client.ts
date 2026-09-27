const API_BASE = '/api';

export class ApiClient {
  private static getToken(): string | null {
    return localStorage.getItem('legalmet_token');
  }

  public static setToken(token: string) {
    localStorage.setItem('legalmet_token', token);
  }

  public static clearToken() {
    localStorage.removeItem('legalmet_token');
    localStorage.removeItem('legalmet_user');
  }

  public static async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const token = this.getToken();
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string>),
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Request failed' }));
      throw new Error(errorData.detail || `HTTP Error ${response.status}`);
    }

    return response.json();
  }

  // Auth
  static login(data: any) {
    return this.request<any>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  static register(data: any) {
    return this.request<any>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  static getMe() {
    return this.request<any>('/auth/me');
  }

  // Instruments
  static getInstruments() {
    return this.request<any[]>('/instruments');
  }

  static getCategories() {
    return this.request<any[]>('/instruments/categories');
  }

  static getModels(params?: { category_id?: number; q?: string; accuracy_class?: string; manufacturer?: string; skip?: number; limit?: number }) {
    const query = new URLSearchParams();
    if (params?.category_id) query.append('category_id', params.category_id.toString());
    if (params?.q) query.append('q', params.q);
    if (params?.accuracy_class) query.append('accuracy_class', params.accuracy_class);
    if (params?.manufacturer) query.append('manufacturer', params.manufacturer);
    if (params?.skip !== undefined) query.append('skip', params.skip.toString());
    if (params?.limit !== undefined) query.append('limit', params.limit.toString());
    const qs = query.toString();
    return this.request<any[]>(qs ? `/instruments/models?${qs}` : '/instruments/models');
  }

  static getModel(id: number) {
    return this.request<any>(`/instruments/models/${id}`);
  }

  static updateModel(id: number, data: any) {
    return this.request<any>(`/instruments/models/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  static getDataQualityStats() {
    return this.request<any>('/instruments/models/data-quality');
  }

  static createInstrument(data: any) {
    return this.request<any>('/instruments', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Applications
  static getApplications(statusFilter?: string) {
    const url = statusFilter ? `/applications?status_filter=${statusFilter}` : '/applications';
    return this.request<any[]>(url);
  }

  static getApplication(id: number) {
    return this.request<any>(`/applications/${id}`);
  }

  static createApplication(data: any) {
    return this.request<any>('/applications', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  static updateApplicationStatus(id: number, status: string, remarks?: string) {
    return this.request<any>(`/applications/${id}/status`, {
      method: 'PUT',
      body: JSON.stringify({ status, remarks }),
    });
  }

  static getApplicationTimeline(id: number) {
    return this.request<any[]>(`/applications/${id}/timeline`);
  }

  // Scheduling
  static getOfficers() {
    return this.request<any[]>('/schedule/officers');
  }

  static getScheduledApplications() {
    return this.request<any[]>('/schedule');
  }

  static assignOfficer(applicationId: number, data: { officer_id: number; scheduled_at: string; remarks?: string }) {
    return this.request<any>(`/schedule/assign/${applicationId}`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Verification & Rule Engine
  static startVerification(applicationId: number, data: any = {}) {
    return this.request<any>(`/verification/start/${applicationId}`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  static completeVerification(applicationId: number, data: any) {
    return this.request<any>(`/verification/${applicationId}/complete`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  static evaluateRule(data: any) {
    return this.request<any>('/rules/evaluate', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  static getRules() {
    return this.request<any[]>('/rules');
  }

  // Certificates & Public Verification
  static getCertificates() {
    return this.request<any[]>('/certificates');
  }

  static getCertificate(id: number) {
    return this.request<any>(`/certificates/${id}`);
  }

  static verifyPublic(certificateNumber: string) {
    return this.request<any>(`/public/verify/${encodeURIComponent(certificateNumber)}`);
  }

  // OCR
  static getOCRDocuments(verifiedOnly?: boolean) {
    const url = verifiedOnly !== undefined ? `/ocr?verified_only=${verifiedOnly}` : '/ocr';
    return this.request<any[]>(url);
  }

  static validateOCRDocument(id: number, data: any) {
    return this.request<any>(`/ocr/${id}/validate`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  // Analytics & Audit
  static getDashboardMetrics() {
    return this.request<any>('/analytics/dashboard');
  }

  static getAuditLogs() {
    return this.request<any[]>('/audit-logs');
  }
}
