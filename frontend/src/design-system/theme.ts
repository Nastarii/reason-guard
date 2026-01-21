/**
 * MUI Theme - ReasonGuard Design System
 *
 * Tema customizado do Material-UI baseado nos design tokens.
 */

import { createTheme, alpha } from '@mui/material/styles'
import { colors, typography, shadows, borders, motion, spacing } from './tokens'

declare module '@mui/material/styles' {
  interface Palette {
    neutral: typeof colors.neutral
  }
  interface PaletteOptions {
    neutral?: typeof colors.neutral
  }
}

export const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      light: colors.accent.light,
      main: colors.accent.main,
      dark: colors.accent.dark,
      contrastText: colors.accent.contrast,
    },
    secondary: {
      light: colors.neutral[400],
      main: colors.neutral[600],
      dark: colors.neutral[800],
      contrastText: colors.text.inverse,
    },
    success: {
      light: colors.semantic.success.light,
      main: colors.semantic.success.main,
      dark: colors.semantic.success.dark,
    },
    warning: {
      light: colors.semantic.warning.light,
      main: colors.semantic.warning.main,
      dark: colors.semantic.warning.dark,
    },
    error: {
      light: colors.semantic.error.light,
      main: colors.semantic.error.main,
      dark: colors.semantic.error.dark,
    },
    info: {
      light: colors.semantic.info.light,
      main: colors.semantic.info.main,
      dark: colors.semantic.info.dark,
    },
    grey: colors.neutral,
    neutral: colors.neutral,
    background: {
      default: colors.surface.background,
      paper: colors.surface.paper,
    },
    text: {
      primary: colors.text.primary,
      secondary: colors.text.secondary,
      disabled: colors.text.disabled,
    },
    divider: colors.border.light,
  },

  typography: {
    fontFamily: typography.fontFamily.primary,
    fontSize: 14,

    h1: {
      fontSize: typography.fontSize['3xl'],
      fontWeight: typography.fontWeight.bold,
      lineHeight: typography.lineHeight.tight,
      letterSpacing: typography.letterSpacing.tight,
    },
    h2: {
      fontSize: typography.fontSize['2xl'],
      fontWeight: typography.fontWeight.bold,
      lineHeight: typography.lineHeight.tight,
      letterSpacing: typography.letterSpacing.tight,
    },
    h3: {
      fontSize: typography.fontSize.xl,
      fontWeight: typography.fontWeight.semibold,
      lineHeight: typography.lineHeight.tight,
    },
    h4: {
      fontSize: typography.fontSize.lg,
      fontWeight: typography.fontWeight.semibold,
      lineHeight: typography.lineHeight.base,
    },
    h5: {
      fontSize: typography.fontSize.md,
      fontWeight: typography.fontWeight.medium,
      lineHeight: typography.lineHeight.base,
    },
    h6: {
      fontSize: typography.fontSize.base,
      fontWeight: typography.fontWeight.medium,
      lineHeight: typography.lineHeight.base,
    },
    subtitle1: {
      fontSize: typography.fontSize.base,
      fontWeight: typography.fontWeight.medium,
      lineHeight: typography.lineHeight.relaxed,
      color: colors.text.secondary,
    },
    subtitle2: {
      fontSize: typography.fontSize.sm,
      fontWeight: typography.fontWeight.medium,
      lineHeight: typography.lineHeight.relaxed,
      color: colors.text.secondary,
    },
    body1: {
      fontSize: typography.fontSize.base,
      fontWeight: typography.fontWeight.regular,
      lineHeight: typography.lineHeight.relaxed,
    },
    body2: {
      fontSize: typography.fontSize.sm,
      fontWeight: typography.fontWeight.regular,
      lineHeight: typography.lineHeight.relaxed,
    },
    caption: {
      fontSize: typography.fontSize.xs,
      fontWeight: typography.fontWeight.regular,
      lineHeight: typography.lineHeight.base,
      color: colors.text.tertiary,
    },
    overline: {
      fontSize: typography.fontSize.xs,
      fontWeight: typography.fontWeight.semibold,
      lineHeight: typography.lineHeight.base,
      letterSpacing: typography.letterSpacing.wider,
      textTransform: 'uppercase',
    },
    button: {
      fontSize: typography.fontSize.sm,
      fontWeight: typography.fontWeight.medium,
      lineHeight: typography.lineHeight.base,
      textTransform: 'none',
      letterSpacing: typography.letterSpacing.wide,
    },
  },

  shape: {
    borderRadius: parseInt(borders.radius.md) * 16,
  },

  shadows: [
    shadows.none,
    shadows.xs,
    shadows.sm,
    shadows.sm,
    shadows.md,
    shadows.md,
    shadows.md,
    shadows.lg,
    shadows.lg,
    shadows.lg,
    shadows.lg,
    shadows.xl,
    shadows.xl,
    shadows.xl,
    shadows.xl,
    shadows.xl,
    shadows.xl,
    shadows.xl,
    shadows.xl,
    shadows.xl,
    shadows.xl,
    shadows.xl,
    shadows.xl,
    shadows.xl,
    shadows.xl,
  ],

  transitions: {
    duration: {
      shortest: motion.duration.instant,
      shorter: motion.duration.fast,
      short: motion.duration.fast,
      standard: motion.duration.normal,
      complex: motion.duration.slow,
      enteringScreen: motion.duration.normal,
      leavingScreen: motion.duration.fast,
    },
    easing: {
      easeInOut: motion.easing.easeInOut,
      easeOut: motion.easing.easeOut,
      easeIn: motion.easing.easeIn,
      sharp: motion.easing.easeInOut,
    },
  },

  components: {
    MuiCssBaseline: {
      styleOverrides: {
        '*': {
          boxSizing: 'border-box',
        },
        html: {
          scrollBehavior: 'smooth',
        },
        body: {
          backgroundColor: colors.surface.background,
          color: colors.text.primary,
          WebkitFontSmoothing: 'antialiased',
          MozOsxFontSmoothing: 'grayscale',
        },
        '::selection': {
          backgroundColor: alpha(colors.accent.main, 0.2),
        },
      },
    },

    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: borders.radius.md,
          padding: `${spacing[2]} ${spacing[4]}`,
          transition: motion.transition.fast,
          boxShadow: 'none',
          '&:hover': {
            boxShadow: shadows.sm,
            transform: 'translateY(-1px)',
          },
          '&:active': {
            transform: 'translateY(0)',
          },
        },
        contained: {
          '&:hover': {
            boxShadow: shadows.md,
          },
        },
        outlined: {
          borderColor: colors.border.main,
          '&:hover': {
            borderColor: colors.accent.main,
            backgroundColor: alpha(colors.accent.main, 0.04),
          },
        },
        text: {
          '&:hover': {
            backgroundColor: alpha(colors.accent.main, 0.04),
          },
        },
      },
    },

    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: borders.radius.lg,
          boxShadow: shadows.sm,
          border: `1px solid ${colors.border.light}`,
          transition: motion.transition.normal,
          '&:hover': {
            boxShadow: shadows.md,
          },
        },
      },
    },

    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: borders.radius.lg,
          boxShadow: shadows.sm,
        },
        outlined: {
          border: `1px solid ${colors.border.light}`,
          boxShadow: 'none',
        },
      },
    },

    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: borders.radius.md,
          fontWeight: typography.fontWeight.medium,
          transition: motion.transition.fast,
        },
        outlined: {
          borderColor: colors.border.main,
        },
      },
    },

    MuiIconButton: {
      styleOverrides: {
        root: {
          borderRadius: borders.radius.md,
          transition: motion.transition.fast,
          '&:hover': {
            backgroundColor: alpha(colors.neutral[900], 0.04),
          },
        },
      },
    },

    MuiTableCell: {
      styleOverrides: {
        root: {
          borderColor: colors.border.light,
          padding: spacing[4],
        },
        head: {
          fontWeight: typography.fontWeight.semibold,
          backgroundColor: colors.neutral[50],
          color: colors.text.secondary,
        },
      },
    },

    MuiTableRow: {
      styleOverrides: {
        root: {
          transition: motion.transition.fast,
          '&:hover': {
            backgroundColor: alpha(colors.accent.main, 0.02),
          },
        },
      },
    },

    MuiDialog: {
      styleOverrides: {
        paper: {
          borderRadius: borders.radius.xl,
          boxShadow: shadows.xl,
        },
      },
    },

    MuiTooltip: {
      styleOverrides: {
        tooltip: {
          backgroundColor: colors.neutral[900],
          color: colors.text.inverse,
          fontSize: typography.fontSize.sm,
          fontWeight: typography.fontWeight.medium,
          borderRadius: borders.radius.md,
          padding: `${spacing[2]} ${spacing[3]}`,
          boxShadow: shadows.lg,
        },
        arrow: {
          color: colors.neutral[900],
        },
      },
    },

    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: borders.radius.md,
            transition: motion.transition.fast,
            '& fieldset': {
              borderColor: colors.border.main,
              transition: motion.transition.fast,
            },
            '&:hover fieldset': {
              borderColor: colors.neutral[400],
            },
            '&.Mui-focused fieldset': {
              borderColor: colors.accent.main,
              borderWidth: '2px',
            },
          },
        },
      },
    },

    MuiDrawer: {
      styleOverrides: {
        paper: {
          borderRight: `1px solid ${colors.border.light}`,
          backgroundColor: colors.surface.paper,
        },
      },
    },

    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: colors.surface.paper,
          color: colors.text.primary,
          boxShadow: shadows.xs,
          borderBottom: `1px solid ${colors.border.light}`,
        },
      },
    },

    MuiListItemButton: {
      styleOverrides: {
        root: {
          borderRadius: borders.radius.md,
          margin: `${spacing[1]} ${spacing[2]}`,
          transition: motion.transition.fast,
          '&:hover': {
            backgroundColor: alpha(colors.neutral[900], 0.04),
          },
          '&.Mui-selected': {
            backgroundColor: alpha(colors.accent.main, 0.08),
            color: colors.accent.dark,
            '& .MuiListItemIcon-root': {
              color: colors.accent.main,
            },
            '&:hover': {
              backgroundColor: alpha(colors.accent.main, 0.12),
            },
          },
        },
      },
    },

    MuiLinearProgress: {
      styleOverrides: {
        root: {
          borderRadius: borders.radius.full,
          backgroundColor: colors.neutral[200],
        },
        bar: {
          borderRadius: borders.radius.full,
        },
      },
    },

    MuiCircularProgress: {
      styleOverrides: {
        root: {
          color: colors.accent.main,
        },
      },
    },

    MuiSkeleton: {
      styleOverrides: {
        root: {
          backgroundColor: colors.neutral[200],
        },
        wave: {
          '&::after': {
            background: `linear-gradient(90deg, transparent, ${alpha(colors.surface.paper, 0.4)}, transparent)`,
          },
        },
      },
    },

    MuiAlert: {
      styleOverrides: {
        root: {
          borderRadius: borders.radius.md,
        },
        standardSuccess: {
          backgroundColor: colors.semantic.success.light,
          color: colors.semantic.success.dark,
        },
        standardWarning: {
          backgroundColor: colors.semantic.warning.light,
          color: colors.semantic.warning.dark,
        },
        standardError: {
          backgroundColor: colors.semantic.error.light,
          color: colors.semantic.error.dark,
        },
        standardInfo: {
          backgroundColor: colors.semantic.info.light,
          color: colors.semantic.info.dark,
        },
      },
    },
  },
})

export default theme
