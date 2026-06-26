import axios, { AxiosError, AxiosInstance, AxiosRequestConfig, CancelTokenSource } from 'axios'
import type {
  Variant,
  ACMGClassification,
  Patient,
  ClinicalReport,
  ResearchReport,
  AnalysisSession,
  FilterOptions,
  PaginationParams,
  PaginatedResponse,
  ChatMessage,
  ChatReference,
  PathwayAnalysisResponse,
  PathwayDetailResponse,
} from '@/types'

const API_BASE = '/api'
const DEFAULT_TIMEOUT = 30000
const MAX_RETRIES = 3
const RETRY_DELAY = 1000

export class APIError extends Error {
  code: string
  status?: number
  details?: unknown

  constructor(message: string, code: string, status?: number, details?: unknown) {
    super(message)
    this.name = 'APIError'
    this.code = code
    this.status = status
    this.details = details
  }
}

export class NetworkError extends APIError {
  constructor(message: string = 'Network error. Please check your connection.') {
    super(message, 'NETWORK_ERROR')
    this.name = 'NetworkError'
  }
}

export class TimeoutError extends APIError {
  constructor(message: string = 'Request timed out. Please try again.') {
    super(message, 'TIMEOUT_ERROR')
    this.name = 'TimeoutError'
  }
}

export class ValidationError extends APIError {
  constructor(message: string, details?: unknown) {
    super(message, 'VALIDATION_ERROR', 400, details)
    this.name = 'ValidationError'
  }
}

export class AuthenticationError extends APIError {
  constructor(message: string = 'Authentication required.') {
    super(message, 'AUTH_ERROR', 401)
    this.name = 'AuthenticationError'
  }
}

export class NotFoundError extends APIError {
  constructor(message: string = 'Resource not found.') {
    super(message, 'NOT_FOUND', 404)
    this.name = 'NotFoundError'
  }
}

export class ServerError extends APIError {
  constructor(message: string = 'Server error. Please try again later.', status: number = 500) {
    super(message, 'SERVER_ERROR', status)
    this.name = 'ServerError'
  }
}

interface ErrorResponse {
  detail?: string
  message?: string
  errors?: Record<string, string[]>
}

function parseError(error: AxiosError<ErrorResponse>): APIError {
  if (!error.response) {
    if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
      return new TimeoutError()
    }
    return new NetworkError()
  }

  const { status, data } = error.response
  const message = data?.detail || data?.message || error.message

  switch (status) {
    case 400:
      return new ValidationError(message, data?.errors)
    case 401:
      return new AuthenticationError(message)
    case 403:
      return new APIError(message, 'FORBIDDEN', 403)
    case 404:
      return new NotFoundError(message)
    case 422:
      return new ValidationError(message, data?.errors)
    case 429:
      return new APIError('Too many requests. Please wait and try again.', 'RATE_LIMIT', 429)
    default:
      if (status >= 500) {
        return new ServerError(message, status)
      }
      return new APIError(message, 'UNKNOWN_ERROR', status)
  }
}

async function delay(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms))
}

class APIService {
  private client: AxiosInstance
  private cancelTokens: Map<string, CancelTokenSource> = new Map()

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE,
      timeout: DEFAULT_TIMEOUT,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    this.client.interceptors.request.use(
      (config) => {
        const requestId = `${config.method}-${config.url}-${Date.now()}`
        config.metadata = { requestId, startTime: Date.now() }
        
        console.debug(`[API] Request: ${config.method?.toUpperCase()} ${config.url}`)
        return config
      },
      (error) => {
        console.error('[API] Request error:', error)
        return Promise.reject(error)
      }
    )

    this.client.interceptors.response.use(
      (response) => {
        const { config } = response
        const duration = config?.metadata?.startTime 
          ? Date.now() - config.metadata.startTime 
          : 0
        console.debug(
          `[API] Response: ${response.status} ${config?.url} (${duration}ms)`
        )
        return response
      },
      async (error: AxiosError<ErrorResponse>) => {
        const { config } = error
        
        if (!config) {
          return Promise.reject(parseError(error))
        }
        
        if (config.metadata?.retryCount === undefined) {
          config.metadata = { retryCount: 0 }
        }

        const isRetryable = 
          !error.response || 
          error.response.status >= 500 ||
          error.code === 'ECONNABORTED'

        if (isRetryable && (config.metadata?.retryCount ?? 0) < MAX_RETRIES) {
          config.metadata = { ...config.metadata, retryCount: (config.metadata?.retryCount ?? 0) + 1 }
          const retryDelay = RETRY_DELAY * Math.pow(2, (config.metadata?.retryCount ?? 1) - 1)
          
          console.debug(
            `[API] Retrying ${config.url} (attempt ${config.metadata?.retryCount}/${MAX_RETRIES})`
          )
          
          await delay(retryDelay)
          return this.client.request(config)
        }

        console.error(
          '[API] Error:',
          error.response?.status,
          error.response?.data || error.message
        )

        const apiError = parseError(error)
        return Promise.reject(apiError)
      }
    )
  }

  cancelRequest(requestKey: string): void {
    const source = this.cancelTokens.get(requestKey)
    if (source) {
      source.cancel('Request cancelled by user')
      this.cancelTokens.delete(requestKey)
    }
  }

  cancelAllRequests(): void {
    this.cancelTokens.forEach((source) => {
      source.cancel('All requests cancelled')
    })
    this.cancelTokens.clear()
  }

  private async request<T>(
    config: AxiosRequestConfig
  ): Promise<T> {
    const { data } = await this.client.request<T>(config)
    return data
  }

  async healthCheck(): Promise<{ status: string }> {
    return this.request({ method: 'GET', url: '/health' })
  }

  async uploadVCF(
    file: File, 
    patientId: string, 
    onProgress?: (progress: number) => void,
    patientInfo?: {
      name?: string
      age?: number
      sex?: string
      ethnicity?: string
      diagnosis_description?: string
      medical_history?: string
      hpo_terms?: Array<{ phrase: string; hpo_id: string }>
    },
    vepOptions?: {
      hgvs?: boolean
      no_pick?: boolean
      format?: string
      fork?: number
    },
    hpoJobId?: string
  ): Promise<{ vcf_file_id: string; patient_id: string; total_variants: number; message: string; vep_status: string; vep_job_id: string | null; vep_job_db_id: number | null }> {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('patient_id', patientId)
    if (patientInfo?.name) formData.append('patient_name', patientInfo.name)
    if (patientInfo?.age !== undefined) formData.append('age', String(patientInfo.age))
    if (patientInfo?.sex) formData.append('sex', patientInfo.sex)
    if (patientInfo?.ethnicity) formData.append('ethnicity', patientInfo.ethnicity)
    if (patientInfo?.diagnosis_description) formData.append('diagnosis_description', patientInfo.diagnosis_description)
    if (patientInfo?.medical_history) formData.append('medical_history', patientInfo.medical_history)
    if (patientInfo?.hpo_terms) formData.append('hpo_terms', JSON.stringify(patientInfo.hpo_terms))
    if (vepOptions) {
      formData.append('vep_hgvs', vepOptions.hgvs !== false ? 'true' : 'false')
      formData.append('vep_no_pick', vepOptions.no_pick ? 'true' : 'false')
      formData.append('vep_format', vepOptions.format || 'vcf')
      formData.append('vep_fork', String(vepOptions.fork || 1))
    }
    if (hpoJobId) {
      formData.append('hpo_job_id', hpoJobId)
    }

    return this.request({
      method: 'POST',
      url: '/variants/upload',
      data: formData,
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 300000,
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          onProgress(progress)
        }
      },
    })
  }

  async getVariants(
    vcfFileId: string,
    filters?: FilterOptions,
    pagination?: PaginationParams
  ): Promise<PaginatedResponse<Variant>> {
    const params = { ...filters, ...pagination }
    return this.request({
      method: 'GET',
      url: `/variants/${vcfFileId}`,
      params,
    })
  }

  async getVariant(variantId: string): Promise<Variant> {
    return this.request({
      method: 'GET',
      url: `/variants/detail/${variantId}`,
    })
  }

  async getACMGClassification(variantId: string): Promise<ACMGClassification> {
    return this.request({
      method: 'GET',
      url: `/acmg/${variantId}`,
    })
  }

  async runACMGAnalysis(
    variantId: string, 
    context?: Record<string, unknown>
  ): Promise<ACMGClassification> {
    return this.request({
      method: 'POST',
      url: `/acmg/${variantId}/analyze`,
      data: context,
    })
  }

  async createPatient(patient: Omit<Patient, 'id'>): Promise<Patient> {
    return this.request({
      method: 'POST',
      url: '/patients',
      data: patient,
    })
  }

  async getPatient(patientId: string): Promise<Patient> {
    return this.request({
      method: 'GET',
      url: `/patients/${patientId}`,
    })
  }

  async getAnalysisSession(sessionId: string): Promise<AnalysisSession> {
    return this.request({
      method: 'GET',
      url: `/analysis/${sessionId}`,
    })
  }

  async createAnalysisSession(
    patientId: string, 
    vcfFileId: string
  ): Promise<AnalysisSession> {
    return this.request({
      method: 'POST',
      url: '/analysis',
      data: { patient_id: patientId, vcf_file_id: vcfFileId },
    })
  }

  async generateClinicalReport(sessionId: string): Promise<ClinicalReport> {
    return this.request({
      method: 'POST',
      url: '/reports/clinical',
      data: { session_id: sessionId },
    })
  }

  async generateResearchReport(sessionId: string): Promise<ResearchReport> {
    return this.request({
      method: 'POST',
      url: '/reports/research',
      data: { session_id: sessionId },
    })
  }

  async getClinicalReport(reportId: string): Promise<ClinicalReport> {
    return this.request({
      method: 'GET',
      url: `/reports/clinical/${reportId}`,
    })
  }

  async getResearchReport(reportId: string): Promise<ResearchReport> {
    return this.request({
      method: 'GET',
      url: `/reports/research/${reportId}`,
    })
  }

  async sendChatMessage(
    patientId: number, 
    message: string, 
    sessionToken?: string
  ): Promise<ChatMessage> {
    const response = await this.request<{
      id: string
      role: string
      content: string
      timestamp: string
      references?: Array<{id: string; type: string; label: string; url?: string}>
      confidence?: number
    }>({
      method: 'POST',
      url: `/chat/${patientId}`,
      data: { message, session_token: sessionToken },
    })
    return {
      id: response.id,
      role: response.role as 'user' | 'assistant',
      content: response.content,
      timestamp: response.timestamp,
      references: response.references?.map(r => ({
        id: r.id,
        type: r.type as 'variant' | 'report' | 'evidence',
        label: r.label,
        url: r.url
      })),
      confidence: response.confidence
    }
  }

  async getChatHistory(sessionToken: string): Promise<ChatMessage[]> {
    const response = await this.request<{
      messages: Array<{
        id: string
        role: string
        content: string
        timestamp: string
        references?: Array<{id: string; type: string; label: string; url?: string}>
        confidence?: number
      }>
    }>({
      method: 'GET',
      url: `/chat/${sessionToken}`,
    })
    return response.messages.map(m => ({
      id: m.id,
      role: m.role as 'user' | 'assistant',
      content: m.content,
      timestamp: m.timestamp,
      references: m.references?.map(r => ({
        id: r.id,
        type: r.type as 'variant' | 'report' | 'evidence',
        label: r.label,
        url: r.url
      })),
      confidence: m.confidence
    }))
  }

  async askQuestion(
    question: string, 
    patientId: number, 
    sessionToken?: string
  ): Promise<{answer: string; sources: ChatReference[]; confidence: number; sessionToken: string}> {
    const response = await this.request<{
      answer: string
      sources: Array<{id: string; type: string; label: string; url?: string}>
      confidence: number
      session_token: string
    }>({
      method: 'POST',
      url: '/chat/qa',
      data: { question, patient_id: patientId, session_token: sessionToken }
    })
    return {
      answer: response.answer,
      sources: response.sources.map(s => ({
        id: s.id,
        type: s.type as 'variant' | 'report' | 'evidence',
        label: s.label,
        url: s.url
      })),
      confidence: response.confidence,
      sessionToken: response.session_token
    }
  }

  async indexPatientDocuments(patientId: number): Promise<{message: string}> {
    return this.request({
      method: 'POST',
      url: `/chat/index/patient/${patientId}`
    })
  }

  async endChatSession(sessionToken: string): Promise<{message: string}> {
    return this.request({
      method: 'DELETE',
      url: `/chat/session/${sessionToken}`
    })
  }

  async downloadReport(reportId: string, type: 'clinical' | 'research'): Promise<Blob> {
    const response = await this.client.get(`/reports/${type}/${reportId}/download`, {
      responseType: 'blob',
    })
    return response.data
  }

  async exportVariants(vcfFileId: string, format: 'csv' | 'json' = 'json'): Promise<Blob> {
    const response = await this.client.get(`/variants/${vcfFileId}/export`, {
      params: { format },
      responseType: 'blob',
    })
    return response.data
  }

  async getLLMSettings(patientId: number): Promise<any> {
    return this.request({
      method: 'GET',
      url: `/settings/patient/${patientId}`,
    })
  }

  async saveLLMSettings(patientId: number, settings: {
    provider: string
    api_key: string
    model: string
    base_url?: string | null
    temperature: number
    max_tokens: number
  }): Promise<any> {
    return this.request({
      method: 'POST',
      url: `/settings/patient/${patientId}`,
      data: settings,
    })
  }

  async getProviders(): Promise<any[]> {
    return this.request({
      method: 'GET',
      url: '/settings/providers',
    })
  }

  async getCases(): Promise<{cases: any[], total: number}> {
    return this.request({
      method: 'GET',
      url: '/cases',
    })
  }

  async getCase(patientId: number): Promise<any> {
    return this.request({
      method: 'GET',
      url: `/cases/${patientId}`,
    })
  }

  async deleteCase(patientId: number): Promise<{message: string, patient_id: number}> {
    return this.request({
      method: 'DELETE',
      url: `/cases/${patientId}`,
    })
  }

  async getSkills(): Promise<any[]> {
    return this.request({
      method: 'GET',
      url: '/skills',
    })
  }

  async getSkillConfigs(): Promise<any[]> {
    return this.request({
      method: 'GET',
      url: '/skills/config',
    })
  }

  async updateSkillConfig(skillName: string, config: { is_enabled?: boolean; config?: Record<string, unknown> }): Promise<any> {
    return this.request({
      method: 'PUT',
      url: `/skills/config/${skillName}`,
      data: config,
    })
  }

  async executeSkill(skillName: string, query: string, patientId: number): Promise<any> {
    return this.request({
      method: 'POST',
      url: `/skills/${skillName}/execute`,
      data: { query, patient_id: patientId },
    })
  }

  async searchPubmed(
    query: string,
    maxResults: number = 10,
    includeAbstracts: boolean = true
  ): Promise<{
    articles: Array<{
      pmid: string
      title: string
      authors: string[]
      journal: string
      year: string
      abstract: string
      url: string
      doi: string
    }>
    total_count: number
    query: string
  }> {
    return this.request({
      method: 'GET',
      url: '/pubmed/search',
      params: { query, max_results: maxResults, include_abstracts: includeAbstracts },
    })
  }

  async getGenes(vcfFileId: string): Promise<{ genes: any[]; total: number }> {
    return this.request({
      method: 'GET',
      url: `/genes/${vcfFileId}`,
    })
  }

  async getGeneVariants(vcfFileId: string, geneName: string): Promise<{ gene: string; variants: any[]; total: number }> {
    return this.request({
      method: 'GET',
      url: `/genes/${vcfFileId}/${geneName}`,
    })
  }

  async getGeneInfo(geneName: string): Promise<any> {
    return this.request({
      method: 'GET',
      url: `/genes/info/${geneName}`,
    })
  }

  async extractHPO(patientId: string, clinicalNote: string): Promise<{
    patient_id: string
    status: string
    terms: Array<{
      phrase: string
      category: string
      hpo_id: string
    }>
  }> {
    return this.request({
      method: 'POST',
      url: '/hpo/extract',
      data: { patient_id: patientId, clinical_note: clinicalNote },
      timeout: 150000,
    })
  }

  async extractHPOAsync(patientId: string, clinicalNote: string): Promise<{
    job_id: string
    patient_id: string
    status: string
  }> {
    return this.request({
      method: 'POST',
      url: '/hpo/extract-async',
      data: { patient_id: patientId, clinical_note: clinicalNote },
    })
  }

  async getHPOJobStatus(jobId: string): Promise<{
    job_id: string
    patient_id: number
    status: string
    results: Array<{ phrase: string; category: string; hpo_id: string }> | null
    error: string | null
  }> {
    return this.request({
      method: 'GET',
      url: `/hpo/status/${jobId}`,
    })
  }

  async getVEPJobStatus(jobId: string): Promise<{
    job_id: string
    status: string
    input_filename: string | null
    input_bytes: number | null
    options: Record<string, unknown> | null
    status_url: string | null
    result_url: string | null
    log_url: string | null
    rows: number | null
    error: string | null
    created_at: string | null
    updated_at: string | null
    vep_annotated_count: number | null
  }> {
    return this.request({
      method: 'GET',
      url: `/vep/jobs/${jobId}/status`,
    })
  }

  async lookupHpoTerm(hpoId: string): Promise<{
    hpo_id: string
    name: string
    definition?: string
    synonyms?: string[]
    category?: string
  }> {
    return this.request({
      method: 'GET',
      url: `/hpo/lookup/${hpoId}`,
    })
  }

  async updatePatientHpoTerms(patientId: number, hpoTerms: Array<{ phrase: string; hpo_id: string; category?: string; display_category?: string }>): Promise<{ message: string; patient_id: number }> {
    return this.request({
      method: 'PUT',
      url: `/cases/${patientId}/hpo-terms`,
      data: { hpo_terms: hpoTerms },
    })
  }

  async updateHpoTermCategory(patientId: number, hpoId: string, displayCategory: string): Promise<{ message: string; patient_id: number; hpo_id: string; display_category: string }> {
    return this.request({
      method: 'PATCH',
      url: `/cases/${patientId}/hpo-terms/category`,
      data: { hpo_id: hpoId, display_category: displayCategory },
    })
  }

  async analyzePathways(genes: string[]): Promise<PathwayAnalysisResponse> {
    return this.request({
      method: 'POST',
      url: '/pathways/analyze',
      data: { genes },
    })
  }

  async analyzeVcfPathways(vcfFileId: string): Promise<PathwayAnalysisResponse> {
    return this.request({
      method: 'POST',
      url: `/pathways/analyze/vcf/${vcfFileId}`,
    })
  }

  async getPathwayDetail(stId: string): Promise<PathwayDetailResponse> {
    return this.request({
      method: 'GET',
      url: `/pathways/detail/${stId}`,
    })
  }

  async getPathwaysForGene(gene: string): Promise<{ gene: string; pathways: unknown[]; count: number }> {
    return this.request({
      method: 'GET',
      url: `/pathways/gene/${gene}`,
    })
  }

  async submitPhenotypeHpoJob(
    vcfFileId: number,
    hpoTerms: string[]
  ): Promise<{ uid: string; status: string; message: string }> {
    return this.request({
      method: 'POST',
      url: '/phenotype-hpo/submit',
      data: { vcf_file_id: vcfFileId, hpo_terms: hpoTerms },
      timeout: 60000,
    })
  }

  async getPhenotypeHpoJobStatus(uid: string): Promise<{
    uid: string
    status: string
    phase: string
    message: string
  }> {
    return this.request({
      method: 'GET',
      url: `/phenotype-hpo/status/${uid}`,
    })
  }

  async getPhenotypeHpoResults(uid: string): Promise<{
    scores: Array<{
      gene_symbol: string
      hgnc_id: string
      gene_score: number
      conclusion_code: string
      best_disease_score: number
      best_disease_name: string
      best_omim_id: string
      best_orpha_id: string
      best_mondo_id: string
      best_disease_source_dbs: string
      best_disease_match_status: string
      mapping_basis: string
      second_best_disease_score: number
      score_gap_to_second_best: number
      disease_profile_count: number
      input_hpo_count: number
      scoring_hpo_count: number
      matched_hpo_count: number
      unmatched_hpo_count: number
      mean_input_hpo_ic: number
      candidate_variant_count_in_gene: number
      gene_sources: string
      best_term_evidence_summary: string
      db_versions: string
      warning: string
      sample_id: string
      gene_rank: number
    }>
    total: number
  }> {
    return this.request({
      method: 'GET',
      url: `/phenotype-hpo/results/${uid}`,
    })
  }

  async submitPpiJob(
    vcfFileId: number,
    hpoJobUid: string,
    hpoTerms: string[]
  ): Promise<{ job_id: string; status: string; message: string }> {
    return this.request({
      method: 'POST',
      url: '/ppi-score/submit',
      data: { vcf_file_id: vcfFileId, hpo_job_uid: hpoJobUid, hpo_terms: hpoTerms },
      timeout: 60000,
    })
  }

  async getPpiJobStatus(jobId: string): Promise<{
    job_id: string
    status: string
    message: string
  }> {
    return this.request({
      method: 'GET',
      url: `/ppi-score/status/${jobId}`,
    })
  }

  async getPpiResults(jobId: string): Promise<{
    scores: Array<{
      gene: string
      disease_score: number
      tissue_score: number
      topology_score: number
      final_score: number
      rank: number
      disease_evidence: string
      tissue_evidence: string
      topology_evidence: string
      neighbor_genes: string
      hpo_match_count: number
    }>
    total: number
  }> {
    return this.request({
      method: 'GET',
      url: `/ppi-score/results/${jobId}`,
    })
  }

  async streamReport(
    request: {
      vcf_file_id: number
      hpo_job_uid?: string
      ppi_job_id?: string
      hpo_terms?: string[]
      symptom_text?: string
      genes?: string[]
      top_n?: number
      k?: number
    },
    onEvent: (event: unknown) => void,
    onError: (error: Error) => void,
    onComplete: () => void
  ): Promise<void> {
    const url = `${API_BASE}/report/stream`
    
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const reader = response.body?.getReader()
      if (!reader) {
        throw new Error('No response body')
      }

      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (line.startsWith('data:')) {
            const dataStr = line.substring(5).trim()
            if (dataStr) {
              try {
                const event = JSON.parse(dataStr)
                onEvent(event)
              } catch {
                console.warn('Failed to parse SSE data:', dataStr)
              }
            }
          }
        }
      }

      onComplete()
    } catch (error) {
      onError(error instanceof Error ? error : new Error(String(error)))
    }
  }

  async downloadReportPdf(runId: string): Promise<Blob> {
    const response = await fetch(`${API_BASE}/report/${runId}/pdf`)
    if (!response.ok) {
      throw new Error(`Failed to download PDF: ${response.status}`)
    }
    return response.blob()
  }
}

declare module 'axios' {
  interface AxiosRequestConfig {
    metadata?: {
      requestId?: string
      startTime?: number
      retryCount?: number
    }
  }
}

export const api = new APIService()
export default api
