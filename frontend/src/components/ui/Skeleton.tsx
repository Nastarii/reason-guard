/**
 * Skeleton Components - ReasonGuard Design System
 *
 * Skeleton screens que mimetizam o layout final para reduzir ansiedade de espera.
 * Usa animação de shimmer suave para indicar carregamento.
 */

import { Box, Skeleton as MuiSkeleton, Paper, Grid, Card, CardContent, styled } from '@mui/material'
import { colors, motion, borders } from '../../design-system/tokens'

// =============================================================================
// SKELETON BASE COM SHIMMER
// =============================================================================

const ShimmerSkeleton = styled(MuiSkeleton)({
  backgroundColor: colors.neutral[100],
  '&::after': {
    background: `linear-gradient(
      90deg,
      transparent,
      rgba(255, 255, 255, 0.6),
      transparent
    )`,
    animation: `shimmer 1.5s infinite`,
  },
  '@keyframes shimmer': {
    '0%': { transform: 'translateX(-100%)' },
    '100%': { transform: 'translateX(100%)' },
  },
})

// =============================================================================
// SKELETON PARA TEXTO
// =============================================================================

interface TextSkeletonProps {
  lines?: number
  lastLineWidth?: string | number
}

export function TextSkeleton({ lines = 3, lastLineWidth = '60%' }: TextSkeletonProps) {
  return (
    <Box sx={{ width: '100%' }}>
      {Array.from({ length: lines }).map((_, index) => (
        <ShimmerSkeleton
          key={index}
          variant="text"
          animation="wave"
          sx={{
            height: 16,
            mb: index < lines - 1 ? 1 : 0,
            width: index === lines - 1 ? lastLineWidth : '100%',
            borderRadius: borders.radius.sm,
          }}
        />
      ))}
    </Box>
  )
}

// =============================================================================
// SKELETON PARA CARDS DE ESTATÍSTICAS
// =============================================================================

export function StatCardSkeleton() {
  return (
    <Card
      variant="outlined"
      sx={{
        height: '100%',
        borderColor: colors.border.light,
      }}
    >
      <CardContent>
        <ShimmerSkeleton
          variant="text"
          width="40%"
          height={14}
          animation="wave"
          sx={{ mb: 1.5, borderRadius: borders.radius.sm }}
        />
        <ShimmerSkeleton
          variant="text"
          width="60%"
          height={36}
          animation="wave"
          sx={{ borderRadius: borders.radius.sm }}
        />
      </CardContent>
    </Card>
  )
}

export function StatCardsGridSkeleton({ count = 4 }: { count?: number }) {
  return (
    <Grid container spacing={3}>
      {Array.from({ length: count }).map((_, index) => (
        <Grid item xs={12} sm={6} md={3} key={index}>
          <StatCardSkeleton />
        </Grid>
      ))}
    </Grid>
  )
}

// =============================================================================
// SKELETON PARA TABELAS
// =============================================================================

interface TableSkeletonProps {
  rows?: number
  columns?: number
  showHeader?: boolean
}

export function TableSkeleton({ rows = 5, columns = 5, showHeader = true }: TableSkeletonProps) {
  return (
    <Paper
      variant="outlined"
      sx={{
        overflow: 'hidden',
        borderColor: colors.border.light,
      }}
    >
      {/* Header */}
      {showHeader && (
        <Box
          sx={{
            display: 'flex',
            gap: 2,
            p: 2,
            borderBottom: `1px solid ${colors.border.light}`,
            backgroundColor: colors.neutral[50],
          }}
        >
          {Array.from({ length: columns }).map((_, index) => (
            <ShimmerSkeleton
              key={index}
              variant="text"
              animation="wave"
              sx={{
                flex: index === 0 ? 2 : 1,
                height: 16,
                borderRadius: borders.radius.sm,
              }}
            />
          ))}
        </Box>
      )}

      {/* Rows */}
      {Array.from({ length: rows }).map((_, rowIndex) => (
        <Box
          key={rowIndex}
          sx={{
            display: 'flex',
            gap: 2,
            p: 2,
            borderBottom: rowIndex < rows - 1 ? `1px solid ${colors.border.light}` : 'none',
          }}
        >
          {Array.from({ length: columns }).map((_, colIndex) => (
            <ShimmerSkeleton
              key={colIndex}
              variant="text"
              animation="wave"
              sx={{
                flex: colIndex === 0 ? 2 : 1,
                height: 20,
                borderRadius: borders.radius.sm,
              }}
            />
          ))}
        </Box>
      ))}
    </Paper>
  )
}

// =============================================================================
// SKELETON PARA GRAFOS/ÁRVORES
// =============================================================================

export function GraphSkeleton() {
  return (
    <Paper
      variant="outlined"
      sx={{
        height: 400,
        p: 3,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        gap: 3,
        borderColor: colors.border.light,
      }}
    >
      {/* Nós simulados */}
      <Box sx={{ display: 'flex', gap: 4 }}>
        <ShimmerSkeleton
          variant="rounded"
          width={120}
          height={60}
          animation="wave"
          sx={{ borderRadius: borders.radius.md }}
        />
      </Box>
      <Box sx={{ display: 'flex', gap: 4 }}>
        <ShimmerSkeleton
          variant="rounded"
          width={100}
          height={50}
          animation="wave"
          sx={{ borderRadius: borders.radius.md }}
        />
        <ShimmerSkeleton
          variant="rounded"
          width={100}
          height={50}
          animation="wave"
          sx={{ borderRadius: borders.radius.md }}
        />
        <ShimmerSkeleton
          variant="rounded"
          width={100}
          height={50}
          animation="wave"
          sx={{ borderRadius: borders.radius.md }}
        />
      </Box>
      <Box sx={{ display: 'flex', gap: 4 }}>
        <ShimmerSkeleton
          variant="rounded"
          width={80}
          height={40}
          animation="wave"
          sx={{ borderRadius: borders.radius.md }}
        />
        <ShimmerSkeleton
          variant="rounded"
          width={80}
          height={40}
          animation="wave"
          sx={{ borderRadius: borders.radius.md }}
        />
      </Box>
    </Paper>
  )
}

export function TreeSkeleton() {
  return (
    <Paper
      variant="outlined"
      sx={{
        height: 500,
        p: 3,
        borderColor: colors.border.light,
      }}
    >
      {/* Estrutura de árvore simulada */}
      <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2 }}>
        {/* Raiz */}
        <ShimmerSkeleton
          variant="rounded"
          width={180}
          height={70}
          animation="wave"
          sx={{ borderRadius: borders.radius.md }}
        />

        {/* Nível 1 */}
        <Box sx={{ display: 'flex', gap: 6, mt: 2 }}>
          {[1, 2, 3].map((i) => (
            <ShimmerSkeleton
              key={i}
              variant="rounded"
              width={140}
              height={60}
              animation="wave"
              sx={{ borderRadius: borders.radius.md }}
            />
          ))}
        </Box>

        {/* Nível 2 */}
        <Box sx={{ display: 'flex', gap: 3, mt: 2 }}>
          {[1, 2, 3, 4, 5].map((i) => (
            <ShimmerSkeleton
              key={i}
              variant="rounded"
              width={100}
              height={50}
              animation="wave"
              sx={{ borderRadius: borders.radius.md }}
            />
          ))}
        </Box>
      </Box>
    </Paper>
  )
}

// =============================================================================
// SKELETON PARA LISTA DE CARDS
// =============================================================================

export function CardListSkeleton({ count = 3 }: { count?: number }) {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
      {Array.from({ length: count }).map((_, index) => (
        <Card
          key={index}
          variant="outlined"
          sx={{ borderColor: colors.border.light }}
        >
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
              <ShimmerSkeleton
                variant="text"
                width="30%"
                height={24}
                animation="wave"
                sx={{ borderRadius: borders.radius.sm }}
              />
              <ShimmerSkeleton
                variant="rounded"
                width={80}
                height={24}
                animation="wave"
                sx={{ borderRadius: borders.radius.full }}
              />
            </Box>
            <TextSkeleton lines={2} lastLineWidth="80%" />
          </CardContent>
        </Card>
      ))}
    </Box>
  )
}

// =============================================================================
// SKELETON PARA CHAT
// =============================================================================

export function ChatMessageSkeleton({ isUser = false }: { isUser?: boolean }) {
  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: isUser ? 'flex-end' : 'flex-start',
        mb: 2,
      }}
    >
      <Box
        sx={{
          maxWidth: '70%',
          p: 2,
          borderRadius: borders.radius.lg,
          backgroundColor: isUser ? colors.accent.light : colors.neutral[100],
        }}
      >
        <TextSkeleton lines={isUser ? 1 : 3} lastLineWidth="70%" />
      </Box>
    </Box>
  )
}

export function ChatSkeleton() {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1, p: 2 }}>
      <ChatMessageSkeleton isUser />
      <ChatMessageSkeleton />
      <ChatMessageSkeleton isUser />
      <ChatMessageSkeleton />
    </Box>
  )
}

// =============================================================================
// SKELETON PARA DASHBOARD
// =============================================================================

export function DashboardSkeleton() {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
      {/* Header */}
      <Box>
        <ShimmerSkeleton
          variant="text"
          width={200}
          height={32}
          animation="wave"
          sx={{ mb: 1, borderRadius: borders.radius.sm }}
        />
        <ShimmerSkeleton
          variant="text"
          width={300}
          height={20}
          animation="wave"
          sx={{ borderRadius: borders.radius.sm }}
        />
      </Box>

      {/* Stats Cards */}
      <StatCardsGridSkeleton count={4} />

      {/* Charts */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Paper
            variant="outlined"
            sx={{
              height: 300,
              p: 3,
              borderColor: colors.border.light,
            }}
          >
            <ShimmerSkeleton
              variant="text"
              width={150}
              height={24}
              animation="wave"
              sx={{ mb: 3, borderRadius: borders.radius.sm }}
            />
            <ShimmerSkeleton
              variant="rounded"
              width="100%"
              height={220}
              animation="wave"
              sx={{ borderRadius: borders.radius.md }}
            />
          </Paper>
        </Grid>
        <Grid item xs={12} md={4}>
          <Paper
            variant="outlined"
            sx={{
              height: 300,
              p: 3,
              borderColor: colors.border.light,
            }}
          >
            <ShimmerSkeleton
              variant="text"
              width={120}
              height={24}
              animation="wave"
              sx={{ mb: 3, borderRadius: borders.radius.sm }}
            />
            <Box sx={{ display: 'flex', justifyContent: 'center' }}>
              <ShimmerSkeleton
                variant="circular"
                width={180}
                height={180}
                animation="wave"
              />
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  )
}

// =============================================================================
// SKELETON PARA PÁGINA GENÉRICA
// =============================================================================

export function PageSkeleton() {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
      {/* Page Header */}
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
        <ShimmerSkeleton
          variant="circular"
          width={32}
          height={32}
          animation="wave"
        />
        <ShimmerSkeleton
          variant="text"
          width={250}
          height={28}
          animation="wave"
          sx={{ borderRadius: borders.radius.sm }}
        />
      </Box>

      {/* Content */}
      <TableSkeleton rows={8} columns={6} />
    </Box>
  )
}

// =============================================================================
// LOADING INDICATOR SUTIL
// =============================================================================

export function LoadingBar() {
  return (
    <Box
      sx={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        height: 3,
        backgroundColor: colors.neutral[200],
        zIndex: 9999,
        overflow: 'hidden',
      }}
    >
      <Box
        sx={{
          position: 'absolute',
          top: 0,
          left: 0,
          height: '100%',
          width: '30%',
          backgroundColor: colors.accent.main,
          animation: 'loadingBar 1.5s infinite ease-in-out',
          '@keyframes loadingBar': {
            '0%': { transform: 'translateX(-100%)' },
            '50%': { transform: 'translateX(200%)' },
            '100%': { transform: 'translateX(400%)' },
          },
        }}
      />
    </Box>
  )
}

// =============================================================================
// EXPORTS
// =============================================================================

export { ShimmerSkeleton }
