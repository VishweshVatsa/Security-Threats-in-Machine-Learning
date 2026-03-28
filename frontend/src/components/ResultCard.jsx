import React from 'react';

const ResultCard = ({ title, value, isAdversarial = false, changed = false }) => {
  return (
    <div className="model-result" style={changed ? { borderColor: 'rgba(248, 81, 73, 0.5)', background: 'rgba(248, 81, 73, 0.05)' } : {}}>
      <div className="model-name">{title}</div>
      <div className="prediction-value" style={changed ? { color: 'var(--danger)' } : {}}>
        {value}
      </div>
      {isAdversarial && (
        <div className="noise-added">
          {changed ? "⚠️ Tricked!" : "🛡️ Resisted"}
        </div>
      )}
    </div>
  );
};

export default ResultCard;
