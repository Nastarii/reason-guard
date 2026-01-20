import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { SignedIn, SignedOut, RedirectToSignIn } from '@clerk/clerk-react'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import ReasoningTraces from './pages/ReasoningTraces'
import PathAnalysis from './pages/PathAnalysis'
import LogicValidation from './pages/LogicValidation'
import ConsistencyChecks from './pages/ConsistencyChecks'
import AuditReports from './pages/AuditReports'
import Chat from './pages/Chat'
import Settings from './pages/Settings'
import SignIn from './pages/SignIn'
import SignUp from './pages/SignUp'

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  return (
    <>
      <SignedIn>{children}</SignedIn>
      <SignedOut>
        <RedirectToSignIn />
      </SignedOut>
    </>
  )
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/sign-in" element={<SignIn />} />
        <Route path="/sign-up" element={<SignUp />} />
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }
        >
          <Route index element={<Navigate to="/dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="chat" element={<Chat />} />
          <Route path="reasoning" element={<ReasoningTraces />} />
          <Route path="path-analysis" element={<PathAnalysis />} />
          <Route path="logic" element={<LogicValidation />} />
          <Route path="consistency" element={<ConsistencyChecks />} />
          <Route path="audit" element={<AuditReports />} />
          <Route path="settings" element={<Settings />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
