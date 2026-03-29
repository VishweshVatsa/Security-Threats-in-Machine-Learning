import React, { useState } from 'react';
import DrawingPad from './components/DrawingPad';
import ResultCard from './components/ResultCard';

function App() {
  const [cleanPredictions, setCleanPredictions] = useState(null);
  const [advPredictions, setAdvPredictions] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handlePredict = async (base64Image) => {
    setLoading(true);
    setError('');
    
    try {
      const response = await fetch('http://127.0.0.1:8000/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image: base64Image }),
      });

      const data = await response.json();
      if (data.status === 'success') {
        setCleanPredictions(data.clean_predictions);
        setAdvPredictions(data.adversarial_predictions);
      } else {
        setError(data.message || 'Prediction failed.');
      }
    } catch (err) {
      setError('Cannot connect to server. Is the API running?');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setCleanPredictions(null);
    setAdvPredictions(null);
    setError('');
  };

  return (
    <div className="app-container">
      <header>
        <h1>MNIST Security Analysis</h1>
        <p className="subtitle">
          Draw a digit to compare model predictions on clean vs adversarial inputs.
        </p>
      </header>

      <div className="dashboard">
        {/* Drawing Pad */}
        <div className="canvas-section">
          <div className="card">
            <div className="section-label">Input</div>
            <DrawingPad onPredict={handlePredict} onClear={handleClear} disabled={loading} />
          </div>
        </div>

        {/* Results */}
        <div className="results-section">
          {/* Clean */}
          <div className="card">
            {loading && (
              <div className="loading-overlay">
                <div className="spinner"></div>
                Running models…
              </div>
            )}

            <div className="results-header">
              <span className="results-title">Clean Predictions</span>
            </div>

            {error && <div style={{color: 'var(--danger)', fontSize: '0.8125rem', marginBottom: '0.75rem'}}>{error}</div>}
            
            {!cleanPredictions && !loading && !error && (
              <div className="empty-state">Draw a digit and click Predict.</div>
            )}
            
            {cleanPredictions && (
              <div className="predictions-grid">
                {Object.entries(cleanPredictions).map(([model, value]) => (
                  <ResultCard key={`clean-${model}`} title={model} value={value} />
                ))}
              </div>
            )}
          </div>

          {/* Adversarial */}
          <div className="card">
            <div className="results-header">
              <span className="results-title">Adversarial Predictions</span>
              <span className="results-badge">+ noise</span>
            </div>
            
            {!advPredictions && !loading && !error && (
              <div className="empty-state">Waiting for input…</div>
            )}
            
            {advPredictions && cleanPredictions && (
              <div className="predictions-grid">
                {Object.entries(advPredictions).map(([model, value]) => {
                  const changed = value !== cleanPredictions[model];
                  return (
                    <ResultCard 
                      key={`adv-${model}`} 
                      title={model} 
                      value={value} 
                      isAdversarial={true}
                      changed={changed}
                    />
                  );
                })}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
