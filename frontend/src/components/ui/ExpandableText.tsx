/**
 * ExpandableText Component - ReasonGuard Design System
 *
 * Componente para exibir textos longos com opção de expandir/colapsar.
 * Resolve o problema de textos truncados em visualizações.
 */

import { useState, useRef, useEffect } from 'react'
import {
  Box,
  Typography,
  Button,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
  Collapse,
  styled,
} from '@mui/material'
import {
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  OpenInFull as OpenInFullIcon,
  Close as CloseIcon,
} from '@mui/icons-material'
import { colors, borders, motion } from '../../design-system/tokens'

// =============================================================================
// STYLED COMPONENTS
// =============================================================================

const TruncatedText = styled(Typography)({
  overflow: 'hidden',
  textOverflow: 'ellipsis',
  display: '-webkit-box',
  WebkitBoxOrient: 'vertical',
  wordBreak: 'break-word',
})

const ExpandButton = styled(Button)({
  minWidth: 'auto',
  padding: '2px 8px',
  fontSize: '0.75rem',
  textTransform: 'none',
  color: colors.accent.main,
  '&:hover': {
    backgroundColor: `${colors.accent.main}08`,
  },
})

const FullScreenButton = styled(IconButton)({
  padding: 4,
  color: colors.text.tertiary,
  '&:hover': {
    color: colors.accent.main,
    backgroundColor: `${colors.accent.main}08`,
  },
})

// =============================================================================
// EXPANDABLE TEXT - INLINE
// =============================================================================

interface ExpandableTextProps {
  text: string
  maxLines?: number
  maxLength?: number
  variant?: 'body1' | 'body2' | 'caption'
  showFullScreenOption?: boolean
}

export function ExpandableText({
  text,
  maxLines = 3,
  maxLength = 200,
  variant = 'body2',
  showFullScreenOption = true,
}: ExpandableTextProps) {
  const [expanded, setExpanded] = useState(false)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [isTruncated, setIsTruncated] = useState(false)
  const textRef = useRef<HTMLDivElement>(null)

  const needsTruncation = text.length > maxLength

  useEffect(() => {
    if (textRef.current) {
      setIsTruncated(
        textRef.current.scrollHeight > textRef.current.clientHeight ||
        text.length > maxLength
      )
    }
  }, [text, maxLength])

  if (!needsTruncation) {
    return (
      <Typography variant={variant} sx={{ wordBreak: 'break-word' }}>
        {text}
      </Typography>
    )
  }

  return (
    <Box>
      <Collapse in={expanded} collapsedSize={maxLines * 20}>
        <Typography
          ref={textRef}
          variant={variant}
          sx={{
            wordBreak: 'break-word',
            whiteSpace: 'pre-wrap',
          }}
        >
          {text}
        </Typography>
      </Collapse>

      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mt: 0.5 }}>
        <ExpandButton
          size="small"
          onClick={() => setExpanded(!expanded)}
          endIcon={expanded ? <ExpandLessIcon fontSize="small" /> : <ExpandMoreIcon fontSize="small" />}
        >
          {expanded ? 'Ver menos' : 'Ver mais'}
        </ExpandButton>

        {showFullScreenOption && (
          <Tooltip title="Ver em tela cheia" arrow>
            <FullScreenButton size="small" onClick={() => setDialogOpen(true)}>
              <OpenInFullIcon fontSize="small" />
            </FullScreenButton>
          </Tooltip>
        )}
      </Box>

      {/* Full Screen Dialog */}
      <Dialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6">Conteúdo Completo</Typography>
          <IconButton onClick={() => setDialogOpen(false)} size="small">
            <CloseIcon />
          </IconButton>
        </DialogTitle>
        <DialogContent dividers>
          <Typography
            variant="body1"
            sx={{
              whiteSpace: 'pre-wrap',
              wordBreak: 'break-word',
              lineHeight: 1.8,
            }}
          >
            {text}
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Fechar</Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

// =============================================================================
// TOOLTIP TEXT - PARA NÓS DE GRAFOS/ÁRVORES
// =============================================================================

interface TooltipTextProps {
  text: string
  maxLength?: number
  children?: React.ReactNode
}

export function TooltipText({ text, maxLength = 50, children }: TooltipTextProps) {
  const needsTruncation = text.length > maxLength
  const displayText = needsTruncation ? text.substring(0, maxLength) + '...' : text

  if (!needsTruncation) {
    return children ? <>{children}</> : <span>{text}</span>
  }

  return (
    <Tooltip
      title={
        <Box sx={{ p: 1, maxWidth: 400 }}>
          <Typography
            variant="body2"
            sx={{
              whiteSpace: 'pre-wrap',
              wordBreak: 'break-word',
            }}
          >
            {text}
          </Typography>
        </Box>
      }
      arrow
      placement="top"
      enterDelay={300}
      leaveDelay={200}
    >
      {children ? <Box sx={{ cursor: 'pointer' }}>{children}</Box> : <span style={{ cursor: 'pointer' }}>{displayText}</span>}
    </Tooltip>
  )
}

// =============================================================================
// CLICKABLE EXPANDABLE NODE - PARA NÓS DE GRAFOS
// =============================================================================

interface ExpandableNodeProps {
  label: string
  fullContent: string
  maxLength?: number
  extraInfo?: React.ReactNode
}

export function ExpandableNode({
  label,
  fullContent,
  maxLength = 40,
  extraInfo,
}: ExpandableNodeProps) {
  const [dialogOpen, setDialogOpen] = useState(false)
  const needsTruncation = fullContent.length > maxLength
  const displayLabel = needsTruncation ? label.substring(0, maxLength) + '...' : label

  return (
    <>
      <Tooltip
        title={
          needsTruncation ? (
            <Box sx={{ p: 1, maxWidth: 350 }}>
              <Typography
                variant="body2"
                sx={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word', mb: 1 }}
              >
                {fullContent}
              </Typography>
              <Typography
                variant="caption"
                sx={{ color: colors.accent.light, cursor: 'pointer' }}
              >
                Clique para ver em tela cheia
              </Typography>
            </Box>
          ) : ''
        }
        arrow
        placement="top"
        enterDelay={400}
      >
        <Box
          onClick={() => needsTruncation && setDialogOpen(true)}
          sx={{
            cursor: needsTruncation ? 'pointer' : 'default',
            transition: `all ${motion.duration.fast}ms ${motion.easing.easeInOut}`,
            '&:hover': needsTruncation ? {
              backgroundColor: `${colors.accent.main}08`,
              borderRadius: borders.radius.sm,
            } : {},
          }}
        >
          <Typography variant="caption" sx={{ display: 'block' }}>
            {displayLabel}
          </Typography>
          {extraInfo}
        </Box>
      </Tooltip>

      <Dialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="h6">Detalhes do Nó</Typography>
            <IconButton onClick={() => setDialogOpen(false)} size="small">
              <CloseIcon />
            </IconButton>
          </Box>
        </DialogTitle>
        <DialogContent dividers>
          <Typography
            variant="body1"
            sx={{
              whiteSpace: 'pre-wrap',
              wordBreak: 'break-word',
              lineHeight: 1.8,
            }}
          >
            {fullContent}
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Fechar</Button>
        </DialogActions>
      </Dialog>
    </>
  )
}

export default ExpandableText
