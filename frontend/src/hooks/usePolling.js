import { useState, useEffect, useRef } from 'react';
import { evaluationsAPI } from '../services/api';

// Polls evaluation status every 3 seconds until completed or failed
export function useEvaluationPolling(evaluationId, enabled = true) {
  const [evaluation, setEvaluation]   = useState(null);
  const [isComplete, setIsComplete]   = useState(false);
  const [isLoading,  setIsLoading]    = useState(true);
  const [error,      setError]        = useState(null);
  const intervalRef = useRef(null);

  useEffect(() => {
    if (!evaluationId || !enabled) return;

    const poll = async () => {
      try {
        const response = await evaluationsAPI.getOne(evaluationId);
        const data = response.data;
        setEvaluation(data);
        setIsLoading(false);

        if (['completed', 'failed'].includes(data.status?.toLowerCase())) {
          setIsComplete(true);
          if (intervalRef.current) {
            clearInterval(intervalRef.current);
          }
        }
      } catch (err) {
        setError('Failed to fetch evaluation status.');
        setIsLoading(false);
      }
    };

    // Poll immediately, then every 3 seconds
    poll();
    intervalRef.current = setInterval(poll, 3000);

    // Cleanup on unmount
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [evaluationId, enabled]);

  return { evaluation, isComplete, isLoading, error };
}