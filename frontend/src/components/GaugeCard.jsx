import { useEffect, useState } from 'react';

export default function GaugeCard({ label, value, unit, min, max, type, optimalMin, optimalMax }) {
  const [animatedValue, setAnimatedValue] = useState(0);
  const radius = 40;
  const circumference = 2 * Math.PI * radius;
  const normalizedValue = Math.max(0, Math.min(1, (value - min) / (max - min)));
  const offset = circumference - normalizedValue * circumference;

  // Determine if value is in optimal range
  const isOptimal = optimalMin !== undefined && optimalMax !== undefined
    ? value >= optimalMin && value <= optimalMax
    : true;

  useEffect(() => {
    const timer = setTimeout(() => setAnimatedValue(value), 100);
    return () => clearTimeout(timer);
  }, [value]);

  const getColor = () => {
    if (!isOptimal) return '#E74C3C';
    switch (type) {
      case 'ph': return '#2ECC71';
      case 'ec': return '#3498DB';
      case 'temp': return '#E67E22';
      case 'water': return '#1ABC9C';
      default: return '#2ECC71';
    }
  };

  return (
    <div className={`gauge-card ${type}`}>
      <div className="gauge-svg-container">
        <svg className="gauge-svg" viewBox="0 0 100 100">
          <circle className="gauge-bg" cx="50" cy="50" r={radius} />
          <circle
            className={`gauge-fill ${type}`}
            cx="50" cy="50" r={radius}
            style={{
              strokeDasharray: circumference,
              strokeDashoffset: offset,
              stroke: getColor()
            }}
          />
        </svg>
        <div className="gauge-value" style={{ color: getColor() }}>
          {animatedValue}
        </div>
      </div>
      <div className="gauge-label">{label}</div>
      <div className="gauge-unit">{unit}</div>
    </div>
  );
}
