import { useState, useEffect } from 'react';
import axios from 'axios';
import { RiskMatrixViewer } from './RiskMatrixViewer';
import { RiskBadge } from './RiskBadge';
import type { ImpactAssessment } from '../types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface ImpactAssessmentFormProps {
  deviationId?: string; // Made optional
  consequenceId?: string; // Added to support consequence-specific assessment
  onSaved?: () => void;
}

// Impact descriptions based on screenshot 2.png - Using A-E labels to match Risk Matrix
const IMPACT_DESCRIPTIONS = {
  safety: {
    1: "A - Minor: First aid treatment only",
    2: "B - Limited: Medical treatment required",
    3: "C - Moderate: Lost time injury",
    4: "D - Significant: Permanent disablement",
    5: "E - Major/Critical: Fatality"
  },
  financial: {
    1: "A - Minor: <$10K",
    2: "B - Limited: $10K-$100K",
    3: "C - Moderate: $100K-$1M",
    4: "D - Significant: $1M-$10M",
    5: "E - Major: >$10M"
  },
  environmental: {
    1: "A - Minor: Contained, no impact",
    2: "B - Limited: Localized impact",
    3: "C - Moderate: Regional impact",
    4: "D - Significant: Substantial impact",
    5: "E - Major: Environmental catastrophe"
  },
  reputation: {
    1: "A - Minor: Local awareness",
    2: "B - Limited: Regional awareness",
    3: "C - Moderate: National awareness",
    4: "D - Significant: International impact",
    5: "E - Major: Severe long-term damage"
  },
  schedule: {
    1: "A - Minor: <1 day delay",
    2: "B - Limited: 1-7 days",
    3: "C - Moderate: 1-4 weeks",
    4: "D - Significant: 1-3 months",
    5: "E - Major: >3 months"
  },
  performance: {
    1: "A - Minor: <5% degradation",
    2: "B - Limited: 5-15%",
    3: "C - Moderate: 15-30%",
    4: "D - Significant: 30-50%",
    5: "E - Major: >50% or shutdown"
  }
};

const LIKELIHOOD_DESCRIPTIONS = {
  1: "Very Unlikely: Not occurred in similar operations",
  2: "Unlikely: Occurred in similar operations",
  3: "Possible: Has occurred in this operation",
  4: "Highly Likely: Several times per year",
  5: "Probable: Occurs frequently"
};

export const ImpactAssessmentForm = ({ deviationId, consequenceId, onSaved }: ImpactAssessmentFormProps) => {
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [existingAssessment, setExistingAssessment] = useState<ImpactAssessment | null>(null);

  const [formData, setFormData] = useState({
    safety_impact: 1,
    financial_impact: 1,
    environmental_impact: 1,
    reputation_impact: 1,
    schedule_impact: 1,
    performance_impact: 1,
    likelihood: 1,
    assessment_notes: ''
  });

  const [calculatedRisk, setCalculatedRisk] = useState({
    max_impact: 1,
    risk_score: 1,
    risk_level: 'Low' as 'Low' | 'Medium' | 'High' | 'Critical',
    risk_color: 'green'
  });

  useEffect(() => {
    loadExistingAssessment();
  }, [deviationId]);

  useEffect(() => {
    // Recalculate risk whenever form data changes
    calculateRisk();
  }, [
    formData.safety_impact,
    formData.financial_impact,
    formData.environmental_impact,
    formData.reputation_impact,
    formData.schedule_impact,
    formData.performance_impact,
    formData.likelihood
  ]);

  const loadExistingAssessment = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');

      let url;
      if (consequenceId) {
        // If consequence ID is provided, load assessment for that consequence
        url = `${API_URL}/api/consequences/${consequenceId}/impact-assessment`;
      } else if (deviationId) {
        // Otherwise, use the legacy deviation-based assessment
        url = `${API_URL}/api/deviations/${deviationId}/impact-assessment`;
      } else {
        console.error('Either deviationId or consequenceId must be provided');
        setLoading(false);
        return;
      }

      const response = await axios.get(url, {
        headers: { Authorization: `Bearer ${token}` }
      });

      setExistingAssessment(response.data);
      setFormData({
        safety_impact: response.data.safety_impact,
        financial_impact: response.data.financial_impact,
        environmental_impact: response.data.environmental_impact,
        reputation_impact: response.data.reputation_impact,
        schedule_impact: response.data.schedule_impact,
        performance_impact: response.data.performance_impact,
        likelihood: response.data.likelihood,
        assessment_notes: response.data.assessment_notes || ''
      });
    } catch (err: any) {
      if (err.response?.status !== 404) {
        console.error('Failed to load impact assessment:', err);
      }
      // 404 is expected for new assessments
    } finally {
      setLoading(false);
    }
  };

  const calculateRisk = () => {
    const impacts = [
      formData.safety_impact,
      formData.financial_impact,
      formData.environmental_impact,
      formData.reputation_impact,
      formData.schedule_impact,
      formData.performance_impact
    ];

    const max_impact = Math.max(...impacts);
    const risk_score = formData.likelihood * max_impact;

    let risk_level: 'Low' | 'Medium' | 'High' | 'Critical' = 'Low';
    let risk_color = 'green';

    if (risk_score <= 7) {
      risk_level = 'Low';
      risk_color = 'green';
    } else if (risk_score <= 16) {
      risk_level = 'Medium';
      risk_color = 'yellow';
    } else if (risk_score <= 20) {
      risk_level = 'High';
      risk_color = 'orange';
    } else {
      risk_level = 'Critical';
      risk_color = 'red';
    }

    setCalculatedRisk({ max_impact, risk_score, risk_level, risk_color });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);

    try {
      const token = localStorage.getItem('token');

      let url;
      if (consequenceId) {
        // If consequence ID is provided, save assessment for that consequence
        url = `${API_URL}/api/consequences/${consequenceId}/impact-assessment`;
      } else if (deviationId) {
        // Otherwise, use the legacy deviation-based assessment
        url = `${API_URL}/api/deviations/${deviationId}/impact-assessment`;
      } else {
        console.error('Either deviationId or consequenceId must be provided');
        setSaving(false);
        alert('Error: No deviation or consequence specified for risk assessment');
        return;
      }

      const response = await axios.post(
        url,
        formData,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      if (response.status >= 200 && response.status < 300) {
        alert('Impact assessment saved successfully!');
        await loadExistingAssessment();
        onSaved?.();
      } else {
        throw new Error(`Unexpected response status: ${response.status}`);
      }
    } catch (err) {
      console.error('Failed to save impact assessment:', err);
      alert('Failed to save impact assessment. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  const renderImpactSelector = (
    label: string,
    field: keyof typeof formData,
    descriptions: Record<number, string>
  ) => {
    return (
      <div className="space-y-2">
        <label className="block text-sm font-semibold text-gray-700">{label}</label>
        <select
          value={formData[field as keyof typeof formData]}
          onChange={(e) => setFormData({ ...formData, [field]: parseInt(e.target.value) })}
          className="w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
        >
          {Object.entries(descriptions).map(([value, desc]) => (
            <option key={value} value={value}>
              {desc}
            </option>
          ))}
        </select>
      </div>
    );
  };

  if (loading) {
    return <div className="text-center py-8 text-gray-600">Loading assessment...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Header with Current Risk Badge */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">Impact Assessment</h3>
        <div className="flex items-center gap-3">
          <span className="text-sm text-gray-600">Current Risk:</span>
          <RiskBadge riskLevel={calculatedRisk.risk_level} riskScore={calculatedRisk.risk_score} showScore />
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Impact Ratings */}
        <div className="bg-gray-50 rounded-lg p-6 space-y-4">
          <h4 className="font-semibold text-gray-900 mb-4">Impact Ratings (1-5)</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {renderImpactSelector('🏥 Health & Safety', 'safety_impact', IMPACT_DESCRIPTIONS.safety)}
            {renderImpactSelector('💰 Financial', 'financial_impact', IMPACT_DESCRIPTIONS.financial)}
            {renderImpactSelector('🌍 Environmental', 'environmental_impact', IMPACT_DESCRIPTIONS.environmental)}
            {renderImpactSelector('📢 Reputation', 'reputation_impact', IMPACT_DESCRIPTIONS.reputation)}
            {renderImpactSelector('📅 Schedule', 'schedule_impact', IMPACT_DESCRIPTIONS.schedule)}
            {renderImpactSelector('⚙️ Performance', 'performance_impact', IMPACT_DESCRIPTIONS.performance)}
          </div>
        </div>

        {/* Likelihood Rating */}
        <div className="bg-gray-50 rounded-lg p-6 space-y-4">
          <h4 className="font-semibold text-gray-900 mb-4">Likelihood (1-5)</h4>
          {renderImpactSelector('🎲 Probability of Occurrence', 'likelihood', LIKELIHOOD_DESCRIPTIONS)}
        </div>

        {/* Calculated Risk Summary */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 space-y-3">
          <h4 className="font-semibold text-gray-900">Risk Calculation</h4>
          <div className="grid grid-cols-3 gap-4 text-sm">
            <div>
              <div className="text-gray-600">Max Impact</div>
              <div className="text-2xl font-bold text-gray-900">{calculatedRisk.max_impact}</div>
            </div>
            <div>
              <div className="text-gray-600">Likelihood</div>
              <div className="text-2xl font-bold text-gray-900">{formData.likelihood}</div>
            </div>
            <div>
              <div className="text-gray-600">Risk Score</div>
              <div className="text-2xl font-bold text-gray-900">{calculatedRisk.risk_score}</div>
            </div>
          </div>
          <div className="text-xs text-gray-600 mt-2">
            Formula: Risk Score = Likelihood × Max Impact = {formData.likelihood} × {calculatedRisk.max_impact} = {calculatedRisk.risk_score}
          </div>
        </div>

        {/* Risk Matrix Visualization */}
        <div className="mt-6">
          <RiskMatrixViewer
            highlightedCell={{
              likelihood: formData.likelihood,
              severity: calculatedRisk.max_impact
            }}
          />
        </div>

        {/* Assessment Notes */}
        <div className="space-y-2">
          <label className="block text-sm font-semibold text-gray-700">
            Assessment Notes (Optional)
          </label>
          <textarea
            value={formData.assessment_notes}
            onChange={(e) => setFormData({ ...formData, assessment_notes: e.target.value })}
            rows={3}
            className="w-full border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder="Add any notes or justifications for this risk assessment..."
          />
        </div>

        {/* Action Buttons */}
        <div className="flex justify-end gap-3 pt-4 border-t">
          <button
            type="submit"
            disabled={saving}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 font-semibold"
          >
            {saving ? 'Saving...' : existingAssessment ? 'Update Assessment' : 'Save Assessment'}
          </button>
        </div>
      </form>
    </div>
  );
};
