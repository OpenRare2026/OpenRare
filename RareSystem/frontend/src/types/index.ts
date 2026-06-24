export type VariantType = 'SNV' | 'INDEL' | 'STR' | 'CNV'

export type ClassificationCategory =
  | 'Pathogenic'
  | 'Likely Pathogenic'
  | 'Variant of Uncertain Significance'
  | 'Likely Benign'
  | 'Benign'

export type EvidenceStrength =
  | 'pathogenic_very_strong'
  | 'pathogenic_strong'
  | 'pathogenic_moderate'
  | 'pathogenic_supporting'
  | 'benign_standalone'
  | 'benign_strong'
  | 'benign_supporting'

export type EvidenceDirection = 'pathogenic' | 'benign'

export interface Variant {
  id: string
  chromosome: string
  position: number
  ref: string
  alt: string
  variant_type: VariantType
  gene: string
  transcript?: string
  all_genes?: string
  consequence?: string
  impact?: string
  hgvs_c?: string
  hgvs_p?: string
  cdna_position?: string
  cds_position?: string
  protein_position?: string
  amino_acids?: string
  codons?: string
  exon?: string
  intron?: string
  strand?: string
  protein_domains?: string
  revel_score?: number
  cadd?: number
  gnomad_popmax_af?: number
  gnomad_eas_af?: number
  gnomad_nhomalt?: number
  spliceai_ds_max?: number
  spliceai_type?: string
  loftee_lof_flag?: string
  loftee_lof_filter?: string
  clinvar_significance?: string
  clinvar_review_status?: string
  clinvar_star_rating?: number
  pathogenic_rank?: string
  evidence_summary?: string
  quality?: number
  gnomad_af?: number
  clinvar_status?: string
  sift?: string
  polyphen?: string
  vep_annotated?: boolean
  predictions?: {
    sift?: number
    polyphen?: number
    cadd?: number
    revel?: number
    spliceai?: number
  }
  created_at?: string
}

export interface CriterionResult {
  criterion_code: string
  criterion_name: string
  is_met: boolean
  evidence_strength: EvidenceStrength
  direction: EvidenceDirection
  score: number
  description: string
  evidence_sources: string[]
  confidence: number
  metadata?: Record<string, unknown>
}

export interface ACMGClassification {
  variant_id: string
  classification: ClassificationCategory
  confidence_score: number
  total_pathogenic_score: number
  total_benign_score: number
  pathogenic_criteria: CriterionResult[]
  benign_criteria: CriterionResult[]
  evidence_chain: EvidenceChainItem[]
  warnings: string[]
  metadata?: Record<string, unknown>
}

export interface EvidenceChainItem {
  criterion: string
  description: string
  score: number
  confidence: number
  sources: string[]
}

export interface VCFFile {
  id: string
  file_name: string
  file_path: string
  upload_date: string
  patient_id: string
  variant_count?: number
  status?: 'pending' | 'processing' | 'completed' | 'error'
}

export interface Patient {
  id: string
  name: string
  age?: number
  sex?: 'M' | 'F' | 'Other'
  ethnicity?: string
  diagnosis_description?: string
  medical_history?: string
}

export interface ClinicalReport {
  id: string
  patient_id: string
  report_date: string
  report_content: string
  report_version?: string
  is_final: boolean
  clinician_id?: string
  review_date?: string
}

export interface ResearchReport {
  id: string
  patient_id: string
  report_date: string
  hypotheses: string
  uncertainty_metrics?: Record<string, number>
  evidence_gaps?: string
  priority_score?: number
  is_reviewed: boolean
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: string
  references?: {
    type: 'variant' | 'report' | 'evidence'
    id: string
    label: string
  }[]
}

export interface AnalysisSession {
  id: string
  patient_id: string
  vcf_file_id: string
  status: 'pending' | 'processing' | 'completed' | 'error'
  created_at: string
  updated_at?: string
  variants?: Variant[]
  classifications?: ACMGClassification[]
}

export interface FilterOptions {
  gene?: string
  chromosome?: string
  classification?: ClassificationCategory
  variant_type?: VariantType
  af_min?: number
  af_max?: number
  consequence?: string
}

export interface PaginationParams {
  page: number
  page_size: number
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface ConfigSchemaField {
  type: 'string' | 'integer' | 'float' | 'select' | 'textarea'
  label: string
  description?: string
  placeholder?: string
  required?: boolean
  default?: string | number
  min?: number
  max?: number
  step?: number
  rows?: number
  options?: Array<{ value: string; label: string }>
  group?: string
  group_label?: string
}

export interface Skill {
  name: string
  description: string
  skill_type: string
  icon: string
  input_schema: Record<string, string>
  config_schema: Record<string, ConfigSchemaField>
  is_enabled: boolean
  config: Record<string, string | number | boolean>
}
