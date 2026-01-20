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
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Tooltip,
} from '@mui/material'
import {
  Visibility,
  Hub,
  Warning,
  Error as ErrorIcon,
  HelpOutline,
  Loop,
  CheckCircle,
} from '@mui/icons-material'
import ReactFlow, {
  Node,
  Edge,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  MarkerType,
} from 'reactflow'
import 'reactflow/dist/style.css'
import { getLogicGraphs, getLogicGraphVisualization, getLogicGraphIssues } from '../services/api'

interface LogicGraphData {
  id: string
  reasoning_trace_id: string | null
  has_contradictions: boolean
  has_logic_gaps: boolean
  has_hidden_premises: boolean
  has_circularity: boolean
  overall_validity_score: number | null
  created_at: string
}

interface GraphVisualization {
  nodes: Array<{
    id: string
    type: string
    label: string
    fullContent: string
    confidence: number | null
  }>
  edges: Array<{
    id: string
    source: string
    target: string
    type: string
    strength: number | null
  }>
  validity_score: number | null
}

const nodeTypeColors: Record<string, string> = {
  premise: '#e3f2fd',
  inference: '#fff3e0',
  conclusion: '#e8f5e9',
  hidden_premise: '#fce4ec',
}

const edgeTypeColors: Record<string, string> = {
  supports: '#4caf50',
  contradicts: '#f44336',
  implies: '#2196f3',
  depends_on: '#9c27b0',
}

function GraphVisualization({ data }: { data: GraphVisualization }) {
  const initialNodes: Node[] = data.nodes.map((node, index) => ({
    id: node.id,
    position: { x: (index % 3) * 300 + 50, y: Math.floor(index / 3) * 150 + 50 },
    data: {
      label: (
        <Box sx={{ p: 1 }}>
          <Chip label={node.type} size="small" sx={{ mb: 0.5 }} />
          <Typography variant="caption" sx={{ display: 'block' }}>
            {node.label}
          </Typography>
          {node.confidence !== null && (
            <Typography variant="caption" color="text.secondary">
              Confiança: {(node.confidence * 100).toFixed(0)}%
            </Typography>
          )}
        </Box>
      ),
    },
    style: {
      backgroundColor: nodeTypeColors[node.type] || '#fff',
      border: '1px solid #ccc',
      borderRadius: 8,
      width: 220,
    },
  }))

  const initialEdges: Edge[] = data.edges.map((edge) => ({
    id: edge.id,
    source: edge.source,
    target: edge.target,
    label: edge.type,
    markerEnd: { type: MarkerType.ArrowClosed },
    style: { stroke: edgeTypeColors[edge.type] || '#999' },
    animated: edge.type === 'contradicts',
  }))

  const [nodes, , onNodesChange] = useNodesState(initialNodes)
  const [edges, , onEdgesChange] = useEdgesState(initialEdges)

  return (
    <Box sx={{ height: 400, width: '100%' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        fitView
        attributionPosition="bottom-right"
      >
        <Controls />
        <Background />
      </ReactFlow>
    </Box>
  )
}

export default function LogicValidation() {
  const [page, setPage] = useState(0)
  const [rowsPerPage, setRowsPerPage] = useState(10)
  const [selectedGraph, setSelectedGraph] = useState<LogicGraphData | null>(null)
  const [detailsOpen, setDetailsOpen] = useState(false)

  const { data: graphs, isLoading, error } = useQuery({
    queryKey: ['logicGraphs'],
    queryFn: () => getLogicGraphs(100).then((res) => res.data),
  })

  const { data: vizData, isLoading: vizLoading } = useQuery({
    queryKey: ['logicGraphViz', selectedGraph?.id],
    queryFn: () => getLogicGraphVisualization(selectedGraph!.id).then((res) => res.data),
    enabled: !!selectedGraph?.id && detailsOpen,
  })

  const { data: issuesData } = useQuery({
    queryKey: ['logicGraphIssues', selectedGraph?.id],
    queryFn: () => getLogicGraphIssues(selectedGraph!.id).then((res) => res.data),
    enabled: !!selectedGraph?.id && detailsOpen,
  })

  const handleViewDetails = (graph: LogicGraphData) => {
    setSelectedGraph(graph)
    setDetailsOpen(true)
  }

  const handleCloseDetails = () => {
    setDetailsOpen(false)
    setSelectedGraph(null)
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
        Erro ao carregar grafos lógicos.
      </Alert>
    )
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
        <Hub color="info" sx={{ fontSize: 32 }} />
        <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
          Validação Lógica (GoT)
        </Typography>
      </Box>

      <Paper>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>ID</TableCell>
                <TableCell>Score de Validade</TableCell>
                <TableCell>Problemas</TableCell>
                <TableCell>Data</TableCell>
                <TableCell align="center">Ações</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {graphs
                ?.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                .map((graph: LogicGraphData) => (
                  <TableRow key={graph.id} hover>
                    <TableCell>
                      <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                        {graph.id.substring(0, 8)}...
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={graph.overall_validity_score !== null
                          ? `${(graph.overall_validity_score * 100).toFixed(0)}%`
                          : 'N/A'
                        }
                        color={
                          graph.overall_validity_score !== null
                            ? graph.overall_validity_score >= 0.7 ? 'success'
                            : graph.overall_validity_score >= 0.4 ? 'warning' : 'error'
                            : 'default'
                        }
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                        {graph.has_contradictions && (
                          <Chip icon={<ErrorIcon />} label="Contradições" color="error" size="small" />
                        )}
                        {graph.has_logic_gaps && (
                          <Chip icon={<Warning />} label="Lacunas" color="warning" size="small" />
                        )}
                        {graph.has_hidden_premises && (
                          <Chip icon={<HelpOutline />} label="Premissas Ocultas" color="info" size="small" />
                        )}
                        {graph.has_circularity && (
                          <Chip icon={<Loop />} label="Circularidade" color="secondary" size="small" />
                        )}
                        {!graph.has_contradictions && !graph.has_logic_gaps && !graph.has_hidden_premises && !graph.has_circularity && (
                          <Chip icon={<CheckCircle />} label="Sem problemas" color="success" size="small" />
                        )}
                      </Box>
                    </TableCell>
                    <TableCell>
                      {new Date(graph.created_at).toLocaleString('pt-BR')}
                    </TableCell>
                    <TableCell align="center">
                      <IconButton
                        color="primary"
                        onClick={() => handleViewDetails(graph)}
                      >
                        <Visibility />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              {(!graphs || graphs.length === 0) && (
                <TableRow>
                  <TableCell colSpan={5} align="center">
                    Nenhuma validação encontrada
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
        <TablePagination
          component="div"
          count={graphs?.length || 0}
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
            <Hub />
            Grafo Lógico
          </Box>
        </DialogTitle>
        <DialogContent dividers>
          {vizLoading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
              <CircularProgress />
            </Box>
          ) : vizData ? (
            <Box>
              <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid item xs={12} md={3}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="subtitle2" color="text.secondary">
                        Score de Validade
                      </Typography>
                      <Typography variant="h4" color={
                        vizData.validity_score !== null
                          ? vizData.validity_score >= 0.7 ? 'success.main'
                          : vizData.validity_score >= 0.4 ? 'warning.main' : 'error.main'
                          : 'text.primary'
                      }>
                        {vizData.validity_score !== null
                          ? `${(vizData.validity_score * 100).toFixed(0)}%`
                          : 'N/A'
                        }
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12} md={3}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="subtitle2" color="text.secondary">
                        Proposições
                      </Typography>
                      <Typography variant="h4">{vizData.nodes.length}</Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12} md={3}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="subtitle2" color="text.secondary">
                        Conexões
                      </Typography>
                      <Typography variant="h4">{vizData.edges.length}</Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12} md={3}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="subtitle2" color="text.secondary">
                        Problemas
                      </Typography>
                      <Typography variant="h4">{issuesData?.total_issues || 0}</Typography>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>

              <Typography variant="h6" gutterBottom>
                Visualização do Grafo
              </Typography>
              <Paper variant="outlined" sx={{ p: 1, mb: 3 }}>
                <GraphVisualization data={vizData} />
              </Paper>

              {issuesData && issuesData.total_issues > 0 && (
                <>
                  <Typography variant="h6" gutterBottom>
                    Problemas Encontrados
                  </Typography>
                  <Grid container spacing={2}>
                    {issuesData.contradictions?.length > 0 && (
                      <Grid item xs={12} md={6}>
                        <Card variant="outlined" sx={{ borderColor: 'error.main' }}>
                          <CardContent>
                            <Typography variant="subtitle2" color="error">
                              Contradições
                            </Typography>
                            <List dense>
                              {issuesData.contradictions.map((c: any, i: number) => (
                                <ListItem key={i}>
                                  <ListItemIcon>
                                    <ErrorIcon color="error" />
                                  </ListItemIcon>
                                  <ListItemText
                                    primary={c.explanation}
                                    secondary={`Severidade: ${c.severity}`}
                                  />
                                </ListItem>
                              ))}
                            </List>
                          </CardContent>
                        </Card>
                      </Grid>
                    )}
                    {issuesData.logic_gaps?.length > 0 && (
                      <Grid item xs={12} md={6}>
                        <Card variant="outlined" sx={{ borderColor: 'warning.main' }}>
                          <CardContent>
                            <Typography variant="subtitle2" color="warning.main">
                              Lacunas Lógicas
                            </Typography>
                            <List dense>
                              {issuesData.logic_gaps.map((g: any, i: number) => (
                                <ListItem key={i}>
                                  <ListItemIcon>
                                    <Warning color="warning" />
                                  </ListItemIcon>
                                  <ListItemText
                                    primary={g.missing}
                                    secondary={`Severidade: ${g.severity}`}
                                  />
                                </ListItem>
                              ))}
                            </List>
                          </CardContent>
                        </Card>
                      </Grid>
                    )}
                    {issuesData.hidden_premises?.length > 0 && (
                      <Grid item xs={12} md={6}>
                        <Card variant="outlined" sx={{ borderColor: 'info.main' }}>
                          <CardContent>
                            <Typography variant="subtitle2" color="info.main">
                              Premissas Ocultas
                            </Typography>
                            <List dense>
                              {issuesData.hidden_premises.map((p: any, i: number) => (
                                <ListItem key={i}>
                                  <ListItemIcon>
                                    <HelpOutline color="info" />
                                  </ListItemIcon>
                                  <ListItemText
                                    primary={p.premise}
                                    secondary={`Importância: ${p.importance}`}
                                  />
                                </ListItem>
                              ))}
                            </List>
                          </CardContent>
                        </Card>
                      </Grid>
                    )}
                    {issuesData.circular_references?.length > 0 && (
                      <Grid item xs={12} md={6}>
                        <Card variant="outlined" sx={{ borderColor: 'secondary.main' }}>
                          <CardContent>
                            <Typography variant="subtitle2" color="secondary">
                              Circularidade
                            </Typography>
                            <List dense>
                              {issuesData.circular_references.map((c: any, i: number) => (
                                <ListItem key={i}>
                                  <ListItemIcon>
                                    <Loop color="secondary" />
                                  </ListItemIcon>
                                  <ListItemText
                                    primary={c.explanation}
                                    secondary={`Ciclo: ${c.cycle}`}
                                  />
                                </ListItem>
                              ))}
                            </List>
                          </CardContent>
                        </Card>
                      </Grid>
                    )}
                  </Grid>
                </>
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
