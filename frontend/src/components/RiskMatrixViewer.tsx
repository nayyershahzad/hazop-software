import { useState } from 'react';

interface RiskMatrixViewerProps {
  highlightedCell?: { likelihood: number; severity: number };
  onCellClick?: (likelihood: number, severity: number) => void;
  compact?: boolean;
}

export const RiskMatrixViewer = ({
  highlightedCell,
  onCellClick,
  compact = false
}: RiskMatrixViewerProps) => {
  const [hoveredCell, setHoveredCell] = useState<{ likelihood: number; severity: number } | null>(null);

  // Risk Matrix: likelihood (rows: 1-5 bottom to top) × severity (columns: 1-5 left to right)
  // Based on screenshot 1.png
  const likelihoodLabels = [
    { value: 5, label: 'Probable', shortLabel: '5' },
    { value: 4, label: 'Highly Likely', shortLabel: '4' },
    { value: 3, label: 'Possible', shortLabel: '3' },
    { value: 2, label: 'Unlikely', shortLabel: '2' },
    { value: 1, label: 'Very Unlikely', shortLabel: '1' }
  ];

  const severityLabels = [
    { value: 1, label: 'Minor (A)', shortLabel: 'A' },
    { value: 2, label: 'Significant (B)', shortLabel: 'B' },
    { value: 3, label: 'Moderate (C)', shortLabel: 'C' },
    { value: 4, label: 'Major (D)', shortLabel: 'D' },
    { value: 5, label: 'Critical (E)', shortLabel: 'E' }
  ];

  // Calculate risk score and get color
  const getRiskInfo = (likelihood: number, severity: number) => {
    const score = likelihood * severity;
    let level = 'Low';
    let color = 'bg-green-400';
    let borderColor = 'border-green-600';

    if (score <= 7) {
      level = 'Low';
      color = 'bg-green-400';
      borderColor = 'border-green-600';
    } else if (score <= 16) {
      level = 'Medium';
      color = 'bg-yellow-300';
      borderColor = 'border-yellow-600';
    } else if (score <= 20) {
      level = 'High';
      color = 'bg-orange-400';
      borderColor = 'border-orange-600';
    } else {
      level = 'Critical';
      color = 'bg-red-500';
      borderColor = 'border-red-700';
    }

    return { score, level, color, borderColor };
  };

  const isHighlighted = (likelihood: number, severity: number) => {
    return highlightedCell?.likelihood === likelihood && highlightedCell?.severity === severity;
  };

  const isHovered = (likelihood: number, severity: number) => {
    return hoveredCell?.likelihood === likelihood && hoveredCell?.severity === severity;
  };

  if (compact) {
    return (
      <div className="inline-flex flex-col gap-0.5 p-2 bg-gray-50 rounded border">
        {likelihoodLabels.map((likelihood) => (
          <div key={likelihood.value} className="flex gap-0.5">
            {severityLabels.map((severity) => {
              const { color, borderColor } = getRiskInfo(likelihood.value, severity.value);
              const highlighted = isHighlighted(likelihood.value, severity.value);

              return (
                <div
                  key={`${likelihood.value}-${severity.value}`}
                  className={`w-4 h-4 ${color} ${highlighted ? `ring-2 ring-blue-600 ${borderColor} border-2` : 'border border-gray-400'}`}
                  title={`L${likelihood.value} × S${severity.value}`}
                />
              );
            })}
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="bg-white p-6 rounded-lg border shadow-sm">
      <h3 className="text-lg font-semibold mb-4 text-gray-900">Risk Matrix (5×5)</h3>

      <div className="overflow-x-auto">
        <table className="border-collapse">
          <thead>
            <tr>
              <th className="p-2 text-xs font-semibold text-gray-600 border">Likelihood ↓<br />Severity →</th>
              {severityLabels.map((sev) => (
                <th key={sev.value} className="p-2 text-xs font-semibold text-gray-600 border min-w-[80px]">
                  {sev.label}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {likelihoodLabels.map((likelihood) => (
              <tr key={likelihood.value}>
                <td className="p-2 text-xs font-semibold text-gray-600 border bg-gray-50">
                  {likelihood.label}
                </td>
                {severityLabels.map((severity) => {
                  const { score, level, color, borderColor } = getRiskInfo(likelihood.value, severity.value);
                  const highlighted = isHighlighted(likelihood.value, severity.value);
                  const hovered = isHovered(likelihood.value, severity.value);

                  return (
                    <td
                      key={`${likelihood.value}-${severity.value}`}
                      className={`p-0 border relative ${
                        onCellClick ? 'cursor-pointer' : ''
                      } ${highlighted ? `ring-4 ring-blue-500 ring-inset ${borderColor} border-4` : ''}`}
                      onClick={() => onCellClick?.(likelihood.value, severity.value)}
                      onMouseEnter={() => setHoveredCell({ likelihood: likelihood.value, severity: severity.value })}
                      onMouseLeave={() => setHoveredCell(null)}
                    >
                      <div
                        className={`${color} p-4 h-full w-full flex flex-col items-center justify-center transition-all ${
                          hovered ? 'opacity-90 scale-105' : 'opacity-75'
                        } ${highlighted ? 'opacity-100' : ''}`}
                      >
                        <div className="text-2xl font-bold text-gray-900">{score}</div>
                        {(highlighted || hovered) && (
                          <div className="text-xs font-semibold text-gray-900 mt-1">{level}</div>
                        )}
                      </div>
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Legend */}
      <div className="mt-6 space-y-2">
        <h4 className="text-sm font-semibold text-gray-700">Risk Levels:</h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 bg-green-400 border border-green-600 rounded"></div>
            <div className="text-sm">
              <div className="font-semibold">Low</div>
              <div className="text-xs text-gray-600">1-7</div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 bg-yellow-300 border border-yellow-600 rounded"></div>
            <div className="text-sm">
              <div className="font-semibold">Medium</div>
              <div className="text-xs text-gray-600">8-16</div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 bg-orange-400 border border-orange-600 rounded"></div>
            <div className="text-sm">
              <div className="font-semibold">High</div>
              <div className="text-xs text-gray-600">17-20</div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 bg-red-500 border border-red-700 rounded"></div>
            <div className="text-sm">
              <div className="font-semibold">Critical</div>
              <div className="text-xs text-gray-600">21-25</div>
            </div>
          </div>
        </div>
      </div>

      {/* Hover Info */}
      {hoveredCell && (
        <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded text-sm">
          <strong>Risk Score:</strong> {getRiskInfo(hoveredCell.likelihood, hoveredCell.severity).score}
          {' '}({getRiskInfo(hoveredCell.likelihood, hoveredCell.severity).level})
          <br />
          <strong>Calculation:</strong> Likelihood ({hoveredCell.likelihood}) × Max Impact ({hoveredCell.severity}) = {getRiskInfo(hoveredCell.likelihood, hoveredCell.severity).score}
        </div>
      )}
    </div>
  );
};
