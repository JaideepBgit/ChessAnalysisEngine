import React from 'react';

class ThreeJSErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('3D Visualization Error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          width: '100%',
          height: '500px',
          background: 'linear-gradient(135deg, #1a1a2e 0%, #2a2a3e 100%)',
          borderRadius: '12px',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '40px',
          border: '2px solid #4a9eff',
          color: '#fff'
        }}>
          <div style={{ fontSize: '48px', marginBottom: '20px' }}>🎲</div>
          <h3 style={{ margin: '0 0 10px 0', color: '#4a9eff' }}>3D Visualization Unavailable</h3>
          <p style={{ 
            textAlign: 'center', 
            color: '#888', 
            maxWidth: '400px',
            lineHeight: '1.6',
            fontSize: '14px'
          }}>
            The 3D visualization couldn't load. This might be due to browser compatibility or WebGL support.
            Please use the 2D view instead.
          </p>
          <button
            onClick={() => this.setState({ hasError: false })}
            style={{
              marginTop: '20px',
              padding: '10px 20px',
              background: '#4a9eff',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: '600'
            }}
          >
            Try Again
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ThreeJSErrorBoundary;
