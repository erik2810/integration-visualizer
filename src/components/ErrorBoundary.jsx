import { Component } from 'react';
import { COLORS } from '../utils/constants';

export class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('ErrorBoundary caught:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          padding: '24px',
          margin: '16px',
          background: `${COLORS.error}15`,
          border: `1px solid ${COLORS.error}40`,
          borderRadius: '12px',
          color: COLORS.error,
          textAlign: 'center',
        }}>
          <h3 style={{ marginBottom: '8px' }}>Something went wrong</h3>
          <p style={{ fontSize: '14px', color: COLORS.textMuted, marginBottom: '16px' }}>
            {this.state.error?.message || 'An unexpected error occurred'}
          </p>
          <button
            onClick={() => this.setState({ hasError: false, error: null })}
            style={{
              padding: '8px 20px',
              background: COLORS.error,
              border: 'none',
              borderRadius: '6px',
              color: '#fff',
              fontSize: '14px',
              cursor: 'pointer',
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
