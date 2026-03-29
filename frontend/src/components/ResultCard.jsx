import React from 'react';

const ResultCard = ({ title, value, isAdversarial = false, changed = false }) => {
  return (
    <div className={`model-result${changed ? ' tricked' : ''}`}>
      <div className="model-name">{title}</div>
      <div className={`prediction-value${changed ? ' danger' : ''}`}>
        {value}
      </div>
      {isAdversarial && (
        <div className={`result-status ${changed ? 'tricked' : 'resisted'}`}>
          {changed ? 'Tricked' : 'Resisted'}
        </div>
      )}
    </div>
  );
};

export default ResultCard;
