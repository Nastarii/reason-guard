/**
 * Design Tokens - ReasonGuard Design System
 *
 * Baseado em Minimalismo Moderno com foco em clareza, hierarquia e performance.
 * Escala tipográfica geométrica (razão 1.25) e paleta monocromática com cor de destaque.
 */

// =============================================================================
// CORES
// =============================================================================

export const colors = {
  // Paleta Primária (Monocromática)
  neutral: {
    50: '#FAFAFA',
    100: '#F5F5F5',
    200: '#EEEEEE',
    300: '#E0E0E0',
    400: '#BDBDBD',
    500: '#9E9E9E',
    600: '#757575',
    700: '#616161',
    800: '#424242',
    900: '#212121',
    950: '#0A0A0A',
  },

  // Cor de Destaque (CTA único)
  accent: {
    light: '#818CF8',
    main: '#6366F1',
    dark: '#4F46E5',
    contrast: '#FFFFFF',
  },

  // Estados Semânticos
  semantic: {
    success: {
      light: '#D1FAE5',
      main: '#10B981',
      dark: '#059669',
    },
    warning: {
      light: '#FEF3C7',
      main: '#F59E0B',
      dark: '#D97706',
    },
    error: {
      light: '#FEE2E2',
      main: '#EF4444',
      dark: '#DC2626',
    },
    info: {
      light: '#DBEAFE',
      main: '#3B82F6',
      dark: '#2563EB',
    },
  },

  // Superfícies
  surface: {
    background: '#FAFAFA',
    paper: '#FFFFFF',
    elevated: '#FFFFFF',
    overlay: 'rgba(0, 0, 0, 0.5)',
  },

  // Texto
  text: {
    primary: '#212121',
    secondary: '#616161',
    tertiary: '#9E9E9E',
    disabled: '#BDBDBD',
    inverse: '#FFFFFF',
  },

  // Bordas
  border: {
    light: '#F5F5F5',
    main: '#E0E0E0',
    dark: '#BDBDBD',
  },
} as const

// =============================================================================
// TIPOGRAFIA
// =============================================================================

// Escala tipográfica geométrica (razão 1.25 - Major Third)
export const typography = {
  fontFamily: {
    primary: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    mono: '"JetBrains Mono", "Fira Code", Consolas, monospace',
  },

  // Escala de tamanhos (base 16px, razão 1.25)
  fontSize: {
    xs: '0.64rem',     // 10.24px
    sm: '0.8rem',      // 12.8px
    base: '1rem',      // 16px
    md: '1.25rem',     // 20px
    lg: '1.563rem',    // 25px
    xl: '1.953rem',    // 31.25px
    '2xl': '2.441rem', // 39px
    '3xl': '3.052rem', // 48.8px
  },

  fontWeight: {
    regular: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
  },

  lineHeight: {
    tight: 1.25,
    base: 1.5,
    relaxed: 1.75,
  },

  letterSpacing: {
    tight: '-0.025em',
    normal: '0',
    wide: '0.025em',
    wider: '0.05em',
  },
} as const

// =============================================================================
// ESPAÇAMENTO
// =============================================================================

// Escala de 4px (0.25rem)
export const spacing = {
  0: '0',
  1: '0.25rem',   // 4px
  2: '0.5rem',    // 8px
  3: '0.75rem',   // 12px
  4: '1rem',      // 16px
  5: '1.25rem',   // 20px
  6: '1.5rem',    // 24px
  8: '2rem',      // 32px
  10: '2.5rem',   // 40px
  12: '3rem',     // 48px
  16: '4rem',     // 64px
  20: '5rem',     // 80px
  24: '6rem',     // 96px
} as const

// =============================================================================
// SOMBRAS
// =============================================================================

// Sombras de baixa opacidade para elegância minimalista
export const shadows = {
  none: 'none',
  xs: '0 1px 2px rgba(0, 0, 0, 0.04)',
  sm: '0 2px 4px rgba(0, 0, 0, 0.04), 0 1px 2px rgba(0, 0, 0, 0.02)',
  md: '0 4px 8px rgba(0, 0, 0, 0.04), 0 2px 4px rgba(0, 0, 0, 0.02)',
  lg: '0 8px 16px rgba(0, 0, 0, 0.04), 0 4px 8px rgba(0, 0, 0, 0.02)',
  xl: '0 16px 32px rgba(0, 0, 0, 0.06), 0 8px 16px rgba(0, 0, 0, 0.02)',
  inner: 'inset 0 2px 4px rgba(0, 0, 0, 0.04)',
} as const

// =============================================================================
// BORDAS
// =============================================================================

export const borders = {
  radius: {
    none: '0',
    sm: '0.25rem',   // 4px
    md: '0.5rem',    // 8px
    lg: '0.75rem',   // 12px
    xl: '1rem',      // 16px
    '2xl': '1.5rem', // 24px
    full: '9999px',
  },

  width: {
    none: '0',
    thin: '1px',
    medium: '2px',
    thick: '4px',
  },
} as const

// =============================================================================
// ANIMAÇÕES / MOTION
// =============================================================================

export const motion = {
  // Durações (em ms)
  duration: {
    instant: 50,
    fast: 150,
    normal: 250,
    slow: 400,
    slower: 600,
  },

  // Curvas de easing (cubic-bezier)
  easing: {
    // Ease-out suave - para entradas
    easeOut: 'cubic-bezier(0.0, 0, 0.2, 1)',
    // Ease-in suave - para saídas
    easeIn: 'cubic-bezier(0.4, 0, 1, 1)',
    // Ease-in-out - para transições contínuas
    easeInOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
    // Spring natural
    spring: 'cubic-bezier(0.175, 0.885, 0.32, 1.275)',
    // Linear
    linear: 'linear',
  },

  // Transições predefinidas
  transition: {
    fast: '150ms cubic-bezier(0.4, 0, 0.2, 1)',
    normal: '250ms cubic-bezier(0.4, 0, 0.2, 1)',
    slow: '400ms cubic-bezier(0.4, 0, 0.2, 1)',
    spring: '400ms cubic-bezier(0.175, 0.885, 0.32, 1.275)',
  },
} as const

// =============================================================================
// BREAKPOINTS
// =============================================================================

export const breakpoints = {
  xs: 0,
  sm: 640,
  md: 768,
  lg: 1024,
  xl: 1280,
  '2xl': 1536,
} as const

// =============================================================================
// Z-INDEX
// =============================================================================

export const zIndex = {
  base: 0,
  dropdown: 100,
  sticky: 200,
  modal: 300,
  popover: 400,
  tooltip: 500,
  toast: 600,
} as const

// =============================================================================
// EXPORT COMPLETO
// =============================================================================

export const designTokens = {
  colors,
  typography,
  spacing,
  shadows,
  borders,
  motion,
  breakpoints,
  zIndex,
} as const

export type DesignTokens = typeof designTokens
