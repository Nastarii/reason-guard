import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  Box,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  CircularProgress,
  Alert,
  Card,
  CardContent,
  Stepper,
  Step,
  StepLabel,
  StepContent,
} from '@mui/material'
import {
  Visibility,
  VerifiedUser,
  Psychology,
} from '@mui/icons-material'
import { getReasoningTraces, getReasoningTrace } from '../services/api'

interface ReasoningStep {
  id: string
  step_number: number
  step_type: string
  content: string
  confidence: number | null
}

interface ReasoningTrace {
  id: string
  original_prompt: string
  enhanced_prompt: string
  raw_response: string
  parsed_reasoning: any
  model_provider: string
  model_name: string
  integrity_hash: string
  created_at: string
  steps: ReasoningStep[]
}

const stepTypeColors: Record<string, 'primary' | 'secondary' | 'success'> = {
  premise: 'primary',
  inference: 'secondary',
  conclusion: 'success',
}

export default function ReasoningTraces() {
  const [page, setPage] = useState(0)
  const [rowsPerPage, setRowsPerPage] = useState(10)
  const [selectedTrace, setSelectedTrace] = useState<ReasoningTrace | null>(null)
  const [detailsOpen, setDetailsOpen] = useState(false)

  const { data: traces, isLoading, error } = useQuery({
    queryKey: ['reasoningTraces'],
    queryFn: () => getReasoningTraces(100).then((res) => res.data),
  })

  const { data: traceDetails, isLoading: detailsLoading } = useQuery({
    queryKey: ['reasoningTrace', selectedTrace?.id],
    queryFn: () => getReasoningTrace(selectedTrace!.id).then((res) => res.data),
    enabled: !!selectedTrace?.id && detailsOpen,
  })

  const handleViewDetails = (trace: ReasoningTrace) => {
    setSelectedTrace(trace)
    setDetailsOpen(true)
  }

  const handleCloseDetails = () => {
    setDetailsOpen(false)
    setSelectedTrace(null)
  }

  if (isLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
        <CircularProgress />
      </Box>
    )
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        Erro ao carregar rastreamentos de raciocínio.
      </Alert>
    )
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
        <Psychology color="primary" sx={{ fontSize: 32 }} />
        <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
          Rastreamento de Raciocínio (CoT)
        </Typography>
      </Box>

      <Paper>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Prompt</TableCell>
                <TableCell>Modelo</TableCell>
                <TableCell>Passos</TableCell>
                <TableCell>Data</TableCell>
                <TableCell align="center">Ações</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {traces
                ?.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                .map((trace: ReasoningTrace) => (
                  <TableRow key={trace.id} hover>
                    <TableCell>
                      {trace.original_prompt.length > 100
                        ? trace.original_prompt.substring(0, 100) + '...'
                        : trace.original_prompt}
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={`${trace.model_provider}/${trace.model_name}`}
                        size="small"
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={trace.steps?.length || 0}
                        color="primary"
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      {new Date(trace.created_at).toLocaleString('pt-BR')}
                    </TableCell>
                    <TableCell align="center">
                      <IconButton
                        color="primary"
                        onClick={() => handleViewDetails(trace)}
                      >
                        <Visibility />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              {(!traces || traces.length === 0) && (
                <TableRow>
                  <TableCell colSpan={5} align="center">
                    Nenhum rastreamento encontrado
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
        <TablePagination
          component="div"
          count={traces?.length || 0}
          page={page}
          onPageChange={(_, newPage) => setPage(newPage)}
          rowsPerPage={rowsPerPage}
          onRowsPerPageChange={(e) => {
            setRowsPerPage(parseInt(e.target.value, 10))
            setPage(0)
          }}
          labelRowsPerPage="Linhas por página"
          labelDisplayedRows={({ from, to, count }) => `${from}-${to} de ${count}`}
        />
      </Paper>

      {/* Details Dialog */}
      <Dialog
        open={detailsOpen}
        onClose={handleCloseDetails}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Psychology />
            Detalhes do Rastreamento
          </Box>
        </DialogTitle>
        <DialogContent dividers>
          {detailsLoading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
              <CircularProgress />
            </Box>
          ) : traceDetails ? (
            <Box>
              <Card variant="outlined" sx={{ mb: 3 }}>
                <CardContent>
                  <Typography variant="subtitle2" color="text.secondary">
                    Prompt Original
                  </Typography>
                  <Typography>{traceDetails.original_prompt}</Typography>
                </CardContent>
              </Card>

              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <VerifiedUser color="success" />
                <Typography variant="body2">
                  Hash de Integridade: {traceDetails.integrity_hash.substring(0, 20)}...
                </Typography>
              </Box>

              <Typography variant="h6" gutterBottom>
                Passos de Raciocínio
              </Typography>

              <Stepper orientation="vertical">
                {traceDetails.steps?.map((step: ReasoningStep) => (
                  <Step key={step.id} active>
                    <StepLabel
                      StepIconComponent={() => (
                        <Chip
                          label={step.step_type}
                          color={stepTypeColors[step.step_type] || 'default'}
                          size="small"
                        />
                      )}
                    >
                      Passo {step.step_number}
                      {step.confidence !== null && (
                        <Chip
                          label={`${(step.confidence * 100).toFixed(0)}% confiança`}
                          size="small"
                          sx={{ ml: 1 }}
                        />
                      )}
                    </StepLabel>
                    <StepContent>
                      <Typography>{step.content}</Typography>
                    </StepContent>
                  </Step>
                ))}
              </Stepper>

              {traceDetails.parsed_reasoning?.answer && (
                <Card variant="outlined" sx={{ mt: 3, backgroundColor: 'success.light' }}>
                  <CardContent>
                    <Typography variant="subtitle2" color="success.dark">
                      Resposta Final
                    </Typography>
                    <Typography>{traceDetails.parsed_reasoning.answer}</Typography>
                  </CardContent>
                </Card>
              )}
            </Box>
          ) : (
            <Typography>Erro ao carregar detalhes</Typography>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDetails}>Fechar</Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}
