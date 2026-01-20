import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  Box,
  Paper,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Alert,
  Chip,
  Tooltip,
  CircularProgress,
  Snackbar,
} from '@mui/material'
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  ContentCopy as CopyIcon,
  Key as KeyIcon,
  Block as BlockIcon,
} from '@mui/icons-material'
import { getApiTokens, createApiToken, deleteApiToken, revokeApiToken } from '../services/api'

interface ApiToken {
  id: string
  name: string
  token_prefix: string
  description?: string
  is_active: boolean
  last_used_at?: string
  expires_at?: string
  created_at: string
}

interface NewTokenResponse {
  id: string
  name: string
  token: string
  token_prefix: string
  description?: string
  expires_at?: string
  created_at: string
  message: string
}

export default function Settings() {
  const queryClient = useQueryClient()
  const [openCreateDialog, setOpenCreateDialog] = useState(false)
  const [openTokenDialog, setOpenTokenDialog] = useState(false)
  const [newToken, setNewToken] = useState<NewTokenResponse | null>(null)
  const [tokenName, setTokenName] = useState('')
  const [tokenDescription, setTokenDescription] = useState('')
  const [snackbarOpen, setSnackbarOpen] = useState(false)
  const [snackbarMessage, setSnackbarMessage] = useState('')

  const { data: tokens, isLoading } = useQuery({
    queryKey: ['apiTokens'],
    queryFn: () => getApiTokens().then((res) => res.data as ApiToken[]),
  })

  const createMutation = useMutation({
    mutationFn: (data: { name: string; description?: string }) =>
      createApiToken(data).then((res) => res.data as NewTokenResponse),
    onSuccess: (data) => {
      setNewToken(data)
      setOpenCreateDialog(false)
      setOpenTokenDialog(true)
      setTokenName('')
      setTokenDescription('')
      queryClient.invalidateQueries({ queryKey: ['apiTokens'] })
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => deleteApiToken(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['apiTokens'] })
      showSnackbar('Token removido com sucesso')
    },
  })

  const revokeMutation = useMutation({
    mutationFn: (id: string) => revokeApiToken(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['apiTokens'] })
      showSnackbar('Token revogado com sucesso')
    },
  })

  const showSnackbar = (message: string) => {
    setSnackbarMessage(message)
    setSnackbarOpen(true)
  }

  const handleCreateToken = () => {
    if (!tokenName.trim()) return
    createMutation.mutate({
      name: tokenName,
      description: tokenDescription || undefined,
    })
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    showSnackbar('Token copiado para a área de transferência')
  }

  const formatDate = (dateStr?: string) => {
    if (!dateStr) return '-'
    return new Date(dateStr).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  return (
    <Box>
      <Typography variant="h5" gutterBottom sx={{ fontWeight: 'bold', mb: 3 }}>
        Configurações
      </Typography>

      <Paper sx={{ p: 3, mb: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Box>
            <Typography variant="h6" gutterBottom>
              Tokens de API
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Gerencie seus tokens de acesso à API do ReasonGuard. Use esses tokens para integrar
              aplicações externas com o ReasonGuard.
            </Typography>
          </Box>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setOpenCreateDialog(true)}
          >
            Novo Token
          </Button>
        </Box>

        {isLoading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
            <CircularProgress />
          </Box>
        ) : tokens && tokens.length > 0 ? (
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Nome</TableCell>
                  <TableCell>Token</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Último Uso</TableCell>
                  <TableCell>Criado em</TableCell>
                  <TableCell align="right">Ações</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {tokens.map((token) => (
                  <TableRow key={token.id}>
                    <TableCell>
                      <Box>
                        <Typography variant="body2" fontWeight="medium">
                          {token.name}
                        </Typography>
                        {token.description && (
                          <Typography variant="caption" color="text.secondary">
                            {token.description}
                          </Typography>
                        )}
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <KeyIcon fontSize="small" color="action" />
                        <Typography variant="body2" fontFamily="monospace">
                          {token.token_prefix}...
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      {token.is_active ? (
                        <Chip label="Ativo" color="success" size="small" />
                      ) : (
                        <Chip label="Revogado" color="error" size="small" />
                      )}
                    </TableCell>
                    <TableCell>{formatDate(token.last_used_at)}</TableCell>
                    <TableCell>{formatDate(token.created_at)}</TableCell>
                    <TableCell align="right">
                      {token.is_active && (
                        <Tooltip title="Revogar token">
                          <IconButton
                            size="small"
                            onClick={() => revokeMutation.mutate(token.id)}
                            disabled={revokeMutation.isPending}
                          >
                            <BlockIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      )}
                      <Tooltip title="Excluir token">
                        <IconButton
                          size="small"
                          color="error"
                          onClick={() => deleteMutation.mutate(token.id)}
                          disabled={deleteMutation.isPending}
                        >
                          <DeleteIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        ) : (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <KeyIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
            <Typography variant="body1" color="text.secondary">
              Nenhum token de API criado ainda.
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Crie um token para começar a integrar suas aplicações.
            </Typography>
          </Box>
        )}
      </Paper>

      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Como usar os tokens
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          Use o token no header de autorização das suas requisições HTTP:
        </Typography>
        <Box
          component="pre"
          sx={{
            backgroundColor: 'grey.100',
            p: 2,
            borderRadius: 1,
            overflow: 'auto',
            fontSize: '0.875rem',
          }}
        >
          {`Authorization: Bearer rg_seu_token_aqui`}
        </Box>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
          Exemplo com curl:
        </Typography>
        <Box
          component="pre"
          sx={{
            backgroundColor: 'grey.100',
            p: 2,
            borderRadius: 1,
            overflow: 'auto',
            fontSize: '0.875rem',
          }}
        >
          {`curl -X POST \\
  -H "Authorization: Bearer rg_seu_token_aqui" \\
  -H "Content-Type: application/json" \\
  -d '{"prompt": "Sua pergunta aqui"}' \\
  http://localhost:8000/proxy/chat`}
        </Box>
      </Paper>

      {/* Dialog para criar novo token */}
      <Dialog open={openCreateDialog} onClose={() => setOpenCreateDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Criar Novo Token de API</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Nome do Token"
            placeholder="Ex: Integração Produção"
            fullWidth
            value={tokenName}
            onChange={(e) => setTokenName(e.target.value)}
            sx={{ mb: 2 }}
          />
          <TextField
            margin="dense"
            label="Descrição (opcional)"
            placeholder="Ex: Token usado para integração com sistema X"
            fullWidth
            multiline
            rows={2}
            value={tokenDescription}
            onChange={(e) => setTokenDescription(e.target.value)}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenCreateDialog(false)}>Cancelar</Button>
          <Button
            variant="contained"
            onClick={handleCreateToken}
            disabled={!tokenName.trim() || createMutation.isPending}
          >
            {createMutation.isPending ? 'Criando...' : 'Criar Token'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Dialog para mostrar token criado */}
      <Dialog open={openTokenDialog} onClose={() => setOpenTokenDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Token Criado com Sucesso</DialogTitle>
        <DialogContent>
          <Alert severity="warning" sx={{ mb: 2 }}>
            {newToken?.message}
          </Alert>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
            Seu token de API:
          </Typography>
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 1,
              backgroundColor: 'grey.100',
              p: 2,
              borderRadius: 1,
            }}
          >
            <Typography
              variant="body2"
              fontFamily="monospace"
              sx={{ flex: 1, wordBreak: 'break-all' }}
            >
              {newToken?.token}
            </Typography>
            <IconButton
              size="small"
              onClick={() => newToken && copyToClipboard(newToken.token)}
            >
              <CopyIcon fontSize="small" />
            </IconButton>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button
            variant="contained"
            onClick={() => {
              newToken && copyToClipboard(newToken.token)
              setOpenTokenDialog(false)
            }}
            startIcon={<CopyIcon />}
          >
            Copiar e Fechar
          </Button>
        </DialogActions>
      </Dialog>

      <Snackbar
        open={snackbarOpen}
        autoHideDuration={3000}
        onClose={() => setSnackbarOpen(false)}
        message={snackbarMessage}
      />
    </Box>
  )
}
