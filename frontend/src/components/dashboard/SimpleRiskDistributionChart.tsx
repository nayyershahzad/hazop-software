import React from 'react';

interface RiskDistributionChartProps {
  data: {
    critical: number;
    high: number;
    medium: number;
    low: number;
  };
  onRiskClick?: (riskLevel: string) => void;
}

export const RiskDistributionChart = ({ data, onRiskClick }: RiskDistributionChartProps) => {
  const chartData = [
    { name: 'Critical', value: data.critical, color: '#EF4444' },
    { name: 'High', value: data.high, color: '#F59E0B' },
    { name: 'Medium', value: data.medium, color: '#FBBF24' },
    { name: 'Low', value: data.low, color: '#10B981' }
  ].filter(item => item.value > 0);

  const total = data.critical + data.high + data.medium + data.low;

  if (total === 0) {
    return (
      <div className="h-full flex items-center justify-center text-gray-500">
        <div className="text-center">
          <p className="text-lg">No risk assessments yet</p>
          <p className="text-sm">Add impact assessments to see risk distribution</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col items-center justify-center">
      {/* Simple donut chart using CSS */}
      <div className="flex space-x-4 mb-4">
        {chartData.map((item, index) => {
          const percentage = Math.round((item.value / total) * 100);
          return (
            <div
              key={index}
              className="flex flex-col items-center"
              style={{ cursor: onRiskClick ? 'pointer' : 'default' }}
              onClick={() => onRiskClick && onRiskClick(item.name.toLowerCase())}
            >
              <div
                className="w-20 h-20 rounded-full mb-2 flex items-center justify-center chart-circle"
                style={{
                  backgroundColor: item.color,
                  border: '5px solid white',
                  boxShadow: '0 0 0 1px #e5e7eb'
                }}
              >
                <span className="text-white font-bold">{percentage}%</span>
              </div>
              <div className="text-sm font-medium">{item.name}</div>
              <div className="text-xs text-gray-600">{item.value} deviations</div>
            </div>
          );
        })}
      </div>

      {/* Legend */}
      <div className="flex flex-wrap justify-center gap-4 mt-4">
        {chartData.map((item, index) => (
          <div key={`legend-${index}`} className="flex items-center">
            <div
              className="w-4 h-4 mr-2"
              style={{ backgroundColor: item.color }}
            ></div>
            <span className="text-sm">{item.name} ({item.value})</span>
          </div>
        ))}
      </div>
    </div>
  );
};