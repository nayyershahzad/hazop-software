import { useState, useEffect } from 'react';
import axios from 'axios';
import type { Deviation, Cause, Consequence, Safeguard, Recommendation, ImpactAssessment } from '../types';
import { ImpactAssessmentForm } from './ImpactAssessmentForm';
import { RiskBadge } from './RiskBadge';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface HAZOPAnalysisProps {
  deviation: Deviation;
}

export const HAZOPAnalysis = ({ deviation }: HAZOPAnalysisProps) => {
  const [causes, setCauses] = useState<Cause[]>([]);
  const [consequences, setConsequences] = useState<Consequence[]>([]);
  const [safeguards, setSafeguards] = useState<Safeguard[]>([]);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);

  // State for mapping consequences to causes, and safeguards/recommendations to consequences
  const [consequencesByCause, setConsequencesByCause] = useState<Record<string, Consequence[]>>({});
  const [safeguardsByConsequence, setSafeguardsByConsequence] = useState<Record<string, Safeguard[]>>({});
  const [recommendationsByConsequence, setRecommendationsByConsequence] = useState<Record<string, Recommendation[]>>({});
  const [impactAssessmentsByConsequence, setImpactAssessmentsByConsequence] = useState<Record<string, ImpactAssessment>>({});

  // State for currently selected items
  const [selectedCauseId, setSelectedCauseId] = useState<string | null>(null);
  const [selectedConsequenceId, setSelectedConsequenceId] = useState<string | null>(null);

  const [showCauseModal, setShowCauseModal] = useState(false);
  const [showConsequenceModal, setShowConsequenceModal] = useState(false);
  const [showSafeguardModal, setShowSafeguardModal] = useState(false);
  const [showRecommendationModal, setShowRecommendationModal] = useState(false);
  const [showCopyModal, setShowCopyModal] = useState(false);
  const [similarDeviations, setSimilarDeviations] = useState<any[]>([]);
  const [showRiskAssessment, setShowRiskAssessment] = useState(false);
  const [currentRiskLevel, setCurrentRiskLevel] = useState<'Low' | 'Medium' | 'High' | 'Critical' | null>(null);

  useEffect(() => {
    // Trigger a reload of data when deviation ID changes
    loadAll();
    loadCurrentRisk();
  }, [deviation.id]);

  const loadAll = async () => {
    await loadCauses();
    await loadConsequences();
    await loadSafeguards();
    await loadRecommendations();
    await loadHierarchicalData();
  };

  // Load hierarchical data structures for better rendering
  const loadHierarchicalData = async () => {
    try {
      const token = localStorage.getItem('token');
      const newConsequencesByCause: Record<string, Consequence[]> = {};
      const newSafeguardsByConsequence: Record<string, Safeguard[]> = {};
      const newRecommendationsByConsequence: Record<string, Recommendation[]> = {};
      const newImpactAssessments: Record<string, ImpactAssessment> = {};

      // For each cause, load its consequences
      for (const cause of causes) {
        try {
          const response = await axios.get(`${API_URL}/api/hazop/causes/${cause.id}/consequences`, {
            headers: { Authorization: `Bearer ${token}` }
          });
          newConsequencesByCause[cause.id] = response.data;
        } catch (err) {
          console.error(`Failed to load consequences for cause ${cause.id}:`, err);
          newConsequencesByCause[cause.id] = [];
        }
      }

      // For each consequence, load its safeguards and recommendations
      for (const consequence of consequences) {
        // Load safeguards
        try {
          const response = await axios.get(`${API_URL}/api/hazop/consequences/${consequence.id}/safeguards`, {
            headers: { Authorization: `Bearer ${token}` }
          });
          newSafeguardsByConsequence[consequence.id] = response.data;
        } catch (err) {
          console.error(`Failed to load safeguards for consequence ${consequence.id}:`, err);
          newSafeguardsByConsequence[consequence.id] = [];
        }

        // Load recommendations
        try {
          const response = await axios.get(`${API_URL}/api/hazop/consequences/${consequence.id}/recommendations`, {
            headers: { Authorization: `Bearer ${token}` }
          });
          newRecommendationsByConsequence[consequence.id] = response.data;
        } catch (err) {
          console.error(`Failed to load recommendations for consequence ${consequence.id}:`, err);
          newRecommendationsByConsequence[consequence.id] = [];
        }

        // Load impact assessment for this consequence
        try {
          const response = await axios.get(`${API_URL}/api/consequences/${consequence.id}/impact-assessment`, {
            headers: { Authorization: `Bearer ${token}` }
          });
          newImpactAssessments[consequence.id] = response.data;
        } catch (err) {
          // 404 is expected if no assessment exists yet
          if (axios.isAxiosError(err) && err.response?.status !== 404) {
            console.error(`Failed to load impact assessment for consequence ${consequence.id}:`, err);
          }
        }
      }

      setConsequencesByCause(newConsequencesByCause);
      setSafeguardsByConsequence(newSafeguardsByConsequence);
      setRecommendationsByConsequence(newRecommendationsByConsequence);
      setImpactAssessmentsByConsequence(newImpactAssessments);
    } catch (err) {
      console.error('Failed to load hierarchical data:', err);
    }
  };

  const loadCurrentRisk = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `${API_URL}/api/deviations/${deviation.id}/impact-assessment`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setCurrentRiskLevel(response.data.risk_level);
    } catch (err: any) {
      // 404 is expected if no assessment exists yet
      if (err.response?.status !== 404) {
        console.error('Failed to load risk assessment:', err);
      }
      setCurrentRiskLevel(null);
    }
  };

  const loadCauses = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_URL}/api/hazop/deviations/${deviation.id}/causes`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setCauses(response.data);
      return response.data;
    } catch (err) {
      console.error('Failed to load causes:', err);
      setCauses([]);
      return [];
    }
  };

  const loadConsequences = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_URL}/api/hazop/deviations/${deviation.id}/consequences`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setConsequences(response.data);
      return response.data;
    } catch (err) {
      console.error('Failed to load consequences:', err);
      setConsequences([]);
      return [];
    }
  };

  const loadSafeguards = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_URL}/api/hazop/deviations/${deviation.id}/safeguards`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setSafeguards(response.data);
      return response.data;
    } catch (err) {
      console.error('Failed to load safeguards:', err);
      setSafeguards([]);
      return [];
    }
  };

  const loadRecommendations = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_URL}/api/hazop/deviations/${deviation.id}/recommendations`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setRecommendations(response.data);
      return response.data;
    } catch (err) {
      console.error('Failed to load recommendations:', err);
      setRecommendations([]);
      return [];
    }
  };

  const deleteCause = async (causeId: string) => {
    if (!confirm('Delete this cause?')) return;
    try {
      const token = localStorage.getItem('token');
      await axios.delete(`${API_URL}/api/hazop/causes/${causeId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      loadCauses();
    } catch (err) {
      console.error('Failed to delete cause:', err);
    }
  };

  const deleteConsequence = async (consequenceId: string) => {
    if (!confirm('Delete this consequence?')) return;
    try {
      const token = localStorage.getItem('token');
      await axios.delete(`${API_URL}/api/hazop/consequences/${consequenceId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      // Reset selected consequence if it was the one deleted
      if (selectedConsequenceId === consequenceId) {
        setSelectedConsequenceId(null);
      }

      // Reload all relevant data
      await loadConsequences();
      await loadHierarchicalData(); // Reload relationships
      await loadCurrentRisk();      // Update risk assessment data
    } catch (err) {
      console.error('Failed to delete consequence:', err);
      alert('An error occurred while deleting the consequence. Please try again.');
    }
  };

  const deleteSafeguard = async (safeguardId: string) => {
    if (!confirm('Delete this safeguard?')) return;
    try {
      const token = localStorage.getItem('token');
      await axios.delete(`${API_URL}/api/hazop/safeguards/${safeguardId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      await loadSafeguards();
      await loadHierarchicalData(); // Reload relationships
    } catch (err) {
      console.error('Failed to delete safeguard:', err);
      alert('An error occurred while deleting the safeguard. Please try again.');
    }
  };

  const deleteRecommendation = async (recommendationId: string) => {
    if (!confirm('Delete this recommendation?')) return;
    try {
      const token = localStorage.getItem('token');
      await axios.delete(`${API_URL}/api/hazop/recommendations/${recommendationId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      await loadRecommendations();
      await loadHierarchicalData(); // Reload relationships
    } catch (err) {
      console.error('Failed to delete recommendation:', err);
      alert('An error occurred while deleting the recommendation. Please try again.');
    }
  };

  const findSimilarDeviations = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API_URL}/api/studies/deviations/similar`, {
        params: {
          parameter: deviation.parameter,
          guide_word: deviation.guide_word
        },
        headers: { Authorization: `Bearer ${token}` }
      });
      setSimilarDeviations(response.data);
      setShowCopyModal(true);
    } catch (err) {
      console.error('Failed to find similar deviations:', err);
      alert('Failed to find similar deviations');
    }
  };

  const copyFromPrevious = async (sourceDeviationId: string) => {
    try {
      const token = localStorage.getItem('token');
      await axios.post(
        `${API_URL}/api/studies/deviations/${deviation.id}/copy-from-previous`,
        {
          source_deviation_id: sourceDeviationId,
          copy_causes: true,
          copy_consequences: true,
          copy_safeguards: true,
          copy_recommendations: false
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setShowCopyModal(false);
      loadAll();
      alert('Data copied successfully!');
    } catch (err) {
      console.error('Failed to copy from previous:', err);
      alert('Failed to copy data');
    }
  };

  const createCause = async (e: React.FormEvent) => {
    e.preventDefault();
    const form = e.target as HTMLFormElement;
    const formData = new FormData(form);

    try {
      const token = localStorage.getItem('token');
      await axios.post(`${API_URL}/api/hazop/causes`, {
        deviation_id: deviation.id,
        cause_description: formData.get('cause_description'),
        likelihood: formData.get('likelihood') || null
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setShowCauseModal(false);
      form.reset();
      loadCauses();
    } catch (err) {
      console.error('Failed to create cause:', err);
    }
  };

  const createConsequence = async (e: React.FormEvent) => {
    e.preventDefault();
    const form = e.target as HTMLFormElement;
    const formData = new FormData(form);

    // Always use the selected cause for new consequences
    if (!selectedCauseId) {
      alert("Please select a cause first");
      return;
    }

    // Get all selected categories
    const checkboxes = form.querySelectorAll<HTMLInputElement>('input[name="categories"]:checked');
    const categories = Array.from(checkboxes).map(cb => cb.value).join(',');

    try {
      const token = localStorage.getItem('token');
      await axios.post(`${API_URL}/api/hazop/consequences`, {
        deviation_id: deviation.id,
        cause_id: selectedCauseId, // Always use the selected cause
        consequence_description: formData.get('consequence_description'),
        severity: formData.get('severity') || null,
        category: categories || null
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setShowConsequenceModal(false);
      form.reset();
      await loadConsequences();
      await loadHierarchicalData(); // Reload hierarchical data to update relationships
    } catch (err) {
      console.error('Failed to create consequence:', err);
    }
  };

  const createSafeguard = async (e: React.FormEvent) => {
    e.preventDefault();
    const form = e.target as HTMLFormElement;
    const formData = new FormData(form);

    // Always use the selected consequence for new safeguards
    if (!selectedConsequenceId) {
      alert("Please select a consequence first");
      return;
    }

    try {
      const token = localStorage.getItem('token');
      await axios.post(`${API_URL}/api/hazop/safeguards`, {
        deviation_id: deviation.id,
        consequence_id: selectedConsequenceId, // Always use the selected consequence
        safeguard_description: formData.get('safeguard_description'),
        safeguard_type: formData.get('safeguard_type') || null,
        effectiveness: formData.get('effectiveness') || null
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setShowSafeguardModal(false);
      form.reset();
      await loadSafeguards();
      await loadHierarchicalData(); // Reload hierarchical data to update relationships
    } catch (err) {
      console.error('Failed to create safeguard:', err);
    }
  };

  const createRecommendation = async (e: React.FormEvent) => {
    e.preventDefault();
    const form = e.target as HTMLFormElement;
    const formData = new FormData(form);

    // Always use the selected consequence for new recommendations
    if (!selectedConsequenceId) {
      alert("Please select a consequence first");
      return;
    }

    try {
      const token = localStorage.getItem('token');
      await axios.post(`${API_URL}/api/hazop/recommendations`, {
        deviation_id: deviation.id,
        consequence_id: selectedConsequenceId, // Always use the selected consequence
        recommendation_description: formData.get('recommendation_description'),
        priority: formData.get('priority') || null,
        responsible_party: formData.get('responsible_party') || null,
        target_date: formData.get('target_date') || null
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setShowRecommendationModal(false);
      form.reset();
      await loadRecommendations();
      await loadHierarchicalData(); // Reload hierarchical data to update relationships
    } catch (err) {
      console.error('Failed to create recommendation:', err);
    }
  };

  return (
    <div className="space-y-4">
      {/* Header with Copy from Previous Button */}
      <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg p-3 border border-purple-200">
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-lg font-bold text-gray-900">HAZOP Analysis</h2>
            <p className="text-sm text-gray-600">{deviation.parameter} / {deviation.guide_word}</p>
            <p className="text-sm text-gray-500 mt-1">{deviation.deviation_description}</p>
          </div>
          <button
            onClick={findSimilarDeviations}
            className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 shadow-md"
          >
            <span>📋</span>
            <span>Copy from Previous</span>
          </button>
        </div>
      </div>

      {/* HAZOP Worksheet Grid Layout - Horizontal Flow */}
      <div className="bg-white rounded-lg shadow p-4">
        {/* Action Buttons Bar */}
        <div className="flex justify-between items-center mb-4 border-b pb-3">
          <h3 className="text-md font-semibold text-gray-900">HAZOP Worksheet</h3>
          <div className="flex gap-2">
            <button
              onClick={() => setShowCauseModal(true)}
              className="text-sm bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700 flex items-center gap-1"
            >
              <span>+</span> Add Cause
            </button>
            {selectedCauseId && (
              <button
                onClick={() => {
                  setShowConsequenceModal(true);
                }}
                className="text-sm bg-red-500 text-white px-3 py-1 rounded hover:bg-red-600 flex items-center gap-1"
              >
                <span>+</span> Add Consequence
              </button>
            )}
            {selectedConsequenceId && (
              <>
                <button
                  onClick={() => {
                    setShowSafeguardModal(true);
                  }}
                  className="text-sm bg-green-600 text-white px-3 py-1 rounded hover:bg-green-700 flex items-center gap-1"
                >
                  <span>+</span> Add Safeguard
                </button>
                <button
                  onClick={() => {
                    setShowRecommendationModal(true);
                  }}
                  className="text-sm bg-purple-600 text-white px-3 py-1 rounded hover:bg-purple-700 flex items-center gap-1"
                >
                  <span>+</span> Add Recommendation
                </button>
                <button
                  onClick={() => setShowRiskAssessment(true)}
                  className="text-sm bg-amber-600 text-white px-3 py-1 rounded hover:bg-amber-700 flex items-center gap-1"
                >
                  <span>🎯</span> Risk Assessment
                </button>
              </>
            )}
          </div>
        </div>

        {/* HAZOP Worksheet Content */}
        <div>
          {causes.length > 0 ? (
            <div className="hazop-worksheet-container">
              {/* HAZOP Grid Header */}
              <div className="hazop-grid mb-2 text-xs font-semibold text-gray-700">
                <div className="hazop-col hazop-col-causes">Causes</div>
                <div className="hazop-col hazop-col-consequences">Consequences</div>
                <div className="hazop-col hazop-col-safeguards">Safeguards</div>
                <div className="hazop-col hazop-col-recommendations">Recommendations</div>
                <div className="hazop-col hazop-col-risk">Risk</div>
              </div>

              {/* Scrollable Grid Content */}
              <div className="space-y-4">
                {causes.map((cause) => (
                  <div key={cause.id} className="hazop-grid">
                    {/* Cause Column */}
                    <div className="hazop-col hazop-col-causes border rounded-lg overflow-hidden bg-white">
                      <div
                        className={`border-l-4 border-blue-500 px-3 py-3 bg-blue-50 flex justify-between items-start cursor-pointer ${
                          selectedCauseId === cause.id ? 'bg-blue-100' : ''
                        }`}
                        onClick={() => setSelectedCauseId(selectedCauseId === cause.id ? null : cause.id)}
                      >
                        <div className="flex-1">
                          <p className="text-sm font-medium mb-1">{cause.cause_description}</p>
                          {cause.likelihood && (
                            <span className="text-xs text-gray-600 block">
                              Likelihood: <span className="font-semibold">{cause.likelihood}</span>
                            </span>
                          )}
                          <span className="text-xs bg-blue-100 text-blue-800 px-1.5 py-0.5 rounded-full inline-block mt-1">
                            {consequencesByCause[cause.id]?.length || 0} consequences
                          </span>
                        </div>
                        <div className="flex flex-col items-end">
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              deleteCause(cause.id);
                            }}
                            className="text-red-600 hover:text-red-800 text-sm"
                            title="Delete cause"
                          >
                            🗑️
                          </button>
                          <span className="text-xs mt-1">
                            {selectedCauseId === cause.id ? '◀' : '▶'}
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Consequences Column - Only show if this cause is selected */}
                    <div className="hazop-col hazop-col-consequences border rounded-lg overflow-y-auto bg-white" style={{ maxHeight: '400px' }}>
                      {selectedCauseId === cause.id ? (
                        <>
                          <div className="px-3 py-2 bg-red-50 border-b border-red-100 flex justify-between items-center sticky top-0 z-10">
                            <h4 className="text-xs font-semibold text-gray-700">Consequences</h4>
                          </div>
                          <div className="divide-y divide-gray-100">
                            {consequencesByCause[cause.id]?.length > 0 ? (
                              consequencesByCause[cause.id]?.map((consequence) => (
                                <div
                                  key={consequence.id}
                                  className={`border-l-2 px-3 py-2 ${
                                    selectedConsequenceId === consequence.id
                                      ? 'border-red-500 bg-red-50'
                                      : 'border-red-200 hover:bg-red-50'
                                  } cursor-pointer`}
                                  onClick={() =>
                                    setSelectedConsequenceId(
                                      selectedConsequenceId === consequence.id ? null : consequence.id
                                    )
                                  }
                                >
                                  <div className="flex justify-between">
                                    <p className="text-xs">{consequence.consequence_description}</p>
                                    <button
                                      onClick={(e) => {
                                        e.stopPropagation();
                                        deleteConsequence(consequence.id);
                                      }}
                                      className="text-red-600 hover:text-red-800 text-xs ml-1 opacity-50 hover:opacity-100"
                                      title="Delete consequence"
                                    >
                                      🗑️
                                    </button>
                                  </div>
                                  <div className="flex gap-2 mt-1">
                                    {consequence.severity && (
                                      <span className="text-xs text-gray-600">
                                        Severity: <span className="font-semibold">{consequence.severity}</span>
                                      </span>
                                    )}
                                    {consequence.category && (
                                      <span className="text-xs text-gray-600">
                                        Category: <span className="font-semibold">
                                          {consequence.category.includes(',')
                                            ? consequence.category.split(',').map(cat =>
                                                cat.charAt(0).toUpperCase() + cat.slice(1)).join(', ')
                                            : consequence.category.charAt(0).toUpperCase() + consequence.category.slice(1)}
                                        </span>
                                      </span>
                                    )}
                                  </div>
                                </div>
                              ))
                            ) : (
                              <p className="text-xs text-gray-500 italic p-3">
                                No consequences added for this cause yet
                              </p>
                            )}
                          </div>
                        </>
                      ) : (
                        <div className="p-3 text-xs text-gray-400 italic text-center h-full flex items-center justify-center">
                          Select cause to view consequences
                        </div>
                      )}
                    </div>

                    {/* Safeguards Column - Only show if a consequence for this cause is selected */}
                    <div className="hazop-col hazop-col-safeguards border rounded-lg overflow-y-auto bg-white" style={{ maxHeight: '400px' }}>
                      {selectedConsequenceId &&
                      consequencesByCause[cause.id]?.some(
                        (consequence) => consequence.id === selectedConsequenceId
                      ) ? (
                        <>
                          <div className="px-3 py-2 bg-green-50 border-b border-green-100 flex justify-between items-center sticky top-0 z-10">
                            <h4 className="text-xs font-semibold text-gray-700">Safeguards</h4>
                          </div>
                          <div className="divide-y divide-gray-100">
                            {safeguardsByConsequence[selectedConsequenceId]?.length > 0 ? (
                              safeguardsByConsequence[selectedConsequenceId]?.map((safeguard) => (
                                <div
                                  key={safeguard.id}
                                  className="border-l-2 border-green-300 px-3 py-2 hover:bg-green-50"
                                >
                                  <div className="flex justify-between">
                                    <p className="text-xs">{safeguard.safeguard_description}</p>
                                    <button
                                      onClick={() => deleteSafeguard(safeguard.id)}
                                      className="text-red-600 hover:text-red-800 text-xs ml-1 opacity-50 hover:opacity-100"
                                      title="Delete safeguard"
                                    >
                                      🗑️
                                    </button>
                                  </div>
                                  <div className="flex gap-2 flex-wrap mt-1">
                                    {safeguard.safeguard_type && (
                                      <span className="text-xs text-gray-600">
                                        Type: <span className="font-semibold">{safeguard.safeguard_type}</span>
                                      </span>
                                    )}
                                    {safeguard.effectiveness && (
                                      <span className="text-xs text-gray-600">
                                        Effectiveness:{' '}
                                        <span className="font-semibold">{safeguard.effectiveness}</span>
                                      </span>
                                    )}
                                  </div>
                                </div>
                              ))
                            ) : (
                              <p className="text-xs text-gray-500 italic p-3">
                                No safeguards added for this consequence yet
                              </p>
                            )}
                          </div>
                        </>
                      ) : (
                        <div className="p-3 text-xs text-gray-400 italic text-center h-full flex items-center justify-center">
                          Select consequence to view safeguards
                        </div>
                      )}
                    </div>

                    {/* Recommendations Column - Only show if a consequence for this cause is selected */}
                    <div className="hazop-col hazop-col-recommendations border rounded-lg overflow-y-auto bg-white" style={{ maxHeight: '400px' }}>
                      {selectedConsequenceId &&
                      consequencesByCause[cause.id]?.some(
                        (consequence) => consequence.id === selectedConsequenceId
                      ) ? (
                        <>
                          <div className="px-3 py-2 bg-purple-50 border-b border-purple-100 flex justify-between items-center sticky top-0 z-10">
                            <h4 className="text-xs font-semibold text-gray-700">Recommendations</h4>
                          </div>
                          <div className="divide-y divide-gray-100">
                            {recommendationsByConsequence[selectedConsequenceId]?.length > 0 ? (
                              recommendationsByConsequence[selectedConsequenceId]?.map((rec) => (
                                <div
                                  key={rec.id}
                                  className="border-l-2 border-purple-300 px-3 py-2 hover:bg-purple-50"
                                >
                                  <div className="flex justify-between">
                                    <p className="text-xs">{rec.recommendation_description}</p>
                                    <button
                                      onClick={() => deleteRecommendation(rec.id)}
                                      className="text-red-600 hover:text-red-800 text-xs ml-1 opacity-50 hover:opacity-100"
                                      title="Delete recommendation"
                                    >
                                      🗑️
                                    </button>
                                  </div>
                                  <div className="flex flex-wrap gap-2 mt-1">
                                    {rec.priority && (
                                      <span
                                        className={`text-xs px-1.5 py-0.5 rounded ${
                                          rec.priority === 'critical'
                                            ? 'bg-red-100 text-red-800'
                                            : rec.priority === 'high'
                                            ? 'bg-orange-100 text-orange-800'
                                            : rec.priority === 'medium'
                                            ? 'bg-yellow-100 text-yellow-800'
                                            : 'bg-blue-100 text-blue-800'
                                        }`}
                                      >
                                        {rec.priority}
                                      </span>
                                    )}
                                    {rec.responsible_party && (
                                      <span className="text-xs bg-purple-100 text-purple-800 px-1.5 py-0.5 rounded">
                                        {rec.responsible_party}
                                      </span>
                                    )}
                                  </div>
                                </div>
                              ))
                            ) : (
                              <p className="text-xs text-gray-500 italic p-3">
                                No recommendations added for this consequence yet
                              </p>
                            )}
                          </div>
                        </>
                      ) : (
                        <div className="p-3 text-xs text-gray-400 italic text-center h-full flex items-center justify-center">
                          Select consequence to view recommendations
                        </div>
                      )}
                    </div>

                    {/* Risk Assessment Column - Now visible on all screen sizes */}
                    <div className="hazop-col hazop-col-risk border rounded-lg overflow-y-auto bg-white" style={{ maxHeight: '400px' }}>
                      {selectedConsequenceId &&
                      consequencesByCause[cause.id]?.some(
                        (consequence) => consequence.id === selectedConsequenceId
                      ) ? (
                        <>
                          <div className="px-3 py-2 bg-amber-50 border-b border-amber-100 flex justify-between items-center sticky top-0 z-10">
                            <h4 className="text-xs font-semibold text-gray-700">Risk Assessment</h4>
                          </div>
                          <div className="p-3">
                            {impactAssessmentsByConsequence[selectedConsequenceId] ? (
                              <>
                                <div className="flex justify-center mb-2">
                                  <RiskBadge
                                    riskLevel={
                                      impactAssessmentsByConsequence[selectedConsequenceId].risk_level
                                    }
                                    riskScore={
                                      impactAssessmentsByConsequence[selectedConsequenceId].risk_score
                                    }
                                    showScore
                                  />
                                </div>
                                <div className="grid grid-cols-2 gap-1 text-xs">
                                  <div>
                                    <span className="text-gray-600">Max Impact: </span>
                                    <span className="font-semibold">
                                      {impactAssessmentsByConsequence[selectedConsequenceId].max_impact}
                                    </span>
                                  </div>
                                  <div>
                                    <span className="text-gray-600">Likelihood: </span>
                                    <span className="font-semibold">
                                      {impactAssessmentsByConsequence[selectedConsequenceId].likelihood}
                                    </span>
                                  </div>
                                  <div className="col-span-2 mt-1">
                                    <button
                                      onClick={() => setShowRiskAssessment(true)}
                                      className="w-full text-xs bg-amber-600 text-white px-2 py-1 rounded hover:bg-amber-700 mt-2"
                                    >
                                      Details
                                    </button>
                                  </div>
                                </div>
                              </>
                            ) : (
                              <div className="flex flex-col items-center gap-2 justify-center h-full">
                                <p className="text-xs text-gray-500 text-center">Not assessed</p>
                                <button
                                  onClick={() => {
                                    setSelectedConsequenceId(selectedConsequenceId);
                                    setShowRiskAssessment(true);
                                  }}
                                  className="text-xs bg-amber-600 text-white px-2 py-1 rounded hover:bg-amber-700"
                                >
                                  Assess Risk
                                </button>
                              </div>
                            )}
                          </div>
                        </>
                      ) : (
                        <div className="p-3 text-xs text-gray-400 italic text-center h-full flex items-center justify-center">
                          Select consequence to view risk
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="text-center py-8">
              <p className="text-sm text-gray-500 mb-4">No causes added yet</p>
              <button
                onClick={() => setShowCauseModal(true)}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                + Add First Cause
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Risk Assessment is now fully integrated in the grid, so we removed the separate mobile section */}

      {/* Risk Assessment Modal */}
      {showRiskAssessment && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-3xl w-full mx-4 max-h-[80vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold">🎯 Risk Assessment</h2>
              <button
                onClick={() => setShowRiskAssessment(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                ✕
              </button>
            </div>

            <div>
              <h3 className="text-md font-semibold mb-4">Select consequence to assess:</h3>
              <select
                className="w-full border rounded px-3 py-2 mb-4"
                value={selectedConsequenceId || ""}
                onChange={(e) => setSelectedConsequenceId(e.target.value || null)}
              >
                <option value="">Overall Deviation Risk (Legacy)</option>
                {consequences.map(consequence => (
                  <option key={consequence.id} value={consequence.id}>
                    {consequence.consequence_description.substring(0, 80)}
                    {consequence.consequence_description.length > 80 ? '...' : ''}
                  </option>
                ))}
              </select>
            </div>

            <ImpactAssessmentForm
              deviationId={selectedConsequenceId ? undefined : deviation.id}
              consequenceId={selectedConsequenceId || undefined}
              onSaved={() => {
                loadCurrentRisk();
                loadHierarchicalData();
                setShowRiskAssessment(false); // Close the modal after saving
              }}
            />
          </div>
        </div>
      )}

      {/* Overview Section */}
      {(causes.length === 0 || !selectedCauseId) && (
        <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex justify-between items-center mb-3">
              <h3 className="text-md font-semibold text-gray-900">Overview</h3>
            </div>
            <div className="space-y-1">
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Causes:</span>
                <span className="text-sm font-semibold">{causes.length}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Consequences:</span>
                <span className="text-sm font-semibold">{consequences.length}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Safeguards:</span>
                <span className="text-sm font-semibold">{safeguards.length}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Recommendations:</span>
                <span className="text-sm font-semibold">{recommendations.length}</span>
              </div>
            </div>
            {causes.length > 0 && (
              <div className="mt-4 text-center text-sm text-gray-600">
                <p>Select a cause to view the HAZOP worksheet.</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Modals */}
      {showCauseModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h2 className="text-xl font-bold mb-4">Add Cause</h2>
            <form onSubmit={createCause} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Cause Description *</label>
                <textarea
                  name="cause_description"
                  className="w-full border rounded px-3 py-2"
                  rows={3}
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Likelihood</label>
                <select name="likelihood" className="w-full border rounded px-3 py-2">
                  <option value="">Select...</option>
                  <option value="rare">Rare</option>
                  <option value="unlikely">Unlikely</option>
                  <option value="possible">Possible</option>
                  <option value="likely">Likely</option>
                  <option value="almost_certain">Almost Certain</option>
                </select>
              </div>
              <div className="flex justify-end gap-2">
                <button type="button" onClick={() => setShowCauseModal(false)} className="px-4 py-2 border rounded">Cancel</button>
                <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded">Add</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showConsequenceModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h2 className="text-xl font-bold mb-4">Add Consequence</h2>
            <form onSubmit={createConsequence} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Related Cause</label>
                <select
                  name="cause_id"
                  className="w-full border rounded px-3 py-2"
                >
                  <option value="">Not specific to any cause</option>
                  {causes.map(cause => (
                    <option key={cause.id} value={cause.id}>
                      {cause.cause_description.substring(0, 80)}
                      {cause.cause_description.length > 80 ? '...' : ''}
                    </option>
                  ))}
                </select>
                <p className="text-xs text-gray-500 mt-1">
                  Select a specific cause that this consequence relates to (optional)
                </p>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Consequence Description *</label>
                <textarea
                  name="consequence_description"
                  className="w-full border rounded px-3 py-2"
                  rows={3}
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Severity</label>
                <select name="severity" className="w-full border rounded px-3 py-2">
                  <option value="">Select...</option>
                  <option value="negligible">Negligible</option>
                  <option value="minor">Minor</option>
                  <option value="moderate">Moderate</option>
                  <option value="major">Major</option>
                  <option value="catastrophic">Catastrophic</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Categories (select all that apply)</label>
                <div className="space-y-2 mt-2">
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="category-safety"
                      name="categories"
                      value="safety"
                      className="mr-2"
                    />
                    <label htmlFor="category-safety" className="text-sm">Safety</label>
                  </div>
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="category-environmental"
                      name="categories"
                      value="environmental"
                      className="mr-2"
                    />
                    <label htmlFor="category-environmental" className="text-sm">Environmental</label>
                  </div>
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="category-operational"
                      name="categories"
                      value="operational"
                      className="mr-2"
                    />
                    <label htmlFor="category-operational" className="text-sm">Operational</label>
                  </div>
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="category-financial"
                      name="categories"
                      value="financial"
                      className="mr-2"
                    />
                    <label htmlFor="category-financial" className="text-sm">Financial</label>
                  </div>
                </div>
              </div>
              <div className="flex justify-end gap-2">
                <button type="button" onClick={() => setShowConsequenceModal(false)} className="px-4 py-2 border rounded">Cancel</button>
                <button type="submit" className="px-4 py-2 bg-red-600 text-white rounded">Add</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showSafeguardModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h2 className="text-xl font-bold mb-4">Add Safeguard</h2>
            <form onSubmit={createSafeguard} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Related Consequence</label>
                <select
                  name="consequence_id"
                  className="w-full border rounded px-3 py-2"
                >
                  <option value="">Not specific to any consequence</option>
                  {consequences.map(consequence => (
                    <option key={consequence.id} value={consequence.id}>
                      {consequence.consequence_description.substring(0, 80)}
                      {consequence.consequence_description.length > 80 ? '...' : ''}
                    </option>
                  ))}
                </select>
                <p className="text-xs text-gray-500 mt-1">
                  Select a specific consequence that this safeguard addresses (optional)
                </p>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Safeguard Description *</label>
                <textarea
                  name="safeguard_description"
                  className="w-full border rounded px-3 py-2"
                  rows={3}
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Type</label>
                <select name="safeguard_type" className="w-full border rounded px-3 py-2">
                  <option value="">Select...</option>
                  <option value="prevention">Prevention</option>
                  <option value="detection">Detection</option>
                  <option value="mitigation">Mitigation</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Effectiveness</label>
                <select name="effectiveness" className="w-full border rounded px-3 py-2">
                  <option value="">Select...</option>
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                </select>
              </div>
              <div className="flex justify-end gap-2">
                <button type="button" onClick={() => setShowSafeguardModal(false)} className="px-4 py-2 border rounded">Cancel</button>
                <button type="submit" className="px-4 py-2 bg-green-600 text-white rounded">Add</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showRecommendationModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <h2 className="text-xl font-bold mb-4">Add Recommendation</h2>
            <form onSubmit={createRecommendation} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Related Consequence</label>
                <select
                  name="consequence_id"
                  className="w-full border rounded px-3 py-2"
                >
                  <option value="">Not specific to any consequence</option>
                  {consequences.map(consequence => (
                    <option key={consequence.id} value={consequence.id}>
                      {consequence.consequence_description.substring(0, 80)}
                      {consequence.consequence_description.length > 80 ? '...' : ''}
                    </option>
                  ))}
                </select>
                <p className="text-xs text-gray-500 mt-1">
                  Select a specific consequence that this recommendation addresses (optional)
                </p>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Recommendation *</label>
                <textarea
                  name="recommendation_description"
                  className="w-full border rounded px-3 py-2"
                  rows={3}
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Priority</label>
                <select name="priority" className="w-full border rounded px-3 py-2">
                  <option value="">Select...</option>
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="critical">Critical</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Responsible Party</label>
                <input
                  type="text"
                  name="responsible_party"
                  className="w-full border rounded px-3 py-2"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Target Date</label>
                <input
                  type="date"
                  name="target_date"
                  className="w-full border rounded px-3 py-2"
                />
              </div>
              <div className="flex justify-end gap-2">
                <button type="button" onClick={() => setShowRecommendationModal(false)} className="px-4 py-2 border rounded">Cancel</button>
                <button type="submit" className="px-4 py-2 bg-purple-600 text-white rounded">Add</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Copy from Previous Modal */}
      {showCopyModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-3xl w-full mx-4 max-h-[80vh] overflow-y-auto">
            <h2 className="text-xl font-bold mb-4">
              💡 Similar Deviations Found: {similarDeviations.length}
            </h2>
            <p className="text-sm text-gray-600 mb-4">
              Found deviations with {deviation.parameter} / {deviation.guide_word} from other nodes/studies. Click "Copy All" to copy causes, consequences, and safeguards.
            </p>

            {similarDeviations.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <p className="mb-2">No similar deviations found in other studies.</p>
                <p className="text-sm">This appears to be a unique deviation.</p>
              </div>
            ) : (
              <div className="space-y-3">
                {similarDeviations.map((dev: any) => (
                  <div key={dev.deviation_id} className="border rounded-lg p-4 hover:bg-gray-50 transition-colors">
                    <div className="flex justify-between items-start mb-2">
                      <div className="flex-1">
                        <div className="font-semibold text-lg">{dev.node_number} - {dev.node_name}</div>
                        <div className="text-sm text-gray-600">{dev.study_name}</div>
                        <div className="text-sm text-gray-500 mt-1">{dev.deviation_description}</div>
                      </div>
                    </div>

                    <div className="flex gap-3 mt-3 mb-3">
                      <span className="text-xs px-2 py-1 rounded bg-blue-100 text-blue-800">
                        {dev.causes_count} causes
                      </span>
                      <span className="text-xs px-2 py-1 rounded bg-red-100 text-red-800">
                        {dev.consequences_count} consequences
                      </span>
                      <span className="text-xs px-2 py-1 rounded bg-green-100 text-green-800">
                        {dev.safeguards_count} safeguards
                      </span>
                      {dev.recommendations_count > 0 && (
                        <span className="text-xs px-2 py-1 rounded bg-purple-100 text-purple-800">
                          {dev.recommendations_count} recommendations
                        </span>
                      )}
                    </div>

                    <button
                      onClick={() => copyFromPrevious(dev.deviation_id)}
                      className="w-full px-4 py-2 bg-purple-600 text-white rounded hover:bg-purple-700 flex items-center justify-center gap-2"
                    >
                      <span>📋</span>
                      <span>Copy All Data</span>
                    </button>
                  </div>
                ))}
              </div>
            )}

            <div className="mt-6 flex justify-end">
              <button
                onClick={() => setShowCopyModal(false)}
                className="px-4 py-2 border rounded hover:bg-gray-50"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
