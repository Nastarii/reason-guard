import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add auth token interceptor
api.interceptors.request.use(async (config) => {
  // Get token from Clerk
  const token = await window.Clerk?.session?.getToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Dashboard
export const getDashboardStats = () => api.get('/dashboard/stats')
export const getRecentActivity = (limit = 10) => api.get(`/dashboard/recent-activity?limit=${limit}`)
export const getDashboardSummary = (days = 7) => api.get(`/dashboard/summary?days=${days}`)

// Proxy
export const sendChat = (data: {
  prompt: string
  model_provider?: string
  model_name?: string
  enable_cot?: boolean
  enable_tot?: boolean
  enable_got?: boolean
  enable_consistency?: boolean
  consistency_runs?: number
  temperature?: number
}) => api.post('/proxy/chat', data)

// Reasoning Traces
export const getReasoningTraces = (limit = 50) => api.get(`/reasoning/traces?limit=${limit}`)
export const getReasoningTrace = (id: string) => api.get(`/reasoning/traces/${id}`)
export const createReasoningTrace = (data: { original_prompt: string; model_provider: string }) =>
  api.post('/reasoning/trace', data)

// Path Analysis
export const getPathAnalyses = (limit = 50) => api.get(`/path-analysis/analyses?limit=${limit}`)
export const getPathAnalysis = (id: string) => api.get(`/path-analysis/analyses/${id}`)
export const getPathAnalysisTree = (id: string) => api.get(`/path-analysis/analyses/${id}/tree`)
export const createPathAnalysis = (data: { problem: string; model_provider: string; max_depth?: number; breadth?: number }) =>
  api.post('/path-analysis/analyze', data)

// Logic Validation
export const getLogicGraphs = (limit = 50) => api.get(`/logic/graphs?limit=${limit}`)
export const getLogicGraph = (id: string) => api.get(`/logic/graphs/${id}`)
export const getLogicGraphVisualization = (id: string) => api.get(`/logic/graphs/${id}/visualization`)
export const getLogicGraphIssues = (id: string) => api.get(`/logic/graphs/${id}/issues`)
export const createLogicValidation = (data: { reasoning_trace_id?: string; raw_text?: string }) =>
  api.post('/logic/validate', data)

// Consistency Checks
export const getConsistencyChecks = (limit = 50) => api.get(`/consistency/checks?limit=${limit}`)
export const getConsistencyCheck = (id: string) => api.get(`/consistency/checks/${id}`)
export const getConsistencyCheckSummary = (id: string) => api.get(`/consistency/checks/${id}/summary`)
export const createConsistencyCheck = (data: { query: string; model_provider: string; num_runs?: number }) =>
  api.post('/consistency/check', data)

// Audit Reports
export const getAuditReports = (limit = 50) => api.get(`/audit/reports?limit=${limit}`)
export const getAuditReport = (id: string) => api.get(`/audit/reports/${id}`)
export const downloadAuditReport = (id: string) => api.get(`/audit/reports/${id}/download`, { responseType: 'blob' })
export const createAuditReport = (data: {
  report_type: string
  format: string
  reasoning_trace_ids?: string[]
  path_analysis_ids?: string[]
  logic_graph_ids?: string[]
  consistency_check_ids?: string[]
}) => api.post('/audit/reports', data)

// API Tokens
export const getApiTokens = () => api.get('/api-tokens')
export const createApiToken = (data: { name: string; description?: string; expires_at?: string }) =>
  api.post('/api-tokens', data)
export const deleteApiToken = (id: string) => api.delete(`/api-tokens/${id}`)
export const revokeApiToken = (id: string) => api.post(`/api-tokens/${id}/revoke`)

export default api

// Extend window for Clerk
declare global {
  interface Window {
    Clerk?: {
      session?: {
        getToken: () => Promise<string | null>
      }
    }
  }
}
