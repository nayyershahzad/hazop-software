import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

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
    <ResponsiveContainer width="100%" height="100%">
      <PieChart>
        <Pie
          data={chartData}
          cx="50%"
          cy="50%"
          innerRadius={60}
          outerRadius={100}
          paddingAngle={5}
          dataKey="value"
          onClick={(entry) => onRiskClick && onRiskClick(entry.name.toLowerCase())}
          style={{ cursor: onRiskClick ? 'pointer' : 'default' }}
        >
          {chartData.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={entry.color} />
          ))}
        </Pie>
        <Tooltip
          formatter={(value: number) => [`${value} deviations`, 'Count']}
        />
        <Legend
          verticalAlign="bottom"
          height={36}
          formatter={(value) => {
            const item = chartData.find(d => d.name === value);
            return `${value} (${item?.value})`;
          }}
        />
      </PieChart>
    </ResponsiveContainer>
  );
};
