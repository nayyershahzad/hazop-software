import { useState } from 'react';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface SafeguardEffectiveness {
  confidence_score: number;
  effectiveness_score: number;
  reasoning: string;
  improvement_suggestions?: string;
  before_risk_level?: string;
  after_risk_level?: string;
}

interface SafeguardEffectivenessEvaluatorProps {
  safeguardId: string;
  safeguardDescription: string;
  onUpdateSafeguard?: (effectiveness: string) => void;
}

export const SafeguardEffectivenessEvaluator = ({
  safeguardId,
  safeguardDescription,
  onUpdateSafeguard
}: SafeguardEffectivenessEvaluatorProps) => {
  const [isLoading, setIsLoading] = useState(false);
  const [evaluation, setEvaluation] = useState<SafeguardEffectiveness | null>(null);
  const [showEvaluation, setShowEvaluation] = useState(false);

  const evaluateEffectiveness = async () => {
    setIsLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        `${API_URL}/api/gemini/evaluate-safeguard-effectiveness`,
        { safeguard_id: safeguardId },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setEvaluation(response.data);
      setShowEvaluation(true);
    } catch (err) {
      console.error('Failed to evaluate safeguard effectiveness:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const getEffectivenessColor = (score: number) => {
    if (score >= 0.8) return 'text-green-700';
    if (score >= 0.5) return 'text-yellow-700';
    return 'text-red-700';
  };

  const getEffectivenessLabel = (score: number) => {
    if (score >= 0.8) return 'High';
    if (score >= 0.5) return 'Medium';
    return 'Low';
  };

  const updateSafeguardEffectiveness = () => {
    if (evaluation && onUpdateSafeguard) {
      onUpdateSafeguard(getEffectivenessLabel(evaluation.effectiveness_score));
    }
  };

  return (
    <div className="mt-1">
      {!showEvaluation ? (
        <button
          onClick={evaluateEffectiveness}
          disabled={isLoading}
          className="text-xs text-blue-600 hover:text-blue-800 flex items-center gap-1"
        >
          {isLoading ? (
            <>
              <div className="animate-spin h-3 w-3 border border-blue-600 border-t-transparent rounded-full"></div>
              <span>Evaluating...</span>
            </>
          ) : (
            <>
              <span>🤖</span>
              <span>Evaluate effectiveness</span>
            </>
          )}
        </button>
      ) : evaluation ? (
        <div className="mt-2 text-xs border border-blue-100 rounded-lg bg-blue-50 p-2">
          <div className="mb-2">
            <div className="flex justify-between items-center mb-1">
              <div className="font-semibold">
                AI Effectiveness Evaluation
              </div>
              <button
                onClick={() => setShowEvaluation(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                ✕
              </button>
            </div>

            {/* Progress bars */}
            <div className="space-y-2 mt-2">
              <div>
                <div className="flex justify-between mb-1">
                  <span>Effectiveness:</span>
                  <span className={getEffectivenessColor(evaluation.effectiveness_score)}>
                    {getEffectivenessLabel(evaluation.effectiveness_score)} ({Math.round(evaluation.effectiveness_score * 100)}%)
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-1.5">
                  <div
                    className={`h-1.5 rounded-full ${
                      evaluation.effectiveness_score >= 0.8 ? 'bg-green-600' :
                      evaluation.effectiveness_score >= 0.5 ? 'bg-yellow-500' : 'bg-red-600'
                    }`}
                    style={{ width: `${evaluation.effectiveness_score * 100}%` }}
                  ></div>
                </div>
              </div>

              <div>
                <div className="flex justify-between mb-1">
                  <span>Confidence:</span>
                  <span>{Math.round(evaluation.confidence_score * 100)}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-1.5">
                  <div
                    className="bg-blue-600 h-1.5 rounded-full"
                    style={{ width: `${evaluation.confidence_score * 100}%` }}
                  ></div>
                </div>
              </div>
            </div>

            {/* Risk reduction */}
            {evaluation.before_risk_level && evaluation.after_risk_level && (
              <div className="mt-2">
                <div className="font-medium">Risk Reduction:</div>
                <div className="flex items-center mt-1">
                  <span className={`inline-block px-2 py-0.5 text-white rounded ${
                    evaluation.before_risk_level === 'Critical' ? 'bg-red-700' :
                    evaluation.before_risk_level === 'High' ? 'bg-red-600' :
                    evaluation.before_risk_level === 'Medium' ? 'bg-yellow-500' :
                    'bg-green-600'
                  }`}>{evaluation.before_risk_level}</span>
                  <span className="mx-2">→</span>
                  <span className={`inline-block px-2 py-0.5 text-white rounded ${
                    evaluation.after_risk_level === 'Critical' ? 'bg-red-700' :
                    evaluation.after_risk_level === 'High' ? 'bg-red-600' :
                    evaluation.after_risk_level === 'Medium' ? 'bg-yellow-500' :
                    'bg-green-600'
                  }`}>{evaluation.after_risk_level}</span>
                </div>
              </div>
            )}

            {/* Reasoning */}
            <div className="mt-2">
              <div className="font-medium">Analysis:</div>
              <p className="mt-1 text-gray-700">{evaluation.reasoning}</p>
            </div>

            {/* Improvement suggestions */}
            {evaluation.improvement_suggestions && (
              <div className="mt-2">
                <div className="font-medium">Improvement Suggestions:</div>
                <p className="mt-1 text-gray-700">{evaluation.improvement_suggestions}</p>
              </div>
            )}

            {/* Action button */}
            {onUpdateSafeguard && (
              <div className="mt-2">
                <button
                  onClick={updateSafeguardEffectiveness}
                  className="w-full text-xs bg-blue-600 text-white px-2 py-1 rounded hover:bg-blue-700"
                >
                  Update Safeguard Effectiveness
                </button>
              </div>
            )}
          </div>
        </div>
      ) : null}
    </div>
  );
};