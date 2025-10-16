import React from 'react';

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
  const maxCount = Math.max(...data.map(item => item.count));

  return (
    <div className="h-full flex flex-col">
      <div className="flex-grow overflow-x-auto">
        <div className="min-w-max h-full flex items-end space-x-8 px-4">
          {data.map((item, index) => {
            const heightPercentage = (item.count / maxCount) * 100;
            return (
              <div
                key={index}
                className="flex flex-col items-center"
                style={{ height: '100%' }}
              >
                <div
                  className="w-16 rounded-t-lg flex items-end justify-center hover:opacity-80 transition-opacity chart-bar"
                  style={{
                    height: `${Math.max(heightPercentage, 5)}%`,
                    backgroundColor: colors[index % colors.length],
                    cursor: onNodeClick ? 'pointer' : 'default',
                    minHeight: '20px'
                  }}
                  onClick={() => onNodeClick && onNodeClick(item.node_id)}
                >
                  <div className="text-white font-bold py-2">{item.count}</div>
                </div>
                <div className="text-xs font-medium mt-2 rotate-345 max-w-16 truncate" title={item.node_name}>
                  {item.node_name}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Legend */}
      <div className="flex justify-center mt-4 flex-wrap gap-4">
        {data.map((item, index) => (
          <div key={`legend-${index}`} className="flex items-center">
            <div
              className="w-4 h-4 mr-2"
              style={{ backgroundColor: colors[index % colors.length] }}
            ></div>
            <span className="text-xs">{item.node_name}</span>
          </div>
        ))}
      </div>
    </div>
  );
};