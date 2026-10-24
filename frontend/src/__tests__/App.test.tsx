import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import App from '../App';
import { api } from '../api/client';

// Mock the API client
vi.mock('../api/client', () => ({
  api: {
    listJobs: vi.fn(),
    createJob: vi.fn(),
    getJob: vi.fn(),
    getJobStatus: vi.fn(),
  },
}));

const mockApi = api as unknown as {
  listJobs: ReturnType<typeof vi.fn>;
  createJob: ReturnType<typeof vi.fn>;
  getJob: ReturnType<typeof vi.fn>;
  getJobStatus: ReturnType<typeof vi.fn>;
};

const mockJobs = [
  {
    id: '123e4567-e89b-12d3-a456-426614174000',
    job_type: 'html_to_video',
    status: 'completed',
    input_html: '<html>Test</html>',
    input_css: null,
    input_json: null,
    width: 1920,
    height: 1080,
    fps: 30,
    duration: 10,
    format: 'mp4',
    output_path: '/videos/test.mp4',
    output_url: '/api/jobs/123/download',
    file_size: 1024000,
    error_message: null,
    progress: 100,
    started_at: '2024-01-01T00:00:00Z',
    completed_at: '2024-01-01T00:01:00Z',
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:01:00Z',
  },
];

describe('App', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders header with navigation', () => {
    mockApi.listJobs.mockResolvedValue({ jobs: [], total: 0, page: 1, page_size: 20 });

    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );

    expect(screen.getByText('Nexus Foundry')).toBeInTheDocument();
    expect(screen.getByText('Jobs')).toBeInTheDocument();
    expect(screen.getByText('Create Job')).toBeInTheDocument();
  });

  it('shows empty state when no jobs', async () => {
    mockApi.listJobs.mockResolvedValue({ jobs: [], total: 0, page: 1, page_size: 20 });

    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('No jobs found')).toBeInTheDocument();
    });
  });

  it('displays job list when jobs exist', async () => {
    mockApi.listJobs.mockResolvedValue({ jobs: mockJobs, total: 1, page: 1, page_size: 20 });

    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('HTML_TO_VIDEO')).toBeInTheDocument();
      expect(screen.getByText('completed')).toBeInTheDocument();
    });
  });

  it('navigates to create job page', async () => {
    mockApi.listJobs.mockResolvedValue({ jobs: [], total: 0, page: 1, page_size: 20 });

    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );

    fireEvent.click(screen.getByText('Create Job'));

    await waitFor(() => {
      expect(screen.getByText('Create Video Generation Job')).toBeInTheDocument();
    });
  });
});
