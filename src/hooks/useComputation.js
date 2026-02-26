import { useState, useCallback } from 'react';
import { apiRequest, getComputeConfig } from '../utils/api';

export function useComputation() {
  const [result, setResult] = useState(null);
  const [visualization, setVisualization] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const compute = useCallback(async (integralType, formState) => {
    setLoading(true);
    setError(null);
    setResult(null);
    setVisualization(null);

    try {
      const { endpoint, body } = getComputeConfig(integralType, formState);
      const data = await apiRequest(endpoint, body);
      setResult(data.result || data);
      setVisualization(data.visualization || data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setResult(null);
    setVisualization(null);
    setError(null);
  }, []);

  return { result, visualization, loading, error, compute, reset };
}
