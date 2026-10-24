import { useParams, Link } from 'react-router-dom';
import { useJob, useJobStatus } from '../hooks/useJobs';
import { Job, JobStatus } from '../types';

const statusClasses: Record<JobStatus, string> = {
  pending: 'badge-pending',
  queued: 'badge-queued',
  processing: 'badge-processing',
  completed: 'badge-completed',
  failed: 'badge-failed',
  cancelled: 'badge-cancelled',
};

const formatDate = (dateStr: string | null) => dateStr ? new Date(dateStr).toLocaleString() : 'N/A';

export function JobDetail() {
  const { id } = useParams<{ id: string }>();
  const { job, loading, error } = useJob(id || null);
  const { status: liveStatus } = useJobStatus(id || null);

  const displayStatus = liveStatus?.status || job?.status;
  const displayProgress = liveStatus?.progress ?? job?.progress ?? 0;

  if (loading) {
    return <div className="loading"><div className="spinner" /></div>;
  }

  if (error || !job) {
    return (
      <div className="card" style={{ textAlign: 'center', maxWidth: '600px', margin: '0 auto' }}>
        <div className="alert alert-error">{error || 'Job not found'}</div>
        <Link to="/" className="btn btn-primary">Back to Jobs</Link>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: '800px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <div>
          <Link to="/" className="btn btn-secondary" style={{ marginBottom: '1rem', display: 'inline-block' }}>
            ← Back to Jobs
          </Link>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 700 }}>
            {job.job_type.replace('_', ' ').toUpperCase()} Job
          </h1>
        </div>
        <span className={`badge ${statusClasses[displayStatus]}`} style={{ fontSize: '0.875rem', padding: '0.5rem 1rem' }}>
          {displayStatus}
        </span>
      </div>

      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <h2 style={{ marginBottom: '1rem', fontSize: '1.125rem' }}>Input</h2>
        {job.input_html && (
          <div>
            <h3 style={{ fontSize: '0.875rem', fontWeight: 500, marginBottom: '0.5rem', color: '#6b7280' }}>HTML</h3>
            <pre style={{
              background: '#f3f4f6',
              padding: '1rem',
              borderRadius: '6px',
              overflow: 'auto',
              maxHeight: '300px',
              fontSize: '0.75rem',
              lineHeight: 1.5,
            }}>
              {job.input_html}
            </pre>
          </div>
        )}
        {job.input_css && (
          <div style={{ marginTop: '1rem' }}>
            <h3 style={{ fontSize: '0.875rem', fontWeight: 500, marginBottom: '0.5rem', color: '#6b7280' }}>CSS</h3>
            <pre style={{
              background: '#f3f4f6',
              padding: '1rem',
              borderRadius: '6px',
              overflow: 'auto',
              maxHeight: '200px',
              fontSize: '0.75rem',
              lineHeight: 1.5,
            }}>
              {job.input_css}
            </pre>
          </div>
        )}
        {job.input_json && (
          <div style={{ marginTop: '1rem' }}>
            <h3 style={{ fontSize: '0.875rem', fontWeight: 500, marginBottom: '0.5rem', color: '#6b7280' }}>JSON Data</h3>
            <pre style={{
              background: '#f3f4f6',
              padding: '1rem',
              borderRadius: '6px',
              overflow: 'auto',
              maxHeight: '200px',
              fontSize: '0.75rem',
              lineHeight: 1.5,
            }}>
              {JSON.stringify(job.input_json, null, 2)}
            </pre>
          </div>
        )}
      </div>

      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <h2 style={{ marginBottom: '1rem', fontSize: '1.125rem' }}>Settings</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '1rem' }}>
          <div>
            <div style={{ fontWeight: 500, color: '#6b7280', fontSize: '0.875rem' }}>Resolution</div>
            <div>{job.width}×{job.height}</div>
          </div>
          <div>
            <div style={{ fontWeight: 500, color: '#6b7280', fontSize: '0.875rem' }}>FPS</div>
            <div>{job.fps}</div>
          </div>
          <div>
            <div style={{ fontWeight: 500, color: '#6b7280', fontSize: '0.875rem' }}>Duration</div>
            <div>{job.duration}s</div>
          </div>
          <div>
            <div style={{ fontWeight: 500, color: '#6b7280', fontSize: '0.875rem' }}>Format</div>
            <div>{job.format.toUpperCase()}</div>
          </div>
        </div>
      </div>

      {displayProgress > 0 && displayStatus !== 'completed' && (
        <div className="card" style={{ marginBottom: '1.5rem' }}>
          <h2 style={{ marginBottom: '1rem', fontSize: '1.125rem' }}>Progress</h2>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
            <span>Rendering video...</span>
            <span>{displayProgress}%</span>
          </div>
          <div style={{ height: '10px', background: '#e5e7eb', borderRadius: '5px', overflow: 'hidden' }}>
            <div
              style={{
                height: '100%',
                width: `${displayProgress}%`,
                background: displayStatus === 'failed' ? '#dc2626' : '#2563eb',
                transition: 'width 0.3s ease',
              }}
            />
          </div>
        </div>
      )}

      {job.error_message && (
        <div className="card alert alert-error" style={{ marginBottom: '1.5rem' }}>
          <h3 style={{ marginBottom: '0.5rem' }}>Error</h3>
          <p>{job.error_message}</p>
        </div>
      )}

      {displayStatus === 'completed' && job.output_url && (
        <div className="card" style={{ marginBottom: '1.5rem' }}>
          <h2 style={{ marginBottom: '1rem', fontSize: '1.125rem' }}>Output</h2>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1rem', alignItems: 'center' }}>
            <a href={job.output_url} className="btn btn-primary" download>
              Download Video
            </a>
            {job.file_size && (
              <span style={{ color: '#6b7280' }}>
                Size: {(job.file_size / 1024 / 1024).toFixed(2)} MB
              </span>
            )}
          </div>
        </div>
      )}

      <div className="card">
        <h2 style={{ marginBottom: '1rem', fontSize: '1.125rem' }}>Timeline</h2>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', fontSize: '0.875rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: '#6b7280' }}>Created</span>
            <span>{formatDate(job.created_at)}</span>
          </div>
          {job.started_at && (
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: '#6b7280' }}>Started</span>
              <span>{formatDate(job.started_at)}</span>
            </div>
          )}
          {job.completed_at && (
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: '#6b7280' }}>Completed</span>
              <span>{formatDate(job.completed_at)}</span>
            </div>
          )}
          <div style={{ display: 'flex', justifyContent: 'space-between' }}>
            <span style={{ color: '#6b7280' }}>Last Updated</span>
            <span>{formatDate(job.updated_at)}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
