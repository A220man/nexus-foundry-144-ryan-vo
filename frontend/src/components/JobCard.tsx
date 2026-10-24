import { Job, JobStatus } from '../types';

interface JobCardProps {
  job: Job;
  onClick?: () => void;
  onCancel?: () => void;
  showActions?: boolean;
}

const statusClasses: Record<JobStatus, string> = {
  pending: 'badge-pending',
  queued: 'badge-queued',
  processing: 'badge-processing',
  completed: 'badge-completed',
  failed: 'badge-failed',
  cancelled: 'badge-cancelled',
};

export function JobCard({ job, onClick, onCancel, showActions = true }: JobCardProps) {
  const formatDate = (dateStr: string) => new Date(dateStr).toLocaleString();

  return (
    <div className="card" style={{ cursor: onClick ? 'pointer' : 'default' }} onClick={onClick}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
        <div>
          <h3 style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: '0.25rem' }}>
            {job.job_type.replace('_', ' ').toUpperCase()}
          </h3>
          <span className={`badge ${statusClasses[job.status]}`}>{job.status}</span>
        </div>
        {showActions && job.status === 'completed' && (
          <a
            href={job.output_url || '#'}
            className="btn btn-primary"
            style={{ fontSize: '0.75rem', padding: '0.375rem 0.75rem' }}
          >
            Download
          </a>
        )}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '1rem', fontSize: '0.875rem', color: '#6b7280' }}>
        <div>
          <div style={{ fontWeight: 500 }}>Resolution</div>
          <div>{job.width}×{job.height}</div>
        </div>
        <div>
          <div style={{ fontWeight: 500 }}>FPS</div>
          <div>{job.fps}</div>
        </div>
        <div>
          <div style={{ fontWeight: 500 }}>Duration</div>
          <div>{job.duration}s</div>
        </div>
        <div>
          <div style={{ fontWeight: 500 }}>Format</div>
          <div>{job.format.toUpperCase()}</div>
        </div>
      </div>

      {job.progress > 0 && job.status !== 'completed' && (
        <div style={{ marginTop: '1rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.25rem', fontSize: '0.875rem' }}>
            <span>Progress</span>
            <span>{job.progress}%</span>
          </div>
          <div style={{ height: '6px', background: '#e5e7eb', borderRadius: '3px', overflow: 'hidden' }}>
            <div
              style={{
                height: '100%',
                width: `${job.progress}%`,
                background: job.status === 'failed' ? '#dc2626' : '#2563eb',
                transition: 'width 0.3s ease',
              }}
            />
          </div>
        </div>
      )}

      {job.error_message && (
        <div className="alert alert-error" style={{ marginTop: '1rem', fontSize: '0.875rem' }}>
          {job.error_message}
        </div>
      )}

      <div style={{ marginTop: '1rem', display: 'flex', justifyContent: 'space-between', fontSize: '0.875rem', color: '#6b7280' }}>
        <span>Created: {formatDate(job.created_at)}</span>
        {job.started_at && <span>Started: {formatDate(job.started_at)}</span>}
        {job.completed_at && <span>Completed: {formatDate(job.completed_at)}</span>}
      </div>

      {showActions && job.status === 'pending' && onCancel && (
        <div style={{ marginTop: '1rem', textAlign: 'right' }}>
          <button className="btn btn-danger" onClick={(e) => { e.stopPropagation(); onCancel(); }} style={{ fontSize: '0.75rem' }}>
            Cancel
          </button>
        </div>
      )}
    </div>
  );
}
