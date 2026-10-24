import { useState, useEffect, useCallback } from 'react';
import { api } from '../api/client';
import type { Job, JobCreate, JobListResponse, JobStatusResponse } from '../types';

export function useJobs(page = 1, pageSize = 20, statusFilter?: string, typeFilter?: string) {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchJobs = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.listJobs({ page, page_size: pageSize, status_filter: statusFilter, job_type_filter: typeFilter });
      setJobs(data.jobs);
      setTotal(data.total);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch jobs');
    } finally {
      setLoading(false);
    }
  }, [page, pageSize, statusFilter, typeFilter]);

  useEffect(() => {
    fetchJobs();
  }, [fetchJobs]);

  return { jobs, total, loading, error, refetch: fetchJobs };
}

export function useJob(id: string | null) {
  const [job, setJob] = useState<Job | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) {
      setJob(null);
      setLoading(false);
      return;
    }

    let cancelled = false;

    const fetchJob = async () => {
      setLoading(true);
      setError(null);
      try {
        const data = await api.getJob(id);
        if (!cancelled) {
          setJob(data);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Failed to fetch job');
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    };

    fetchJob();

    return () => {
      cancelled = true;
    };
  }, [id]);

  return { job, loading, error };
}

export function useJobStatus(id: string | null, interval = 2000) {
  const [status, setStatus] = useState<JobStatusResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) {
      setStatus(null);
      setLoading(false);
      return;
    }

    let cancelled = false;
    let timer: ReturnType<typeof setInterval>;

    const fetchStatus = async () => {
      try {
        const data = await api.getJobStatus(id);
        if (!cancelled) {
          setStatus(data);
          setLoading(false);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : 'Failed to fetch status');
          setLoading(false);
        }
      }
    };

    fetchStatus();
    timer = setInterval(fetchStatus, interval);

    return () => {
      cancelled = true;
      clearInterval(timer);
    };
  }, [id, interval]);

  return { status, loading, error };
}

export function useCreateJob() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const createJob = async (job: JobCreate): Promise<Job | null> => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.createJob(job);
      return data;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create job');
      return null;
    } finally {
      setLoading(false);
    }
  };

  return { createJob, loading, error };
}

export function useCancelJob() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const cancelJob = async (id: string): Promise<boolean> => {
    setLoading(true);
    setError(null);
    try {
      await api.cancelJob(id);
      return true;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to cancel job');
      return false;
    } finally {
      setLoading(false);
    }
  };

  return { cancelJob, loading, error };
}
