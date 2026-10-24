export type JobType = 'html_to_video' | 'scene_render' | 'template_render';
export type JobStatus = 'pending' | 'queued' | 'processing' | 'completed' | 'failed' | 'cancelled';

export interface Job {
  id: string;
  job_type: JobType;
  status: JobStatus;
  input_html: string | null;
  input_css: string | null;
  input_json: Record<string, unknown> | null;
  width: number;
  height: number;
  fps: number;
  duration: number;
  format: string;
  output_path: string | null;
  output_url: string | null;
  file_size: number | null;
  error_message: string | null;
  progress: number;
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface JobCreate {
  job_type?: JobType;
  input_html?: string;
  input_css?: string;
  input_json?: Record<string, unknown>;
  width?: number;
  height?: number;
  fps?: number;
  duration?: number;
  format?: string;
}

export interface JobListResponse {
  jobs: Job[];
  total: number;
  page: number;
  page_size: number;
}

export interface JobStatusResponse {
  id: string;
  status: JobStatus;
  progress: number;
  error_message: string | null;
}

export interface DownloadResponse {
  url: string;
  filename: string;
  size: number | null;
}

export interface HealthResponse {
  status: string;
  service: string;
  version: string;
  database?: string;
}
