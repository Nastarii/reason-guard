import { useQuery } from '@tanstack/react-query'
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  CircularProgress,
  Alert,
} from '@mui/material'
import {
  Assessment,
  TrendingUp,
  Warning,
  CheckCircle,
  Psychology,
  AccountTree,
  Hub,
  Schedule,
} from '@mui/icons-material'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
} from 'recharts'
import { getDashboardStats, getRecentActivity, getDashboardSummary } from '../services/api'

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042']

interface StatsCardProps {
  title: string
  value: string | number
  icon: React.ReactNode
  color: string
  subtitle?: string
}

function StatsCard({ title, value, icon, color, subtitle }: StatsCardProps) {
  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Box>
            <Typography color="text.secondary" variant="body2" gutterBottom>
              {title}
            </Typography>
            <Typography variant="h4" component="div" sx={{ fontWeight: 'bold', color }}>
              {value}
            </Typography>
            {subtitle && (
              <Typography variant="caption" color="text.secondary">
                {subtitle}
              </Typography>
            )}
          </Box>
          <Box sx={{ color, opacity: 0.8 }}>{icon}</Box>
        </Box>
      </CardContent>
    </Card>
  )
}

const getActivityIcon = (type: string) => {
  switch (type) {
    case 'reasoning_trace':
      return <Psychology color="primary" />
    case 'path_analysis':
      return <AccountTree color="secondary" />
    case 'logic_graph':
      return <Hub color="info" />
    case 'consistency_check':
      return <CheckCircle color="success" />
    default:
      return <Assessment />
  }
}

const getStatusChip = (status: string) => {
  switch (status) {
    case 'completed':
      return <Chip label="Concluído" color="success" size="small" />
    case 'alert':
      return <Chip label="Alerta" color="error" size="small" />
    case 'warning':
      return <Chip label="Atenção" color="warning" size="small" />
    default:
      return <Chip label={status} size="small" />
  }
}

export default function Dashboard() {
  const { data: stats, isLoading: statsLoading, error: statsError } = useQuery({
    queryKey: ['dashboardStats'],
    queryFn: () => getDashboardStats().then((res) => res.data),
    refetchInterval: 30000,
  })

  const { data: activity, isLoading: activityLoading } = useQuery({
    queryKey: ['recentActivity'],
    queryFn: () => getRecentActivity(10).then((res) => res.data),
    refetchInterval: 30000,
  })

  const { data: summary, isLoading: summaryLoading } = useQuery({
    queryKey: ['dashboardSummary'],
    queryFn: () => getDashboardSummary(7).then((res) => res.data),
    refetchInterval: 60000,
  })

  if (statsLoading || activityLoading || summaryLoading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
        <CircularProgress />
      </Box>
    )
  }

  if (statsError) {
    return (
      <Alert severity="error" sx={{ mb: 2 }}>
        Erro ao carregar dados do dashboard. Verifique a conexão com o servidor.
      </Alert>
    )
  }

  const issueData = summary?.issue_breakdown
    ? Object.entries(summary.issue_breakdown).map(([key, value]) => ({
        name: key === 'contradictions' ? 'Contradições' :
              key === 'logic_gaps' ? 'Lacunas Lógicas' :
              key === 'hidden_premises' ? 'Premissas Ocultas' : 'Circularidade',
        value: value as number,
      }))
    : []

  const consistencyData = summary?.consistency_distribution
    ? [
        { name: 'Alta', value: summary.consistency_distribution.high },
        { name: 'Média', value: summary.consistency_distribution.medium },
        { name: 'Baixa', value: summary.consistency_distribution.low },
      ]
    : []

  return (
    <Box>
      <Typography variant="h5" gutterBottom sx={{ fontWeight: 'bold', mb: 3 }}>
        Visão Geral
      </Typography>

      {/* KPI Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatsCard
            title="Total de Decisões"
            value={stats?.total_decisions || 0}
            icon={<Assessment sx={{ fontSize: 40 }} />}
            color="#1976d2"
            subtitle={`${stats?.decisions_today || 0} hoje`}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatsCard
            title="Taxa de Consistência"
            value={`${stats?.consistency_rate || 0}%`}
            icon={<TrendingUp sx={{ fontSize: 40 }} />}
            color="#2e7d32"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatsCard
            title="Alertas Críticos"
            value={stats?.critical_alerts || 0}
            icon={<Warning sx={{ fontSize: 40 }} />}
            color="#ed6c02"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatsCard
            title="Score de Validade Médio"
            value={`${stats?.average_validity_score || 0}%`}
            icon={<CheckCircle sx={{ fontSize: 40 }} />}
            color="#9c27b0"
          />
        </Grid>
      </Grid>

      {/* Charts */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3, height: 350 }}>
            <Typography variant="h6" gutterBottom>
              Decisões por Dia (Últimos 7 dias)
            </Typography>
            <ResponsiveContainer width="100%" height="85%">
              <LineChart data={summary?.daily_decisions || []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="count" stroke="#1976d2" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, height: 350 }}>
            <Typography variant="h6" gutterBottom>
              Distribuição de Consistência
            </Typography>
            <ResponsiveContainer width="100%" height="85%">
              <PieChart>
                <Pie
                  data={consistencyData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                >
                  {consistencyData.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, height: 350 }}>
            <Typography variant="h6" gutterBottom>
              Problemas Identificados
            </Typography>
            <ResponsiveContainer width="100%" height="85%">
              <BarChart data={issueData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis dataKey="name" type="category" width={120} />
                <Tooltip />
                <Bar dataKey="value" fill="#ed6c02" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, height: 350, overflow: 'auto' }}>
            <Typography variant="h6" gutterBottom>
              Atividade Recente
            </Typography>
            <List dense>
              {activity?.map((item: any) => (
                <ListItem key={item.id} divider>
                  <ListItemIcon>{getActivityIcon(item.type)}</ListItemIcon>
                  <ListItemText
                    primary={item.description}
                    secondary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 0.5 }}>
                        <Schedule sx={{ fontSize: 14 }} />
                        <Typography variant="caption">
                          {new Date(item.created_at).toLocaleString('pt-BR')}
                        </Typography>
                      </Box>
                    }
                  />
                  {getStatusChip(item.status)}
                </ListItem>
              ))}
              {(!activity || activity.length === 0) && (
                <ListItem>
                  <ListItemText primary="Nenhuma atividade recente" />
                </ListItem>
              )}
            </List>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  )
}
