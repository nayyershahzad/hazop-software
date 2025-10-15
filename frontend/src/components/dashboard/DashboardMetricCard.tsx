interface DashboardMetricCardProps {
  title: string;
  value: number | string;
  icon: string;
  color: 'blue' | 'green' | 'yellow' | 'red' | 'purple';
  trend?: {
    value: number;
    isPositive: boolean;
  };
  onClick?: () => void;
}

export const DashboardMetricCard = ({ title, value, icon, color, trend, onClick }: DashboardMetricCardProps) => {
  const colorClasses = {
    blue: 'bg-blue-500 text-blue-100',
    green: 'bg-green-500 text-green-100',
    yellow: 'bg-yellow-500 text-yellow-100',
    red: 'bg-red-500 text-red-100',
    purple: 'bg-purple-500 text-purple-100'
  };

  const bgColorClasses = {
    blue: 'bg-blue-50',
    green: 'bg-green-50',
    yellow: 'bg-yellow-50',
    red: 'bg-red-50',
    purple: 'bg-purple-50'
  };

  return (
    <div
      className={`${bgColorClasses[color]} rounded-lg shadow-md p-6 transition-all hover:shadow-lg ${
        onClick ? 'cursor-pointer hover:scale-105' : ''
      }`}
      onClick={onClick}
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-3xl font-bold text-gray-900 mt-2">{value}</p>
          {trend && (
            <p className={`text-sm mt-2 ${trend.isPositive ? 'text-green-600' : 'text-red-600'}`}>
              {trend.isPositive ? '↑' : '↓'} {Math.abs(trend.value)}%
            </p>
          )}
        </div>
        <div className={`${colorClasses[color]} rounded-full p-3 text-2xl`}>
          {icon}
        </div>
      </div>
    </div>
  );
};
