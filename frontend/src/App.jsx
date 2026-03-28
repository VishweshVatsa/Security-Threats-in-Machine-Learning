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
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ image: base64Image }),
      });

      const data = await response.json();
      if (data.status === 'success') {
        setCleanPredictions(data.clean_predictions);
        setAdvPredictions(data.adversarial_predictions);
      } else {
        setError(data.message || 'Failed to predict.');
      }
    } catch (err) {
      setError('Cannot connect to the ML server. Make sure FastAPI is running.');
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
          Demonstrating Machine Learning vulnerabilities by comparing standard predictions
          against adversarial inputs. Draw a digit below to test!
        </p>
      </header>

      <div className="dashboard">
        {/* Left column: Drawing Pad */}
        <div className="glass-card canvas-section">
          <h3>Input</h3>
          <DrawingPad onPredict={handlePredict} onClear={handleClear} disabled={loading} />
        </div>

        {/* Right column: Results */}
        <div className="results-section">
          {/* Clean Predictions */}
          <div className="glass-card">
            {loading && (
              <div className="loading-overlay">
                <div className="spinner"></div>
                Evaluating Models...
              </div>
            )}
            
            <h3>Standard Inference (Clean)</h3>
            {error && <div style={{color: 'var(--danger)', margin: '1rem'}}>{error}</div>}
            
            {!cleanPredictions && !loading && !error && (
              <div className="empty-state">
                Draw a digit and click predict to see how models perform.
              </div>
            )}
            
            {cleanPredictions && (
              <div className="predictions-grid">
                {Object.entries(cleanPredictions).map(([modelName, value]) => (
                  <ResultCard key={`clean-${modelName}`} title={modelName} value={value} />
                ))}
              </div>
            )}
          </div>

          {/* Adversarial Predictions */}
          <div className="glass-card" style={{ borderColor: 'rgba(248, 81, 73, 0.3)' }}>
            <h3>Adversarial Interference</h3>
            <p style={{fontSize: '0.9em', color: 'var(--secondary)', marginBottom: '1rem'}}>
              What happens when our models receive the exact same drawing with mathematically injected epsilon noise?
            </p>
            
             {!advPredictions && !loading && !error && (
              <div className="empty-state" style={{height: '100px'}}>
                Waiting for input...
              </div>
            )}
            
            {advPredictions && cleanPredictions && (
               <div className="predictions-grid">
                {Object.entries(advPredictions).map(([modelName, value]) => {
                  const changed = value !== cleanPredictions[modelName];
                  return (
                    <ResultCard 
                      key={`adv-${modelName}`} 
                      title={modelName} 
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
