import React, { useRef, useState, useEffect } from 'react';

const DrawingPad = ({ onPredict, onClear, disabled }) => {
  const canvasRef = useRef(null);
  const [isDrawing, setIsDrawing] = useState(false);

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    
    // Fill background with black initially
    ctx.fillStyle = 'black';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Setup drawing settings for drawing a digit like MNIST
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';
    ctx.strokeStyle = 'white';
    ctx.lineWidth = 18; // thick enough to look like a digits brush
  }, []);

  const startDrawing = (e) => {
    if (disabled) return;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    const rect = canvas.getBoundingClientRect();
    const x = (e.clientX || e.touches?.[0].clientX) - rect.left;
    const y = (e.clientY || e.touches?.[0].clientY) - rect.top;

    ctx.beginPath();
    ctx.moveTo(x, y);
    setIsDrawing(true);
  };

  const draw = (e) => {
    if (!isDrawing || disabled) return;
    e.preventDefault();
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    const rect = canvas.getBoundingClientRect();
    const x = (e.clientX || e.touches?.[0].clientX) - rect.left;
    const y = (e.clientY || e.touches?.[0].clientY) - rect.top;

    ctx.lineTo(x, y);
    ctx.stroke();
  };

  const stopDrawing = () => {
    setIsDrawing(false);
  };

  const handleClear = () => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    ctx.fillStyle = 'black';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    if (onClear) onClear();
  };

  const handlePredict = () => {
    const canvas = canvasRef.current;
    const base64Image = canvas.toDataURL('image/png');
    if (onPredict) onPredict(base64Image);
  };

  return (
    <>
      <div className="canvas-container">
        <canvas
          ref={canvasRef}
          width={280}
          height={280}
          onMouseDown={startDrawing}
          onMouseMove={draw}
          onMouseUp={stopDrawing}
          onMouseOut={stopDrawing}
          onTouchStart={startDrawing}
          onTouchMove={draw}
          onTouchEnd={stopDrawing}
        />
      </div>
      <div className="controls">
        <button onClick={handleClear} disabled={disabled}>Clear</button>
        <button className="primary" onClick={handlePredict} disabled={disabled}>Predict</button>
      </div>
    </>
  );
};

export default DrawingPad;
