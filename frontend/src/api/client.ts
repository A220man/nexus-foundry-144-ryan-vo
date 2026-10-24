import axios, { AxiosInstance, AxiosError } from 'axios';
import type { Job, JobCreate, JobListResponse, JobStatusResponse, DownloadResponse, HealthResponse } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 30000,
    });

    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        const message = error.response?.data as { detail?: string } | undefined;
        return Promise.reject(new Error(message?.detail || error.message));
      }
    );
  }

  async healthCheck(): Promise<HealthResponse> {
    const response = await this.client.get<HealthResponse>('/health');
    return response.data;
  }

  async readinessCheck(): Promise<HealthResponse> {
    const response = await this.client.get<HealthResponse>('/health/ready');
    return response.data;
  }

  async createJob(job: JobCreate): Promise<Job> {
    const response = await this.client.post<Job>('/jobs', job);
    return response.data;
  }

  async listJobs(params?: {
    page?: number;
    page_size?: number;
    status_filter?: string;
    job_type_filter?: string;
  }): Promise<JobListResponse> {
    const response = await this.client.get<JobListResponse>('/jobs', { params });
    return response.data;
  }

  async getJob(id: string): Promise<Job> {
    const response = await this.client.get<Job>(`/jobs/${id}`);
    return response.data;
  }

  async getJobStatus(id: string): Promise<JobStatusResponse> {
    const response = await this.client.get<JobStatusResponse>(`/jobs/${id}/status`);
    return response.data;
  }

  async downloadJob(id: string): Promise<DownloadResponse> {
    const response = await this.client.get<DownloadResponse>(`/jobs/${id}/download`);
    return response.data;
  }

  async cancelJob(id: string): Promise<void> {
    await this.client.delete(`/jobs/${id}`);
  }
}

export const api = new ApiClient();
