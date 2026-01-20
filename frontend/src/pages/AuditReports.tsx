import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
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
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  CircularProgress,
  Alert,
  Grid,
  Card,
  CardContent,
} from '@mui/material'
import {
  Download,
  Add,
  Assessment,
  PictureAsPdf,
  TableChart,
  Code,
} from '@mui/icons-material'
import { getAuditReports, createAuditReport, downloadAuditReport } from '../services/api'

interface AuditReportData {
  id: string
  report_type: string
  format: string
  report_data: any
  file_path: string | null
  created_at: string
}

const reportTypeLabels: Record<string, string> = {
  compliance: 'Compliance',
  legal: 'Jurídico',
  technical: 'Técnico',
}

const formatIcons: Record<string, React.ReactNode> = {
  pdf: <PictureAsPdf />,
  excel: <TableChart />,
  json: <Code />,
}

export default function AuditReports() {
  const [page, setPage] = useState(0)
  const [rowsPerPage, setRowsPerPage] = useState(10)
  const [createDialogOpen, setCreateDialogOpen] = useState(false)
  const [reportType, setReportType] = useState('compliance')
  const [reportFormat, setReportFormat] = useState('pdf')
  const [downloading, setDownloading] = useState<string | null>(null)

  const queryClient = useQueryClient()

  const { data: reports, isLoading, error } = useQuery({
    queryKey: ['auditReports'],
    queryFn: () => getAuditReports(100).then((res) => res.data),
  })

  const createMutation = useMutation({
    mutationFn: (data: { report_type: string; format: string }) =>
      createAuditReport(data).then((res) => res.data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['auditReports'] })
      setCreateDialogOpen(false)
    },
  })

  const handleCreateReport = () => {
    createMutation.mutate({
      report_type: reportType,
      format: reportFormat,
    })
  }

  const handleDownload = async (report: AuditReportData) => {
    setDownloading(report.id)
    try {
      const response = await downloadAuditReport(report.id)
      const blob = new Blob([response.data])
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url

      const extension = report.format === 'excel' ? 'xlsx' : report.format
      a.download = `audit_report_${report.report_type}_${report.id.substring(0, 8)}.${extension}`

      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      window.URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Download failed:', error)
    } finally {
      setDownloading(null)
    }
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
        Erro ao carregar relatórios de auditoria.
      </Alert>
    )
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <Assessment color="primary" sx={{ fontSize: 32 }} />
          <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
            Relatórios de Auditoria
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={() => setCreateDialogOpen(true)}
        >
          Novo Relatório
        </Button>
      </Box>

      <Paper>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>ID</TableCell>
                <TableCell>Tipo</TableCell>
                <TableCell>Formato</TableCell>
                <TableCell>Decisões</TableCell>
                <TableCell>Score Médio de Validade</TableCell>
                <TableCell>Data</TableCell>
                <TableCell align="center">Ações</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {reports
                ?.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                .map((report: AuditReportData) => (
                  <TableRow key={report.id} hover>
                    <TableCell>
                      <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                        {report.id.substring(0, 8)}...
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={reportTypeLabels[report.report_type] || report.report_type}
                        color={
                          report.report_type === 'compliance' ? 'primary' :
                          report.report_type === 'legal' ? 'secondary' : 'default'
                        }
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        icon={formatIcons[report.format] as React.ReactElement}
                        label={report.format.toUpperCase()}
                        variant="outlined"
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      {report.report_data?.summary?.total_decisions || 0}
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={`${report.report_data?.summary?.average_validity_score || 0}%`}
                        color={
                          (report.report_data?.summary?.average_validity_score || 0) >= 70 ? 'success' :
                          (report.report_data?.summary?.average_validity_score || 0) >= 40 ? 'warning' : 'error'
                        }
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      {new Date(report.created_at).toLocaleString('pt-BR')}
                    </TableCell>
                    <TableCell align="center">
                      <IconButton
                        color="primary"
                        onClick={() => handleDownload(report)}
                        disabled={downloading === report.id}
                      >
                        {downloading === report.id ? (
                          <CircularProgress size={24} />
                        ) : (
                          <Download />
                        )}
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              {(!reports || reports.length === 0) && (
                <TableRow>
                  <TableCell colSpan={7} align="center">
                    Nenhum relatório encontrado
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
        <TablePagination
          component="div"
          count={reports?.length || 0}
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

      {/* Create Report Dialog */}
      <Dialog
        open={createDialogOpen}
        onClose={() => setCreateDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>Criar Novo Relatório de Auditoria</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Tipo de Relatório</InputLabel>
                <Select
                  value={reportType}
                  label="Tipo de Relatório"
                  onChange={(e) => setReportType(e.target.value)}
                >
                  <MenuItem value="compliance">Compliance</MenuItem>
                  <MenuItem value="legal">Jurídico</MenuItem>
                  <MenuItem value="technical">Técnico</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Formato</InputLabel>
                <Select
                  value={reportFormat}
                  label="Formato"
                  onChange={(e) => setReportFormat(e.target.value)}
                >
                  <MenuItem value="pdf">PDF</MenuItem>
                  <MenuItem value="excel">Excel</MenuItem>
                  <MenuItem value="json">JSON</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <Alert severity="info">
                O relatório será gerado com todos os dados disponíveis do seu histórico de análises.
              </Alert>
            </Grid>
          </Grid>

          <Box sx={{ mt: 3 }}>
            <Typography variant="subtitle2" gutterBottom>
              Descrição do Tipo de Relatório
            </Typography>
            <Card variant="outlined">
              <CardContent>
                {reportType === 'compliance' && (
                  <Typography variant="body2">
                    Relatório focado em conformidade e auditoria. Inclui resumo de decisões,
                    verificação de integridade, e métricas de consistência.
                  </Typography>
                )}
                {reportType === 'legal' && (
                  <Typography variant="body2">
                    Relatório focado em aspectos jurídicos. Inclui trilha de auditoria completa,
                    problemas identificados, e avaliação de confiabilidade.
                  </Typography>
                )}
                {reportType === 'technical' && (
                  <Typography variant="body2">
                    Relatório técnico detalhado. Inclui dados completos de rastreamento,
                    grafos lógicos, árvores de decisão, e métricas de análise.
                  </Typography>
                )}
              </CardContent>
            </Card>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>Cancelar</Button>
          <Button
            variant="contained"
            onClick={handleCreateReport}
            disabled={createMutation.isPending}
            startIcon={createMutation.isPending ? <CircularProgress size={20} /> : <Add />}
          >
            Criar Relatório
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}
