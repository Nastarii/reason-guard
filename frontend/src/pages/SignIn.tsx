import { SignIn as ClerkSignIn } from '@clerk/clerk-react'
import { Box, Container, Typography, Paper } from '@mui/material'

export default function SignIn() {
  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: 'background.default',
      }}
    >
      <Container maxWidth="sm">
        <Paper elevation={3} sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 'bold', color: 'primary.main' }}>
            ReasonGuard
          </Typography>
          <Typography variant="subtitle1" color="text.secondary" sx={{ mb: 3 }}>
            Plataforma de Auditoria de Raciocínio de IA
          </Typography>
          <Box sx={{ display: 'flex', justifyContent: 'center' }}>
            <ClerkSignIn
              routing="path"
              path="/sign-in"
              signUpUrl="/sign-up"
              redirectUrl="/dashboard"
            />
          </Box>
        </Paper>
      </Container>
    </Box>
  )
}
