import { useState, useCallback } from 'react'
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
} from '@mui/material'
import { Visibility, AccountTree } from '@mui/icons-material'
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
import { getPathAnalyses, getPathAnalysisTree } from '../services/api'

interface TreeNode {
  name: string
  fullName?: string
  score?: number
  isPruned?: boolean
  pruneReason?: string
  children?: TreeNode[]
}

interface PathAnalysisData {
  id: string
  original_problem: string
  decomposition: any
  total_nodes_explored: number
  total_paths_pruned: number
  model_provider: string
  model_name: string
  created_at: string
  selected_path: any
}

function convertTreeToFlow(tree: TreeNode, parentId?: string, x = 0, y = 0, level = 0): { nodes: Node[], edges: Edge[] } {
  const nodes: Node[] = []
  const edges: Edge[] = []
  const nodeId = `${level}-${x}-${tree.name.substring(0, 10)}`

  nodes.push({
    id: nodeId,
    position: { x: x * 250, y: level * 150 },
    data: {
      label: (
        <Box sx={{ p: 1, textAlign: 'center' }}>
          <Typography variant="caption" sx={{ display: 'block', fontWeight: 'bold' }}>
            {tree.name}
          </Typography>
          {tree.score !== undefined && (
            <Chip
              label={`${tree.score}%`}
              size="small"
              color={tree.score >= 70 ? 'success' : tree.score >= 40 ? 'warning' : 'error'}
              sx={{ mt: 0.5 }}
            />
          )}
          {tree.isPruned && (
            <Chip label="Podado" size="small" color="default" sx={{ mt: 0.5 }} />
          )}
        </Box>
      ),
    },
    style: {
      backgroundColor: tree.isPruned ? '#ffebee' : tree.score && tree.score >= 70 ? '#e8f5e9' : '#fff',
      border: '1px solid #ccc',
      borderRadius: 8,
      width: 200,
    },
  })

  if (parentId) {
    edges.push({
      id: `${parentId}-${nodeId}`,
      source: parentId,
      target: nodeId,
      markerEnd: { type: MarkerType.ArrowClosed },
      style: { stroke: tree.isPruned ? '#ccc' : '#1976d2' },
    })
  }

  if (tree.children) {
    tree.children.forEach((child, index) => {
      const childResult = convertTreeToFlow(
        child,
        nodeId,
        x + index - (tree.children!.length - 1) / 2,
        y,
        level + 1
      )
      nodes.push(...childResult.nodes)
      edges.push(...childResult.edges)
    })
  }

  return { nodes, edges }
}

function TreeVisualization({ treeData }: { treeData: TreeNode }) {
  const { nodes: initialNodes, edges: initialEdges } = convertTreeToFlow(treeData)
  const [nodes, , onNodesChange] = useNodesState(initialNodes)
  const [edges, , onEdgesChange] = useEdgesState(initialEdges)

  return (
    <Box sx={{ height: 500, width: '100%' }}>
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

export default function PathAnalysis() {
  const [page, setPage] = useState(0)
  const [rowsPerPage, setRowsPerPage] = useState(10)
  const [selectedAnalysis, setSelectedAnalysis] = useState<PathAnalysisData | null>(null)
  const [detailsOpen, setDetailsOpen] = useState(false)

  const { data: analyses, isLoading, error } = useQuery({
    queryKey: ['pathAnalyses'],
    queryFn: () => getPathAnalyses(100).then((res) => res.data),
  })

  const { data: treeData, isLoading: treeLoading } = useQuery({
    queryKey: ['pathAnalysisTree', selectedAnalysis?.id],
    queryFn: () => getPathAnalysisTree(selectedAnalysis!.id).then((res) => res.data),
    enabled: !!selectedAnalysis?.id && detailsOpen,
  })

  const handleViewDetails = (analysis: PathAnalysisData) => {
    setSelectedAnalysis(analysis)
    setDetailsOpen(true)
  }

  const handleCloseDetails = () => {
    setDetailsOpen(false)
    setSelectedAnalysis(null)
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
        Erro ao carregar análises de caminho.
      </Alert>
    )
  }

  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
        <AccountTree color="secondary" sx={{ fontSize: 32 }} />
        <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
          Análise de Caminhos (ToT)
        </Typography>
      </Box>

      <Paper>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Problema</TableCell>
                <TableCell>Nós Explorados</TableCell>
                <TableCell>Caminhos Podados</TableCell>
                <TableCell>Modelo</TableCell>
                <TableCell>Data</TableCell>
                <TableCell align="center">Ações</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {analyses
                ?.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                .map((analysis: PathAnalysisData) => (
                  <TableRow key={analysis.id} hover>
                    <TableCell>
                      {analysis.original_problem.length > 80
                        ? analysis.original_problem.substring(0, 80) + '...'
                        : analysis.original_problem}
                    </TableCell>
                    <TableCell>
                      <Chip label={analysis.total_nodes_explored} color="primary" size="small" />
                    </TableCell>
                    <TableCell>
                      <Chip label={analysis.total_paths_pruned} color="warning" size="small" />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={`${analysis.model_provider}`}
                        size="small"
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>
                      {new Date(analysis.created_at).toLocaleString('pt-BR')}
                    </TableCell>
                    <TableCell align="center">
                      <IconButton
                        color="primary"
                        onClick={() => handleViewDetails(analysis)}
                      >
                        <Visibility />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              {(!analyses || analyses.length === 0) && (
                <TableRow>
                  <TableCell colSpan={6} align="center">
                    Nenhuma análise encontrada
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
        <TablePagination
          component="div"
          count={analyses?.length || 0}
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
            <AccountTree />
            Árvore de Decisão
          </Box>
        </DialogTitle>
        <DialogContent dividers>
          {treeLoading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
              <CircularProgress />
            </Box>
          ) : treeData ? (
            <Box>
              <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid item xs={12} md={4}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="subtitle2" color="text.secondary">
                        Nós Explorados
                      </Typography>
                      <Typography variant="h4">{treeData.stats.total_nodes}</Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Card variant="outlined">
                    <CardContent>
                      <Typography variant="subtitle2" color="text.secondary">
                        Caminhos Podados
                      </Typography>
                      <Typography variant="h4">{treeData.stats.pruned_nodes}</Typography>
                    </CardContent>
                  </Card>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Card variant="outlined" sx={{ backgroundColor: 'success.light' }}>
                    <CardContent>
                      <Typography variant="subtitle2" color="success.dark">
                        Melhor Caminho
                      </Typography>
                      <Typography variant="body2">
                        {treeData.selected_path?.selected_approach || 'N/A'}
                      </Typography>
                      {treeData.selected_path?.score && (
                        <Chip
                          label={`Score: ${treeData.selected_path.score}%`}
                          color="success"
                          size="small"
                          sx={{ mt: 1 }}
                        />
                      )}
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>

              <Typography variant="h6" gutterBottom>
                Visualização da Árvore
              </Typography>
              <Paper variant="outlined" sx={{ p: 1 }}>
                <TreeVisualization treeData={treeData.tree} />
              </Paper>
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
