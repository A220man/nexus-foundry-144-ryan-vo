import { useState } from 'react';
import { JobStatus, JobType } from '../types';
import { useJobs, useCancelJob } from '../hooks/useJobs';
import { JobCard } from './JobCard';

export function JobList() {
  const [page, setPage] = useState(1);
  const pageSize = 10;
  const [statusFilter, setStatusFilter] = useState<JobStatus | ''>('');
  const [typeFilter, setTypeFilter] = useState<JobType | ''>('');

  const { jobs, total, loading, error, refetch } = useJobs(page, pageSize, statusFilter, typeFilter);
  const { cancelJob, loading: cancelLoading } = useCancelJob();

  const totalPages = Math.ceil(total / pageSize);

  const handleCancel = async (jobId: string) => {
    if (window.confirm('Are you sure you want to cancel this job?')) {
      const success = await cancelJob(jobId);
      if (success) {
        refetch();
      }
    }
  };

  if (loading) {
    return <div className="loading"><div className="spinner" /></div>;
  }

  if (error) {
    return (
      <div className="card" style={{ textAlign: 'center' }}>
        <div className="alert alert-error">{error}</div>
        <button className="btn btn-primary" onClick={refetch}>Retry</button>
      </div>
    );
  }

  return (
    <div className="card">
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1rem', marginBottom: '1.5rem', alignItems: 'center' }}>
        <h2 style={{ flex: 1 }}>Video Generation Jobs</h2>
        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
          <select
            className="form-input"
            style={{ width: 'auto', minWidth: '150px' }}
            value={statusFilter}
            onChange={(e) => { setStatusFilter(e.target.value as JobStatus); setPage(1); }}
          >
            <option value="">All Statuses</option>
            <option value="pending">Pending</option>
            <option value="queued">Queued</option>
            <option value="processing">Processing</option>
            <option value="completed">Completed</option>
            <option value="failed">Failed</option>
            <option value="cancelled">Cancelled</option>
          </select>
          <select
            className="form-input"
            style={{ width: 'auto', minWidth: '150px' }}
            value={typeFilter}
            onChange={(e) => { setTypeFilter(e.target.value as JobType); setPage(1); }}
          >
            <option value="">All Types</option>
            <option value="html_to_video">HTML to Video</option>
            <option value="scene_render">Scene Render</option>
            <option value="template_render">Template Render</option>
          </select>
        </div>
      </div>

      {jobs.length === 0 ? (
        <div className="empty-state">
          <h3>No jobs found</h3>
          <p>{total === 0 ? 'Create your first video generation job to get started.' : 'Try adjusting your filters.'}</p>
        </div>
      ) : (
        <>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {jobs.map((job) => (
              <JobCard
                key={job.id}
                job={job}
                onCancel={() => handleCancel(job.id)}
              />
            ))}
          </div>

          {totalPages > 1 && (
            <div className="pagination">
              <button
                className="btn btn-secondary"
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
              >
                Previous
              </button>
              <span className="page-info">
                Page {page} of {totalPages} ({total} total)
              </span>
              <button
                className="btn btn-secondary"
                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
              >
                Next
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
