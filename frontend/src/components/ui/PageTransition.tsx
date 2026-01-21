/**
 * Page Transition Component - ReasonGuard Design System
 *
 * Wrapper para transições suaves entre páginas.
 * Mantém continuidade visual para experiência fluida.
 */

import { ReactNode } from 'react'
import { Box, styled, keyframes } from '@mui/material'
import { motion } from '../../design-system/tokens'

// =============================================================================
// KEYFRAMES
// =============================================================================

const fadeInUp = keyframes`
  from {
    opacity: 0;
    transform: translateY(12px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
`

const fadeIn = keyframes`
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
`

// =============================================================================
// STYLED COMPONENTS
// =============================================================================

const AnimatedContainer = styled(Box)<{ animation?: 'fadeInUp' | 'fadeIn' }>(
  ({ animation = 'fadeInUp' }) => ({
    animation: `${animation === 'fadeInUp' ? fadeInUp : fadeIn} ${motion.duration.normal}ms ${motion.easing.easeOut} forwards`,
    opacity: 0,
  })
)

// =============================================================================
// PAGE TRANSITION COMPONENT
// =============================================================================

interface PageTransitionProps {
  children: ReactNode
  animation?: 'fadeInUp' | 'fadeIn'
}

export function PageTransition({ children, animation = 'fadeInUp' }: PageTransitionProps) {
  return (
    <AnimatedContainer animation={animation}>
      {children}
    </AnimatedContainer>
  )
}

// =============================================================================
// STAGGERED LIST COMPONENT
// =============================================================================

interface StaggeredListProps {
  children: ReactNode[]
  delay?: number
  baseDelay?: number
}

const StaggeredItem = styled(Box)<{ delay: number }>(({ delay }) => ({
  animation: `${fadeInUp} ${motion.duration.normal}ms ${motion.easing.easeOut} forwards`,
  animationDelay: `${delay}ms`,
  opacity: 0,
}))

export function StaggeredList({
  children,
  delay = 50,
  baseDelay = 100
}: StaggeredListProps) {
  return (
    <>
      {children.map((child, index) => (
        <StaggeredItem key={index} delay={baseDelay + index * delay}>
          {child}
        </StaggeredItem>
      ))}
    </>
  )
}

// =============================================================================
// FADE IN COMPONENT
// =============================================================================

interface FadeInProps {
  children: ReactNode
  delay?: number
  duration?: number
}

const FadeInContainer = styled(Box)<{ delay: number; duration: number }>(
  ({ delay, duration }) => ({
    animation: `${fadeIn} ${duration}ms ${motion.easing.easeOut} forwards`,
    animationDelay: `${delay}ms`,
    opacity: 0,
  })
)

export function FadeIn({
  children,
  delay = 0,
  duration = motion.duration.normal
}: FadeInProps) {
  return (
    <FadeInContainer delay={delay} duration={duration}>
      {children}
    </FadeInContainer>
  )
}

// =============================================================================
// SLIDE IN COMPONENT
// =============================================================================

type SlideDirection = 'up' | 'down' | 'left' | 'right'

const slideUp = keyframes`
  from {
    opacity: 0;
    transform: translateY(24px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
`

const slideDown = keyframes`
  from {
    opacity: 0;
    transform: translateY(-24px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
`

const slideLeft = keyframes`
  from {
    opacity: 0;
    transform: translateX(24px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
`

const slideRight = keyframes`
  from {
    opacity: 0;
    transform: translateX(-24px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
`

const getSlideKeyframes = (direction: SlideDirection) => {
  switch (direction) {
    case 'up': return slideUp
    case 'down': return slideDown
    case 'left': return slideLeft
    case 'right': return slideRight
  }
}

interface SlideInProps {
  children: ReactNode
  direction?: SlideDirection
  delay?: number
  duration?: number
}

export function SlideIn({
  children,
  direction = 'up',
  delay = 0,
  duration = motion.duration.normal
}: SlideInProps) {
  const SlideContainer = styled(Box)({
    animation: `${getSlideKeyframes(direction)} ${duration}ms ${motion.easing.easeOut} forwards`,
    animationDelay: `${delay}ms`,
    opacity: 0,
  })

  return (
    <SlideContainer>
      {children}
    </SlideContainer>
  )
}

// =============================================================================
// SCALE IN COMPONENT
// =============================================================================

const scaleIn = keyframes`
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
`

interface ScaleInProps {
  children: ReactNode
  delay?: number
  duration?: number
}

export function ScaleIn({
  children,
  delay = 0,
  duration = motion.duration.normal
}: ScaleInProps) {
  const ScaleContainer = styled(Box)({
    animation: `${scaleIn} ${duration}ms ${motion.easing.easeOut} forwards`,
    animationDelay: `${delay}ms`,
    opacity: 0,
  })

  return (
    <ScaleContainer>
      {children}
    </ScaleContainer>
  )
}

// =============================================================================
// HOVER ANIMATION WRAPPER
// =============================================================================

interface HoverAnimationProps {
  children: ReactNode
  scale?: number
  lift?: number
}

const HoverContainer = styled(Box)<{ hoverScale: number; lift: number }>(
  ({ hoverScale, lift }) => ({
    transition: `transform ${motion.duration.fast}ms ${motion.easing.easeOut}`,
    '&:hover': {
      transform: `translateY(-${lift}px) scale(${hoverScale})`,
    },
    '&:active': {
      transform: 'translateY(0) scale(0.98)',
    },
  })
)

export function HoverAnimation({
  children,
  scale = 1.02,
  lift = 2
}: HoverAnimationProps) {
  return (
    <HoverContainer hoverScale={scale} lift={lift}>
      {children}
    </HoverContainer>
  )
}

export default PageTransition
