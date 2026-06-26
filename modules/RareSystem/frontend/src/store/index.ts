import { create } from 'zustand'
import type {
  Variant,
  ACMGClassification,
  AnalysisSession,
  FilterOptions,
  ChatMessage,
  ClinicalReport,
  ResearchReport,
  GeneAnalysisReport,
} from '@/types'

export interface LLMSettings {
  id: number
  patient_id: number
  is_active: boolean
  provider: string
  provider_name: string | null
  model: string
  base_url: string | null
  temperature: number
  max_tokens: number
  created_at: string
  updated_at: string
}

export interface ProviderInfo {
  code: string
  name: string
  models: string[]
}

interface AppState {
  currentSession: AnalysisSession | null
  variants: Variant[]
  selectedVariant: Variant | null
  classification: ACMGClassification | null
  filters: FilterOptions
  chatMessages: ChatMessage[]
  clinicalReport: ClinicalReport | null
  researchReport: ResearchReport | null
  geneAnalysisReports: GeneAnalysisReport[]
  loading: boolean
  error: string | null
  llmSettings: LLMSettings | null
  providers: ProviderInfo[]

  setCurrentSession: (session: AnalysisSession | null) => void
  setVariants: (variants: Variant[]) => void
  setSelectedVariant: (variant: Variant | null) => void
  setClassification: (classification: ACMGClassification | null) => void
  setFilters: (filters: FilterOptions) => void
  addChatMessage: (message: ChatMessage) => void
  setChatMessages: (messages: ChatMessage[]) => void
  setClinicalReport: (report: ClinicalReport | null) => void
  setResearchReport: (report: ResearchReport | null) => void
  addGeneAnalysisReport: (report: GeneAnalysisReport) => void
  removeGeneAnalysisReport: (id: string) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  setLLMSettings: (settings: LLMSettings | null) => void
  setProviders: (providers: ProviderInfo[]) => void
  reset: () => void
}

const initialState = {
  currentSession: null,
  variants: [],
  selectedVariant: null,
  classification: null,
  filters: {},
  chatMessages: [],
  clinicalReport: null,
  researchReport: null,
  geneAnalysisReports: [],
  loading: false,
  error: null,
  llmSettings: null,
  providers: [],
}

export const useAppStore = create<AppState>((set) => ({
  ...initialState,

  setCurrentSession: (session) => set({ currentSession: session }),
  setVariants: (variants) => set({ variants }),
  setSelectedVariant: (variant) => set({ selectedVariant: variant, classification: null }),
  setClassification: (classification) => set({ classification }),
  setFilters: (filters) => set({ filters }),
  addChatMessage: (message) => set((state) => ({ chatMessages: [...state.chatMessages, message] })),
  setChatMessages: (messages) => set({ chatMessages: messages }),
  setClinicalReport: (report) => set({ clinicalReport: report }),
  setResearchReport: (report) => set({ researchReport: report }),
  addGeneAnalysisReport: (report) => set((state) => ({ 
    geneAnalysisReports: [report, ...state.geneAnalysisReports] 
  })),
  removeGeneAnalysisReport: (id) => set((state) => ({ 
    geneAnalysisReports: state.geneAnalysisReports.filter(r => r.id !== id) 
  })),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
  setLLMSettings: (settings) => set({ llmSettings: settings }),
  setProviders: (providers) => set({ providers }),
  reset: () => set(initialState),
}))
