export interface Patient {
  id: string
  name?: string
  age?: number
  sex?: 'M' | 'F' | 'Other'
  ethnicity?: string
  diagnosis_description?: string
  medical_history?: string
}

export interface VCFFileSummary {
  id: number
  file_name: string
  upload_date: string
  variant_count: number
  classified_count: number
}

export interface CaseSummary {
  patient_id: number
  patient_name?: string
  age?: number
  sex?: string
  ethnicity?: string
  diagnosis_description?: string
  medical_history?: string
  hpo_terms?: Array<{ phrase: string; hpo_id: string; category?: string; display_category?: string }>
  vcf_files: VCFFileSummary[]
  total_variants: number
  total_classified: number
}

export interface VCFFile {
  id: string
  file_name: string
  file_path: string
  upload_date: string
  patient_id: string
}

export interface DynamicVariantListResponse {
  columns: string[]
  items: Record<string, string>[]
  total: number
  page: number
  page_size: number
  total_pages: number
  vep_job_id?: string
  message: string
}

export interface DynamicVariantDetailResponse {
  row_index: number
  columns: string[]
  row: Record<string, string>
}

export interface VEPJobStatus {
  job_id: string
  status: string
  input_filename?: string
  input_bytes?: number
  options?: Record<string, unknown>
  status_url?: string
  result_url?: string
  log_url?: string
  rows?: number
  vep_annotated_count?: number | null
  error?: string
  created_at?: string
  updated_at?: string
  csv_path?: string
  parquet_path?: string
  parquet_available: boolean
}

export type VariantType = 'SNV' | 'INDEL' | 'STR' | 'CNV'

export type ClassificationCategory = 'Pathogenic' | 'Likely Pathogenic' | 'VUS' | 'Likely Benign' | 'Benign'

export type EvidenceStrength = 'pathogenic_very_strong' | 'pathogenic_strong' | 'pathogenic_moderate' | 'pathogenic_supporting' | 'benign_standalone' | 'benign_strong' | 'benign_supporting'

export interface CriterionResult {
  criterion_code: string
  criterion_name: string
  is_met: boolean
  evidence_strength: EvidenceStrength
  direction: 'pathogenic' | 'benign'
  score: number
  description: string
  evidence_sources: string[]
  confidence: number
}

export interface Variant {
  id: string
  chromosome: string
  position: number
  ref: string
  alt: string
  variant_type: VariantType
  quality?: number
  filter_status?: string
  info_field?: Record<string, unknown>
  vcf_file_id: string
  gnomad_af?: number | null
  gene?: string
  hgvs_p?: string
  consequence?: string
  all_genes?: string
  transcript?: string
  impact?: string
  hgvs_c?: string
  cdna_position?: string
  cds_position?: string
  protein_position?: string
  amino_acids?: string
  codons?: string
  exon?: string
  intron?: string
  strand?: string
  protein_domains?: string
  revel_score?: number | null
  cadd?: number | null
  gnomad_popmax_af?: number | null
  gnomad_eas_af?: number | null
  gnomad_nhomalt?: number | null
  spliceai_ds_max?: number | null
  spliceai_type?: string
  loftee_lof_flag?: string
  loftee_lof_filter?: string
  clinvar_significance?: string
  clinvar_review_status?: string
  clinvar_star_rating?: number | null
  pathogenic_rank?: number | null
  evidence_summary?: string
  sift?: string
  polyphen?: string
  vep_annotated?: boolean
  acmg_classification?: string
}

export interface ACMGEvidence {
  id: string
  variant_id: string
  criterion: string
  criterion_code?: string
  evidence_level: string
  description: string
  evidence_source?: string
  is_applied: boolean
  is_met?: boolean
  score?: number
}

export interface ACMGClassification {
  id: string
  variant_id: string
  classification: ClassificationCategory
  confidence_score?: number
  classification_date: string
  classifier_version?: string
  notes?: string
  evidence_chain?: ACMGEvidence[]
  pathogenic_criteria?: CriterionResult[]
  benign_criteria?: CriterionResult[]
  total_pathogenic_score?: number
  total_benign_score?: number
  warnings?: string[]
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
  uncertainty_metrics?: Record<string, unknown>
  evidence_gaps?: string
  priority_score?: number
  is_reviewed: boolean
}

export interface AnalysisSession {
  id: string
  patient_id: string
  vcf_file_id: string
  created_at: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
}

export interface FilterOptions {
  chromosome?: string
  position_start?: number
  position_end?: number
  variant_type?: string
  min_quality?: number
  max_quality?: number
  acmg_classification?: string
  classification?: string
  gene?: string
}

export interface PaginationParams {
  page?: number
  page_size?: number
  sort_by?: string
  sort_desc?: boolean
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface ChatReference {
  id: string
  type: 'variant' | 'report' | 'evidence'
  label: string
  url?: string
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: string
  references?: ChatReference[]
  confidence?: number
}

export interface CaseDocument {
  id: string
  patient_id: string
  title: string
  content: string
  document_type: 'patient_summary' | 'variant_report' | 'clinical_notes'
  metadata?: Record<string, unknown>
  created_at: string
}

export interface QAResponse {
  answer: string
  sources: ChatReference[]
  confidence: number
  reasoning?: string
}

export interface SearchResult {
  id: string
  content: string
  score: number
  metadata?: Record<string, unknown>
}

export type SkillType = 'prompt_injection' | 'tool_call'

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
  skill_type: SkillType
  icon: string
  input_schema: Record<string, unknown>
  config_schema: Record<string, ConfigSchemaField>
  is_enabled: boolean
  config: Record<string, string | number | boolean>
}

export interface SkillConfig {
  id: number
  skill_name: string
  is_enabled: boolean
  config: Record<string, unknown>
  created_at: string
  updated_at: string
}

export interface StreamingChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: string
  references?: ChatReference[]
  confidence?: number
  skill_name?: string
  skill_type?: SkillType
  is_streaming?: boolean
}

export interface WSMessage {
  type: 'chat' | 'skill' | 'cancel'
  content: string
  skill_name?: string
  session_token?: string
}

export interface WSResponse {
  type: 'chunk' | 'skill_result' | 'done' | 'error' | 'session_info'
  content?: string
  message_id?: string
  references?: ChatReference[]
  confidence?: number
  skill_name?: string
  skill_type?: SkillType
  session_token?: string
}

export interface GeneSummary {
  gene: string
  variant_count: number
  variant_types: Record<string, number>
  classifications: Record<string, number>
  max_gnomad_af: number | null
  chromosomes: string[]
}

export interface GeneListResponse {
  genes: GeneSummary[]
  total: number
}

export interface GeneVariant {
  id: string
  chromosome: string
  position: number
  ref: string
  alt: string
  variant_type: string
  quality: number | null
  gnomad_af: number | null
  clinvar_significance: string | null
  acmg_classification: string | null
}

export interface GeneVariantsResponse {
  gene: string
  variants: GeneVariant[]
  total: number
}

export interface GeneInfo {
  symbol: string
  name: string
  description: string
  chromosome: string
  location: string
  omim_id: string | null
  hgnc_id: string | null
  ensembl_id: string | null
  diseases: string[]
  inheritance: string[]
  aliases: string[]
}

export interface PathwayResult {
  st_id: string
  name: string
  p_value: number
  fdr: number
  entities_count: number
  entities_found: number
  entities_ratio: number
  species: string
  mapped_genes: string[]
  pathway_type?: string
  compartments?: string[]
}

export interface PathwayAnalysisResponse {
  token: string
  pathways: PathwayResult[]
  genes_analyzed: number
  genes_not_found: number
}

export interface GOBiologicalProcess {
  db_id: number
  display_name: string
  accession: string
  database_name: string
  definition?: string
  name: string
  url: string
  schema_class: string
}

export interface LiteratureReference {
  db_id: number
  display_name: string
  title?: string
  journal?: string
  pages?: string
  pub_med_identifier?: number
  volume?: number
  year?: number
  url?: string
}

export interface Summation {
  db_id: number
  display_name: string
  text?: string
}

export interface OrthologousEvent {
  db_id: number
  display_name: string
  st_id: string
  st_id_version: string
  species_name: string
  schema_class: string
  is_in_disease: boolean
  is_inferred: boolean
  max_depth: number
  release_date?: string
  has_diagram: boolean
  has_ehld: boolean
}

export interface HasEvent {
  db_id: number
  display_name: string
  st_id: string
  st_id_version: string
  name: string[]
  schema_class: string
  is_in_disease: boolean
  is_inferred: boolean
  max_depth: number
  release_date?: string
  species_name?: string
  category?: string
  has_diagram: boolean
  has_ehld: boolean
}

export interface Compartment {
  db_id: number
  display_name: string
  name: string
  schema_class: string
  accession?: string
}

export interface Species {
  db_id: number
  display_name: string
  name: string[]
  tax_id?: string
  abbreviation?: string
  schema_class: string
}

export interface ReviewStatus {
  db_id: number
  display_name: string
  definition?: string
  name: string[]
  schema_class: string
}

export interface PathwayDetailResponse {
  db_id: number
  st_id: string
  st_id_version: string
  display_name: string
  name: string[]
  schema_class: string
  class_name?: string
  
  species_name: string
  species?: Species
  
  is_in_disease: boolean
  is_inferred: boolean
  has_diagram: boolean
  has_ehld: boolean
  
  release_date?: string
  release_status?: string
  last_updated_date?: string
  review_status?: ReviewStatus
  previous_review_status?: ReviewStatus
  
  max_depth: number
  
  go_biological_process?: GOBiologicalProcess
  summation: Summation[]
  literature_reference: LiteratureReference[]
  compartment: Compartment[]
  has_event: HasEvent[]
  orthologous_event: OrthologousEvent[]
  
  url: string
}

export interface GenePhenotypeScore {
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
}

export interface GenePhenotypeScoresResponse {
  scores: GenePhenotypeScore[]
  total: number
}

export interface PhenotypeHpoJobStatus {
  uid: string
  status: string
  phase: string
  message: string
}

export interface PpiGeneScore {
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
}

export interface PpiGeneScoresResponse {
  scores: PpiGeneScore[]
  total: number
}

export interface PpiJobStatus {
  job_id: string
  status: string
  message: string
}

export interface PpiGeneScore {
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
}

export interface PpiGeneScoresResponse {
  scores: PpiGeneScore[]
  total: number
}

export interface RankedGeneScore {
  gene: string
  combined_score: number
  rank: number
  gene_score: number
  ppi_final: number
  disease_score: number
  tissue_score: number
  topology_score: number
  conclusion_code: string
  best_disease_name: string
  best_disease_score: number
  in_network: boolean
  score_mode: string
  mapped_tissues: string
}

export interface RankedGeneScoresResponse {
  scores: RankedGeneScore[]
  total: number
}

export interface ReportMeta {
  run_id: string
  genes: string[]
  pheno_coverage: number
  ppi_coverage: number
}

export interface ReportMdChunk {
  type: 'md'
  slot?: string
  text: string
}

export interface ReportDone {
  type: 'done'
  pdf_url: string
  md_url?: string
}

export interface ReportError {
  type: 'error'
  message: string
}

export type ReportEvent = ReportMeta | ReportMdChunk | ReportDone | ReportError

export interface ReportRequest {
  vcf_file_id: number
  hpo_job_uid?: string
  ppi_job_id?: string
  hpo_terms?: string[]
  symptom_text?: string
  genes?: string[]
  top_n?: number
  k?: number
}

export interface ReportResult {
  run_id: string
  pdf_url: string
  markdown: string
  meta?: ReportMeta
}

export interface GeneAnalysisReport {
  id: string
  run_id: string
  pdf_url: string
  md_url?: string
  markdown: string
  meta?: ReportMeta
  created_at: string
  vcf_file_id: number
}
