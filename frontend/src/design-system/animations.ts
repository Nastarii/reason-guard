/**
 * Animações - ReasonGuard Design System
 *
 * Variantes de animação para Framer Motion e CSS.
 * Foco em transições suaves e naturais que melhoram a percepção de velocidade.
 */

import { motion } from './tokens'

// =============================================================================
// VARIANTES FRAMER MOTION
// =============================================================================

/**
 * Fade In - Entrada suave com opacidade
 */
export const fadeIn = {
  initial: { opacity: 0 },
  animate: { opacity: 1 },
  exit: { opacity: 0 },
  transition: {
    duration: motion.duration.normal / 1000,
    ease: [0.4, 0, 0.2, 1],
  },
}

/**
 * Fade In Up - Entrada com slide de baixo para cima
 */
export const fadeInUp = {
  initial: { opacity: 0, y: 16 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: 8 },
  transition: {
    duration: motion.duration.normal / 1000,
    ease: [0.4, 0, 0.2, 1],
  },
}

/**
 * Fade In Down - Entrada com slide de cima para baixo
 */
export const fadeInDown = {
  initial: { opacity: 0, y: -16 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -8 },
  transition: {
    duration: motion.duration.normal / 1000,
    ease: [0.4, 0, 0.2, 1],
  },
}

/**
 * Fade In Left - Entrada com slide da esquerda
 */
export const fadeInLeft = {
  initial: { opacity: 0, x: -24 },
  animate: { opacity: 1, x: 0 },
  exit: { opacity: 0, x: -12 },
  transition: {
    duration: motion.duration.normal / 1000,
    ease: [0.4, 0, 0.2, 1],
  },
}

/**
 * Fade In Right - Entrada com slide da direita
 */
export const fadeInRight = {
  initial: { opacity: 0, x: 24 },
  animate: { opacity: 1, x: 0 },
  exit: { opacity: 0, x: 12 },
  transition: {
    duration: motion.duration.normal / 1000,
    ease: [0.4, 0, 0.2, 1],
  },
}

/**
 * Scale In - Entrada com escala
 */
export const scaleIn = {
  initial: { opacity: 0, scale: 0.95 },
  animate: { opacity: 1, scale: 1 },
  exit: { opacity: 0, scale: 0.98 },
  transition: {
    duration: motion.duration.normal / 1000,
    ease: [0.4, 0, 0.2, 1],
  },
}

/**
 * Scale In Spring - Entrada com escala e efeito spring
 */
export const scaleInSpring = {
  initial: { opacity: 0, scale: 0.9 },
  animate: { opacity: 1, scale: 1 },
  exit: { opacity: 0, scale: 0.95 },
  transition: {
    type: 'spring',
    stiffness: 300,
    damping: 25,
  },
}

/**
 * Slide In Bottom - Entrada de baixo (para modais)
 */
export const slideInBottom = {
  initial: { opacity: 0, y: '10%' },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: '5%' },
  transition: {
    duration: motion.duration.slow / 1000,
    ease: [0.4, 0, 0.2, 1],
  },
}

/**
 * Collapse - Expandir/Colapsar vertical
 */
export const collapse = {
  initial: { height: 0, opacity: 0 },
  animate: { height: 'auto', opacity: 1 },
  exit: { height: 0, opacity: 0 },
  transition: {
    duration: motion.duration.normal / 1000,
    ease: [0.4, 0, 0.2, 1],
  },
}

// =============================================================================
// STAGGER CHILDREN - Para listas e grids
// =============================================================================

export const staggerContainer = {
  initial: {},
  animate: {
    transition: {
      staggerChildren: 0.05,
      delayChildren: 0.1,
    },
  },
  exit: {
    transition: {
      staggerChildren: 0.03,
      staggerDirection: -1,
    },
  },
}

export const staggerItem = {
  initial: { opacity: 0, y: 12 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: 6 },
  transition: {
    duration: motion.duration.normal / 1000,
    ease: [0.4, 0, 0.2, 1],
  },
}

// =============================================================================
// TRANSIÇÕES DE PÁGINA
// =============================================================================

export const pageTransition = {
  initial: { opacity: 0, y: 8 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -4 },
  transition: {
    duration: motion.duration.normal / 1000,
    ease: [0.4, 0, 0.2, 1],
  },
}

export const pageSlideTransition = {
  initial: { opacity: 0, x: 20 },
  animate: { opacity: 1, x: 0 },
  exit: { opacity: 0, x: -10 },
  transition: {
    duration: motion.duration.normal / 1000,
    ease: [0.4, 0, 0.2, 1],
  },
}

// =============================================================================
// MICRO-INTERAÇÕES
// =============================================================================

export const hoverScale = {
  whileHover: { scale: 1.02 },
  whileTap: { scale: 0.98 },
  transition: {
    duration: motion.duration.fast / 1000,
    ease: [0.4, 0, 0.2, 1],
  },
}

export const hoverLift = {
  whileHover: { y: -2 },
  whileTap: { y: 0 },
  transition: {
    duration: motion.duration.fast / 1000,
    ease: [0.4, 0, 0.2, 1],
  },
}

export const pressScale = {
  whileTap: { scale: 0.97 },
  transition: {
    duration: motion.duration.instant / 1000,
  },
}

// =============================================================================
// SKELETON / LOADING
// =============================================================================

export const shimmer = {
  initial: { x: '-100%' },
  animate: {
    x: '100%',
    transition: {
      repeat: Infinity,
      duration: 1.5,
      ease: 'linear',
    },
  },
}

export const pulse = {
  animate: {
    opacity: [1, 0.5, 1],
    transition: {
      repeat: Infinity,
      duration: 1.5,
      ease: 'easeInOut',
    },
  },
}

// =============================================================================
// CSS KEYFRAMES (para uso sem Framer Motion)
// =============================================================================

export const cssKeyframes = `
  @keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
  }

  @keyframes fadeInUp {
    from {
      opacity: 0;
      transform: translateY(16px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  @keyframes fadeInDown {
    from {
      opacity: 0;
      transform: translateY(-16px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  @keyframes scaleIn {
    from {
      opacity: 0;
      transform: scale(0.95);
    }
    to {
      opacity: 1;
      transform: scale(1);
    }
  }

  @keyframes shimmer {
    0% { transform: translateX(-100%); }
    100% { transform: translateX(100%); }
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
  }

  @keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
  }

  @keyframes slideInRight {
    from {
      opacity: 0;
      transform: translateX(24px);
    }
    to {
      opacity: 1;
      transform: translateX(0);
    }
  }
`

// =============================================================================
// CLASSES CSS DE ANIMAÇÃO
// =============================================================================

export const cssAnimationClasses = {
  fadeIn: `animation: fadeIn ${motion.duration.normal}ms ${motion.easing.easeOut} forwards`,
  fadeInUp: `animation: fadeInUp ${motion.duration.normal}ms ${motion.easing.easeOut} forwards`,
  fadeInDown: `animation: fadeInDown ${motion.duration.normal}ms ${motion.easing.easeOut} forwards`,
  scaleIn: `animation: scaleIn ${motion.duration.normal}ms ${motion.easing.easeOut} forwards`,
  shimmer: `animation: shimmer 1.5s infinite linear`,
  pulse: `animation: pulse 1.5s infinite ease-in-out`,
  spin: `animation: spin 1s infinite linear`,
  slideInRight: `animation: slideInRight ${motion.duration.normal}ms ${motion.easing.easeOut} forwards`,
}

// =============================================================================
// ESTILOS DE TRANSIÇÃO CSS
// =============================================================================

export const cssTransitions = {
  fast: `all ${motion.duration.fast}ms ${motion.easing.easeInOut}`,
  normal: `all ${motion.duration.normal}ms ${motion.easing.easeInOut}`,
  slow: `all ${motion.duration.slow}ms ${motion.easing.easeInOut}`,
  transform: `transform ${motion.duration.fast}ms ${motion.easing.easeOut}`,
  opacity: `opacity ${motion.duration.normal}ms ${motion.easing.easeInOut}`,
  colors: `color ${motion.duration.fast}ms, background-color ${motion.duration.fast}ms, border-color ${motion.duration.fast}ms`,
}
