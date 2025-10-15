import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

interface DeviationsByNodeChartProps {
  data: Array<{
    node_id: string;
    node_name: string;
    count: number;
  }>;
  onNodeClick?: (nodeId: string) => void;
}

export const DeviationsByNodeChart = ({ data, onNodeClick }: DeviationsByNodeChartProps) => {
  if (!data || data.length === 0) {
    return (
      <div className="h-full flex items-center justify-center text-gray-500">
        <div className="text-center">
          <p className="text-lg">No nodes yet</p>
          <p className="text-sm">Add nodes to see deviation distribution</p>
        </div>
      </div>
    );
  }

  const colors = ['#3B82F6', '#8B5CF6', '#14B8A6', '#F59E0B', '#EF4444', '#10B981'];

  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis
          dataKey="node_name"
          angle={-45}
          textAnchor="end"
          height={80}
          interval={0}
        />
        <YAxis label={{ value: 'Deviations', angle: -90, position: 'insideLeft' }} />
        <Tooltip
          formatter={(value: number) => [`${value} deviations`, 'Count']}
        />
        <Bar
          dataKey="count"
          onClick={(data: any) => {
            if (onNodeClick && data?.payload?.node_id) {
              onNodeClick(data.payload.node_id);
            }
          }}
          style={{ cursor: onNodeClick ? 'pointer' : 'default' }}
        >
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
};
