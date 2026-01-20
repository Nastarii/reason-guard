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
  Grid,
  Card,
  CardContent,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
} from '@mui/material'
import {
  Visibility,
  CheckCircle,
  ExpandMore,
  TrendingUp,
  Warning,
} from '@mui/icons-material'
import { getConsistencyChecks, getConsistencyCheck, getConsistencyCheckSummary } from '../services/api'

interface ConsistencyCheckData {
  id: string
  original_query: string
  query_variations: string[]
  responses: Array<{
    run: number
    query: string
    response: string
    model: string
  }>
  convergence_rate: number
  confidence_score: number
  divergent_points: Array<{
    between_runs: number[]
    point: string
  }> | null
  total_runs: number
  model_provider: string
  model_name: string
  created_at: string
}

export default function ConsistencyChecks() {
  const [page, setPage] = useState(0)
  const [rowsPerPage, setRowsPerPage] = useState(10)
  const [selectedCheck, setSelectedCheck] = useState<ConsistencyCheckData | null>(null)
  const [detailsOpen, setDetailsOpen] = useState(false)

  const { data: checks, isLoading, error } = useQuery({
    queryKey: ['consistencyChecks'],
    queryFn: () => getConsistencyChecks(100).then((res) => res.data),
  })

  const { data: checkDetails, isLoading: detailsLoading } = useQuery({
    queryKey: ['consistencyCheck', selectedCheck?.id],
    queryFn: () => getConsistencyCheck(selectedCheck!.id).then((res) => res.data),
    enabled: !!selectedCheck?.id && detailsOpen,
  })

  const { data: summary } = useQuery({
    queryKey: ['consistencyCheckSummary', selectedCheck?.id],
    queryFn: () => getConsistencyCheckSummary(selectedCheck!.id).then((res) => res.data),
    enabled: !!selectedCheck?.id && detailsOpen,
  })

  const handleViewDetails = (check: ConsistencyCheckData) => {
    setSelectedCheck(check)
    setDetailsOpen(true)
  }

  const handleCloseDetails = () => {
    setDetailsOpen(false)
    setSelectedCheck(null)
  }

  const getStatusColor = (score: number) => {
    if (score >= 0.8) return 'success'
    if (score >= 0.5) return 'warning'
    return 'error'
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
        Erro ao carregar verificações de consistência.
      </Alert>
    )
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
        <CheckCircle color="success" sx={{ fontSize: 32 }} />
        <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
          Verificação de Consistência
        </Typography>
      </Box>

      <Paper>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Consulta</TableCell>
                <TableCell>Execuções</TableCell>
                <TableCell>Taxa de Convergência</TableCell>
                <TableCell>Score de Confiança</TableCell>
                <TableCell>Data</TableCell>
                <TableCell align="center">Ações</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {checks
                ?.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                .map((check: ConsistencyCheckData) => (
                  <TableRow key={check.id} hover>
                    <TableCell>
                      {check.original_query.length > 60
                        ? check.original_query.substring(0, 60) + '...'
                        : check.original_query}
                    </TableCell>
                    <TableCell>
                      <Chip label={check.total_runs} size="small" />
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <LinearProgress
                          variant="determinate"
                          value={check.convergence_rate * 100}
                          sx={{ width: 80, height: 8, borderRadius: 4 }}
                          color={getStatusColor(check.convergence_rate)}
                        />
                        <Typography variant="body2">
                          {(check.convergence_rate * 100).toFixed(0)}%
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={`${(check.confidence_score * 100).toFixed(0)}%`}
                        color={getStatusColor(check.confidence_score)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      {new Date(check.created_at).toLocaleString('pt-BR')}
                    </TableCell>
                    <TableCell align="center">
                      <IconButton
                        color="primary"
                        onClick={() => handleViewDetails(check)}
                      >
                        <Visibility />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              {(!checks || checks.length === 0) && (
                <TableRow>
                  <TableCell colSpan={6} align="center">
                    Nenhuma verificação encontrada
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
        <TablePagination
          component="div"
          count={checks?.length || 0}
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
        maxWidth="lg"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <CheckCircle />
            Detalhes da Verificação de Consistência
          </Box>
        </DialogTitle>
        <DialogContent dividers>
          {detailsLoading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
              <CircularProgress />
            </Box>
          ) : checkDetails ? (
            <Box>
              <Card variant="outlined" sx={{ mb: 3 }}>
                <CardContent>
                  <Typography variant="subtitle2" color="text.secondary">
                    Consulta Original
                  </Typography>
                  <Typography>{checkDetails.original_query}</Typography>
                </CardContent>
              </Card>

              <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid item xs={12} md={3}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="subtitle2" color="text.secondary">
                        Execuções
                      </Typography>
                      <Typography variant="h4">{checkDetails.total_runs}</Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12} md={3}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="subtitle2" color="text.secondary">
                        Taxa de Convergência
                      </Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography variant="h4" color={getStatusColor(checkDetails.convergence_rate) + '.main'}>
                          {(checkDetails.convergence_rate * 100).toFixed(0)}%
                        </Typography>
                        <TrendingUp color={getStatusColor(checkDetails.convergence_rate)} />
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12} md={3}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="subtitle2" color="text.secondary">
                        Score de Confiança
                      </Typography>
                      <Typography variant="h4" color={getStatusColor(checkDetails.confidence_score) + '.main'}>
                        {(checkDetails.confidence_score * 100).toFixed(0)}%
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12} md={3}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="subtitle2" color="text.secondary">
                        Pontos Divergentes
                      </Typography>
                      <Typography variant="h4">
                        {checkDetails.divergent_points?.length || 0}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>

              {summary && (
                <Alert
                  severity={checkDetails.confidence_score >= 0.8 ? 'success' : checkDetails.confidence_score >= 0.5 ? 'warning' : 'error'}
                  sx={{ mb: 3 }}
                >
                  <Typography variant="subtitle2">{summary.status}</Typography>
                  <Typography variant="body2">{summary.recommendation}</Typography>
                </Alert>
              )}

              <Typography variant="h6" gutterBottom>
                Respostas por Execução
              </Typography>

              {checkDetails.responses?.map((response: any, index: number) => (
                <Accordion key={index}>
                  <AccordionSummary expandIcon={<ExpandMore />}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, width: '100%' }}>
                      <Chip label={`Execução ${response.run}`} size="small" />
                      <Typography variant="body2" color="text.secondary" sx={{ flexGrow: 1 }}>
                        {response.query.length > 80
                          ? response.query.substring(0, 80) + '...'
                          : response.query}
                      </Typography>
                    </Box>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Card variant="outlined">
                      <CardContent>
                        <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                          Variação da Consulta
                        </Typography>
                        <Typography variant="body2" sx={{ mb: 2 }}>
                          {response.query}
                        </Typography>
                        <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                          Resposta
                        </Typography>
                        <Typography sx={{ whiteSpace: 'pre-wrap' }}>
                          {response.response}
                        </Typography>
                      </CardContent>
                    </Card>
                  </AccordionDetails>
                </Accordion>
              ))}

              {checkDetails.divergent_points && checkDetails.divergent_points.length > 0 && (
                <Box sx={{ mt: 3 }}>
                  <Typography variant="h6" gutterBottom>
                    Pontos Divergentes
                  </Typography>
                  <Card variant="outlined" sx={{ borderColor: 'warning.main' }}>
                    <CardContent>
                      <List dense>
                        {checkDetails.divergent_points.map((point: any, index: number) => (
                          <ListItem key={index}>
                            <ListItemText
                              primary={point.point}
                              secondary={`Entre execuções: ${point.between_runs.join(' e ')}`}
                            />
                            <Warning color="warning" />
                          </ListItem>
                        ))}
                      </List>
                    </CardContent>
                  </Card>
                </Box>
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
