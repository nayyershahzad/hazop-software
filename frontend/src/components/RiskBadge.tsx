interface RiskBadgeProps {
  riskLevel: 'Low' | 'Medium' | 'High' | 'Critical';
  riskScore?: number;
  size?: 'sm' | 'md' | 'lg';
  showScore?: boolean;
}

export const RiskBadge = ({
  riskLevel,
  riskScore,
  size = 'md',
  showScore = false
}: RiskBadgeProps) => {
  // Color mapping based on risk level
  const colorClasses = {
    Low: 'bg-green-100 text-green-800 border-green-300',
    Medium: 'bg-yellow-100 text-yellow-800 border-yellow-300',
    High: 'bg-orange-100 text-orange-800 border-orange-300',
    Critical: 'bg-red-100 text-red-800 border-red-300'
  };

  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5',
    md: 'text-sm px-2.5 py-1',
    lg: 'text-base px-3 py-1.5'
  };

  return (
    <span
      className={`inline-flex items-center gap-1 font-semibold rounded-full border ${
        colorClasses[riskLevel]
      } ${sizeClasses[size]}`}
      title={showScore && riskScore ? `Risk Score: ${riskScore}` : undefined}
    >
      {/* Risk Level Icon */}
      {riskLevel === 'Critical' && <span>⚠️</span>}
      {riskLevel === 'High' && <span>⚡</span>}
      {riskLevel === 'Medium' && <span>⚠</span>}
      {riskLevel === 'Low' && <span>✓</span>}

      {/* Risk Level Text */}
      <span>{riskLevel}</span>

      {/* Optional Risk Score */}
      {showScore && riskScore && (
        <span className="ml-1 opacity-75">({riskScore})</span>
      )}
    </span>
  );
};

// Compact version for lists
export const RiskIndicator = ({
  riskLevel
}: {
  riskLevel: 'Low' | 'Medium' | 'High' | 'Critical'
}) => {
  const colorClasses = {
    Low: 'bg-green-500',
    Medium: 'bg-yellow-500',
    High: 'bg-orange-500',
    Critical: 'bg-red-500'
  };

  return (
    <div
      className={`w-3 h-3 rounded-full ${colorClasses[riskLevel]}`}
      title={`${riskLevel} Risk`}
    />
  );
};
