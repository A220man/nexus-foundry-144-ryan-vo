import { useState } from 'react';
import { JobCreate } from '../types';
import { useCreateJob } from '../hooks/useJobs';

interface JobFormProps {
  onSuccess?: (jobId: string) => void;
}

export function JobForm({ onSuccess }: JobFormProps) {
  const [formData, setFormData] = useState<JobCreate>({
    job_type: 'html_to_video',
    input_html: '<html><body><h1>Hello Nexus Foundry</h1></body></html>',
    input_css: 'body { font-family: sans-serif; text-align: center; padding: 2rem; }',
    width: 1920,
    height: 1080,
    fps: 30,
    duration: 10,
    format: 'mp4',
  });
  const [errors, setErrors] = useState<Partial<Record<keyof JobCreate, string>>>({});
  const { createJob, loading, error } = useCreateJob();

  const validate = (): boolean => {
    const newErrors: Partial<Record<keyof JobCreate, string>> = {};
    if (!formData.input_html?.trim()) {
      newErrors.input_html = 'HTML content is required';
    }
    if (formData.width && (formData.width < 100 || formData.width > 7680)) {
      newErrors.width = 'Width must be between 100 and 7680';
    }
    if (formData.height && (formData.height < 100 || formData.height > 4320)) {
      newErrors.height = 'Height must be between 100 and 4320';
    }
    if (formData.fps && (formData.fps < 1 || formData.fps > 120)) {
      newErrors.fps = 'FPS must be between 1 and 120';
    }
    if (formData.duration && (formData.duration < 0.1 || formData.duration > 3600)) {
      newErrors.duration = 'Duration must be between 0.1 and 3600 seconds';
    }
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validate()) return;

    const job = await createJob(formData);
    if (job && onSuccess) {
      onSuccess(job.id);
    }
  };

  const handleChange = (field: keyof JobCreate, value: string | number) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: undefined }));
    }
  };

  return (
    <form onSubmit={handleSubmit} className="card" style={{ maxWidth: '700px' }}>
      <h2 style={{ marginBottom: '1.5rem' }}>Create Video Generation Job</h2>

      {error && <div className="alert alert-error">{error}</div>}

      <div className="form-group">
        <label className="form-label">Job Type</label>
        <select
          className="form-input"
          value={formData.job_type}
          onChange={(e) => handleChange('job_type', e.target.value)}
        >
          <option value="html_to_video">HTML to Video</option>
          <option value="scene_render">Scene Render</option>
          <option value="template_render">Template Render</option>
        </select>
      </div>

      <div className="form-group">
        <label className="form-label">HTML Content *</label>
        <textarea
          className="form-input form-textarea"
          value={formData.input_html || ''}
          onChange={(e) => handleChange('input_html', e.target.value)}
          placeholder="Enter HTML content..."
        />
        {errors.input_html && <span style={{ color: '#dc2626', fontSize: '0.75rem' }}>{errors.input_html}</span>}
      </div>

      <div className="form-group">
        <label className="form-label">CSS (Optional)</label>
        <textarea
          className="form-input form-textarea"
          value={formData.input_css || ''}
          onChange={(e) => handleChange('input_css', e.target.value)}
          placeholder="Enter CSS styles..."
          style={{ minHeight: '80px' }}
        />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '1rem' }}>
        <div className="form-group">
          <label className="form-label">Width</label>
          <input
            type="number"
            className="form-input"
            value={formData.width}
            onChange={(e) => handleChange('width', parseInt(e.target.value) || 0)}
            min={100}
            max={7680}
          />
          {errors.width && <span style={{ color: '#dc2626', fontSize: '0.75rem' }}>{errors.width}</span>}
        </div>

        <div className="form-group">
          <label className="form-label">Height</label>
          <input
            type="number"
            className="form-input"
            value={formData.height}
            onChange={(e) => handleChange('height', parseInt(e.target.value) || 0)}
            min={100}
            max={4320}
          />
          {errors.height && <span style={{ color: '#dc2626', fontSize: '0.75rem' }}>{errors.height}</span>}
        </div>

        <div className="form-group">
          <label className="form-label">FPS</label>
          <input
            type="number"
            className="form-input"
            value={formData.fps}
            onChange={(e) => handleChange('fps', parseInt(e.target.value) || 0)}
            min={1}
            max={120}
          />
          {errors.fps && <span style={{ color: '#dc2626', fontSize: '0.75rem' }}>{errors.fps}</span>}
        </div>

        <div className="form-group">
          <label className="form-label">Duration (s)</label>
          <input
            type="number"
            step="0.1"
            className="form-input"
            value={formData.duration}
            onChange={(e) => handleChange('duration', parseFloat(e.target.value) || 0)}
            min={0.1}
            max={3600}
          />
          {errors.duration && <span style={{ color: '#dc2626', fontSize: '0.75rem' }}>{errors.duration}</span>}
        </div>

        <div className="form-group">
          <label className="form-label">Format</label>
          <select
            className="form-input"
            value={formData.format}
            onChange={(e) => handleChange('format', e.target.value)}
          >
            <option value="mp4">MP4</option>
            <option value="webm">WebM</option>
          </select>
        </div>
      </div>

      <div style={{ marginTop: '1.5rem', display: 'flex', gap: '1rem' }}>
        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? 'Creating...' : 'Create Job'}
        </button>
        <button type="button" className="btn btn-secondary" onClick={() => setFormData({
          job_type: 'html_to_video',
          input_html: '<html><body><h1>Hello Nexus Foundry</h1></body></html>',
          input_css: 'body { font-family: sans-serif; text-align: center; padding: 2rem; }',
          width: 1920,
          height: 1080,
          fps: 30,
          duration: 10,
          format: 'mp4',
        })} disabled={loading}>
          Reset
        </button>
      </div>
    </form>
  );
}
