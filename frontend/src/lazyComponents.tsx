import { lazy } from 'react';

// Lazy load main pages
export const Login = lazy(() => import('./pages/Login').then(module => ({ default: module.Login })));
export const Studies = lazy(() => import('./pages/Studies').then(module => ({ default: module.Studies })));
export const StudyDetail = lazy(() => import('./pages/StudyDetail').then(module => ({ default: module.StudyDetail })));
export const StudyDashboard = lazy(() => import('./pages/StudyDashboard').then(module => ({ default: module.StudyDashboard })));

// Lazy load large components
export const HAZOPAnalysis = lazy(() => import('./components/HAZOPAnalysis'));
export const PIDViewer = lazy(() => import('./components/PIDViewer'));
export const GeminiInsightsPanel = lazy(() => import('./components/GeminiInsightsPanel'));
export const ImpactAssessmentForm = lazy(() => import('./components/ImpactAssessmentForm'));
export const ContextualKnowledgePanel = lazy(() => import('./components/ContextualKnowledgePanel'));
export const RiskMatrixViewer = lazy(() => import('./components/RiskMatrixViewer'));

// Lazy load dashboard components
export const DeviationsByNodeChart = lazy(() => import('./components/dashboard/DeviationsByNodeChart'));
export const RiskDistributionChart = lazy(() => import('./components/dashboard/RiskDistributionChart'));