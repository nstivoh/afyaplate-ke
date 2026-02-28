"use client"

import { PieChart, Pie, Cell, ResponsiveContainer, Legend } from 'recharts';
import { MacroNutrients } from '@/types/planner';

interface MacroChartProps {
  macros: MacroNutrients;
}

const COLORS = ['#008000', '#FF8042', '#FFBB28']; // Green for Protein, Orange for Carbs, Yellow for Fat

const RADIAN = Math.PI / 180;
const renderCustomizedLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent }: any) => {
  const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
  const x = cx + radius * Math.cos(-midAngle * RADIAN);
  const y = cy + radius * Math.sin(-midAngle * RADIAN);

  return (
    <text x={x} y={y} fill="white" textAnchor={x > cx ? 'start' : 'end'} dominantBaseline="central">
      {`${(percent * 100).toFixed(0)}%`}
    </text>
  );
};


export function MacroChart({ macros }: MacroChartProps) {
  const data = [
    { name: 'Protein', value: macros.protein_g },
    { name: 'Carbs', value: macros.carbs_g },
    { name: 'Fat', value: macros.fat_g },
  ];

  return (
    <ResponsiveContainer width="100%" height={300}>
      <PieChart>
        <Pie
          data={data}
          cx="50%"
          cy="50%"
          labelLine={false}
          label={renderCustomizedLabel}
          outerRadius={100}
          fill="#8884d8"
          dataKey="value"
        >
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
          ))}
        </Pie>
        <Legend />
      </PieChart>
    </ResponsiveContainer>
  );
}
