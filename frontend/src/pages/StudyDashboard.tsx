import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { DashboardMetricCard } from '../components/dashboard/DashboardMetricCard';
import { RiskDistributionChart } from '../components/dashboard/RiskDistributionChart';
import { DeviationsByNodeChart } from '../components/dashboard/DeviationsByNodeChart';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface DashboardData {
  study: {
    id: string;
    title: string;
    facility_name: string;
  };
  metrics: {
    total_nodes: number;
    total_deviations: number;
    total_causes: number;
    total_consequences: number;
    total_safeguards: number;
    total_recommendations: number;
    risk_distribution: {
      critical: number;
      high: number;
      medium: number;
      low: number;
    };
    deviations_by_node: Array<{
      node_id: string;
      node_name: string;
      count: number;
    }>;
    completion_percentage: number;
  };
}

export const StudyDashboard = () => {
  const { studyId } = useParams();
  const navigate = useNavigate();
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDashboardData();
  }, [studyId]);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_URL}/api/studies/${studyId}/dashboard`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setDashboardData(response.data);
      setError(null);
    } catch (err: any) {
      console.error('Failed to load dashboard data:', err);
      setError(err.response?.data?.detail || 'Failed to load dashboard');
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `${API_URL}/api/studies/${studyId}/export/excel`,
        {
          headers: { Authorization: `Bearer ${token}` },
          responseType: 'blob'
        }
      );

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      const filename = `${dashboardData?.study.title.replace(/[^a-z0-9]/gi, '_')}_HAZOP_${new Date().toISOString().split('T')[0]}.xlsx`;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error('Failed to export:', err);
      alert('Failed to export to Excel');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (error || !dashboardData) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 text-xl">❌ {error || 'Failed to load dashboard'}</p>
          <button
            onClick={() => navigate('/studies')}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Back to Studies
          </button>
        </div>
      </div>
    );
  }

  const totalRisks =
    dashboardData.metrics.risk_distribution.critical +
    dashboardData.metrics.risk_distribution.high +
    dashboardData.metrics.risk_distribution.medium +
    dashboardData.metrics.risk_distribution.low;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex justify-between items-start">
            <div>
              <button
                onClick={() => navigate('/studies')}
                className="text-sm text-blue-600 hover:text-blue-800 mb-2"
              >
                ← Back to Studies
              </button>
              <h1 className="text-3xl font-bold text-gray-900">{dashboardData.study.title}</h1>
              {dashboardData.study.facility_name && (
                <p className="text-lg text-gray-600 mt-1">📍 {dashboardData.study.facility_name}</p>
              )}
            </div>
            <div className="flex gap-3">
              <button
                onClick={handleExport}
                className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
              >
                <span>📥</span>
                <span>Export to Excel</span>
              </button>
              <button
                onClick={() => navigate(`/studies/${studyId}`)}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                <span>📝</span>
                <span>HAZOP Analysis</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <DashboardMetricCard
            title="Total Nodes"
            value={dashboardData.metrics.total_nodes}
            icon="🏭"
            color="blue"
            onClick={() => navigate(`/studies/${studyId}`)}
          />
          <DashboardMetricCard
            title="Total Deviations"
            value={dashboardData.metrics.total_deviations}
            icon="⚠️"
            color="purple"
            onClick={() => navigate(`/studies/${studyId}`)}
          />
          <DashboardMetricCard
            title="Total Causes"
            value={dashboardData.metrics.total_causes}
            icon="🔍"
            color="yellow"
          />
          <DashboardMetricCard
            title="Risk Assessments"
            value={totalRisks}
            icon={
              dashboardData.metrics.risk_distribution.critical > 0 ? '🔴' :
              dashboardData.metrics.risk_distribution.high > 0 ? '🟠' :
              dashboardData.metrics.risk_distribution.medium > 0 ? '🟡' : '🟢'
            }
            color={
              dashboardData.metrics.risk_distribution.critical > 0 ? 'red' :
              dashboardData.metrics.risk_distribution.high > 0 ? 'yellow' :
              dashboardData.metrics.risk_distribution.medium > 0 ? 'yellow' : 'green'
            }
          />
        </div>

        {/* Charts Row 1 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Risk Distribution Chart */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Risk Distribution</h2>
            <div style={{ height: '300px' }}>
              <RiskDistributionChart
                data={dashboardData.metrics.risk_distribution}
              />
            </div>
          </div>

          {/* Deviations by Node Chart */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Deviations by Node</h2>
            <div style={{ height: '300px' }}>
              <DeviationsByNodeChart
                data={dashboardData.metrics.deviations_by_node}
                onNodeClick={(nodeId: string) => navigate(`/studies/${studyId}?node=${nodeId}`)}
              />
            </div>
          </div>
        </div>

        {/* Additional Metrics Row */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Consequences</p>
                <p className="text-2xl font-bold text-gray-900 mt-2">
                  {dashboardData.metrics.total_consequences}
                </p>
              </div>
              <div className="text-4xl">💥</div>
            </div>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Safeguards</p>
                <p className="text-2xl font-bold text-gray-900 mt-2">
                  {dashboardData.metrics.total_safeguards}
                </p>
              </div>
              <div className="text-4xl">🛡️</div>
            </div>
          </div>
          <div className="bg-white rounded-lg shadow-md p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Recommendations</p>
                <p className="text-2xl font-bold text-gray-900 mt-2">
                  {dashboardData.metrics.total_recommendations}
                </p>
              </div>
              <div className="text-4xl">💡</div>
            </div>
          </div>
        </div>

        {/* Nodes Quick Access */}
        {dashboardData.metrics.deviations_by_node.length > 0 && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Access to Nodes</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
              {dashboardData.metrics.deviations_by_node.map((node) => (
                <button
                  key={node.node_id}
                  onClick={() => navigate(`/studies/${studyId}?node=${node.node_id}`)}
                  className="bg-blue-50 hover:bg-blue-100 border-2 border-blue-200 rounded-lg p-4 transition-all hover:shadow-md"
                >
                  <p className="font-semibold text-gray-900 text-sm truncate">{node.node_name}</p>
                  <p className="text-xs text-gray-600 mt-1">{node.count} deviations</p>
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
