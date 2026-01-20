import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import {
  Box,
  Paper,
  TextField,
  Button,
  Typography,
  FormControlLabel,
  Checkbox,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Card,
  CardContent,
  Divider,
  CircularProgress,
  Alert,
  Chip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Slider,
} from '@mui/material'
import {
  Send,
  ExpandMore,
  Psychology,
  AccountTree,
  Hub,
  CheckCircle,
} from '@mui/icons-material'
import { sendChat } from '../services/api'

interface ChatResponse {
  response: string
  reasoning_trace_id?: string
  path_analysis_id?: string
  logic_graph_id?: string
  consistency_check_id?: string
  metadata: Record<string, any>
}

export default function Chat() {
  const [prompt, setPrompt] = useState('')
  const [provider, setProvider] = useState('openai')
  const [enableCot, setEnableCot] = useState(true)
  const [enableTot, setEnableTot] = useState(false)
  const [enableGot, setEnableGot] = useState(false)
  const [enableConsistency, setEnableConsistency] = useState(false)
  const [consistencyRuns, setConsistencyRuns] = useState(3)
  const [temperature, setTemperature] = useState(0.7)
  const [response, setResponse] = useState<ChatResponse | null>(null)

  const mutation = useMutation({
    mutationFn: (data: any) => sendChat(data).then((res) => res.data),
    onSuccess: (data) => {
      setResponse(data)
    },
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!prompt.trim()) return

    mutation.mutate({
      prompt,
      model_provider: provider,
      enable_cot: enableCot,
      enable_tot: enableTot,
      enable_got: enableGot,
      enable_consistency: enableConsistency,
      consistency_runs: consistencyRuns,
      temperature,
    })
  }

  return (
    <Box>
      <Typography variant="h5" gutterBottom sx={{ fontWeight: 'bold', mb: 3 }}>
        Chat com IA Auditável
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Configurações
            </Typography>

            <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Provedor</InputLabel>
              <Select
                value={provider}
                label="Provedor"
                onChange={(e) => setProvider(e.target.value)}
              >
                <MenuItem value="openai">OpenAI</MenuItem>
              </Select>
            </FormControl>

            <Typography gutterBottom>Temperatura: {temperature}</Typography>
            <Slider
              value={temperature}
              onChange={(_, value) => setTemperature(value as number)}
              min={0}
              max={2}
              step={0.1}
              sx={{ mb: 2 }}
            />

            <Divider sx={{ my: 2 }} />

            <Typography variant="subtitle2" gutterBottom>
              Módulos de Análise
            </Typography>

            <FormControlLabel
              control={
                <Checkbox
                  checked={enableCot}
                  onChange={(e) => setEnableCot(e.target.checked)}
                />
              }
              label={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Psychology fontSize="small" />
                  <span>Chain of Thought (CoT)</span>
                </Box>
              }
            />

            <FormControlLabel
              control={
                <Checkbox
                  checked={enableTot}
                  onChange={(e) => setEnableTot(e.target.checked)}
                />
              }
              label={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <AccountTree fontSize="small" />
                  <span>Tree of Thought (ToT)</span>
                </Box>
              }
            />

            <FormControlLabel
              control={
                <Checkbox
                  checked={enableGot}
                  onChange={(e) => setEnableGot(e.target.checked)}
                  disabled={!enableCot}
                />
              }
              label={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Hub fontSize="small" />
                  <span>Graph of Thought (GoT)</span>
                </Box>
              }
            />

            <FormControlLabel
              control={
                <Checkbox
                  checked={enableConsistency}
                  onChange={(e) => setEnableConsistency(e.target.checked)}
                />
              }
              label={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <CheckCircle fontSize="small" />
                  <span>Verificação de Consistência</span>
                </Box>
              }
            />

            {enableConsistency && (
              <Box sx={{ mt: 1, ml: 3 }}>
                <Typography variant="caption">
                  Número de execuções: {consistencyRuns}
                </Typography>
                <Slider
                  value={consistencyRuns}
                  onChange={(_, value) => setConsistencyRuns(value as number)}
                  min={2}
                  max={10}
                  step={1}
                  marks
                  size="small"
                />
              </Box>
            )}
          </Paper>
        </Grid>

        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3, mb: 3 }}>
            <form onSubmit={handleSubmit}>
              <TextField
                fullWidth
                multiline
                rows={4}
                label="Sua pergunta ou problema"
                placeholder="Digite sua pergunta para a IA..."
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                sx={{ mb: 2 }}
              />
              <Button
                type="submit"
                variant="contained"
                size="large"
                endIcon={mutation.isPending ? <CircularProgress size={20} color="inherit" /> : <Send />}
                disabled={mutation.isPending || !prompt.trim()}
              >
                {mutation.isPending ? 'Processando...' : 'Enviar'}
              </Button>
            </form>
          </Paper>

          {mutation.isError && (
            <Alert severity="error" sx={{ mb: 3 }}>
              Erro ao processar a requisição. Verifique as configurações e tente novamente.
            </Alert>
          )}

          {response && (
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Resposta
              </Typography>

              <Box sx={{ display: 'flex', gap: 1, mb: 2, flexWrap: 'wrap' }}>
                {response.reasoning_trace_id && (
                  <Chip icon={<Psychology />} label="CoT" color="primary" size="small" />
                )}
                {response.path_analysis_id && (
                  <Chip icon={<AccountTree />} label="ToT" color="secondary" size="small" />
                )}
                {response.logic_graph_id && (
                  <Chip icon={<Hub />} label="GoT" color="info" size="small" />
                )}
                {response.consistency_check_id && (
                  <Chip icon={<CheckCircle />} label="Consistência" color="success" size="small" />
                )}
              </Box>

              <Card variant="outlined" sx={{ mb: 2 }}>
                <CardContent>
                  <Typography sx={{ whiteSpace: 'pre-wrap' }}>
                    {response.response}
                  </Typography>
                </CardContent>
              </Card>

              {Object.keys(response.metadata).length > 0 && (
                <Accordion>
                  <AccordionSummary expandIcon={<ExpandMore />}>
                    <Typography>Metadados da Análise</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    {response.metadata.cot && (
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="subtitle2" color="primary">
                          Chain of Thought
                        </Typography>
                        <Typography variant="body2">
                          Passos de raciocínio: {response.metadata.cot.steps_count}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Hash de integridade: {response.metadata.cot.integrity_hash}
                        </Typography>
                      </Box>
                    )}

                    {response.metadata.tot && (
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="subtitle2" color="secondary">
                          Tree of Thought
                        </Typography>
                        <Typography variant="body2">
                          Nós explorados: {response.metadata.tot.nodes_explored}
                        </Typography>
                        <Typography variant="body2">
                          Caminhos podados: {response.metadata.tot.paths_pruned}
                        </Typography>
                      </Box>
                    )}

                    {response.metadata.got && (
                      <Box sx={{ mb: 2 }}>
                        <Typography variant="subtitle2" color="info.main">
                          Graph of Thought
                        </Typography>
                        <Typography variant="body2">
                          Score de validade: {((response.metadata.got.validity_score || 0) * 100).toFixed(1)}%
                        </Typography>
                        {response.metadata.got.has_contradictions && (
                          <Chip label="Contradições detectadas" color="error" size="small" sx={{ mt: 1 }} />
                        )}
                        {response.metadata.got.has_logic_gaps && (
                          <Chip label="Lacunas lógicas" color="warning" size="small" sx={{ mt: 1, ml: 1 }} />
                        )}
                      </Box>
                    )}

                    {response.metadata.consistency && (
                      <Box>
                        <Typography variant="subtitle2" color="success.main">
                          Verificação de Consistência
                        </Typography>
                        <Typography variant="body2">
                          Taxa de convergência: {(response.metadata.consistency.convergence_rate * 100).toFixed(1)}%
                        </Typography>
                        <Typography variant="body2">
                          Score de confiança: {(response.metadata.consistency.confidence_score * 100).toFixed(1)}%
                        </Typography>
                        <Typography variant="body2">
                          Execuções: {response.metadata.consistency.total_runs}
                        </Typography>
                      </Box>
                    )}
                  </AccordionDetails>
                </Accordion>
              )}
            </Paper>
          )}
        </Grid>
      </Grid>
    </Box>
  )
}
