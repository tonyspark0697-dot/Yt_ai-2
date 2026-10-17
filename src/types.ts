export type PrivacyType = 'private' | 'unlisted' | 'public';

export interface WorkflowRun {
  id: number;
  name: string;
  display_title: string;
  status: 'queued' | 'in_progress' | 'completed' | string;
  conclusion: 'success' | 'failure' | 'cancelled' | 'timed_out' | 'action_required' | null | string;
  html_url: string;
  event: string;
  created_at: string;
  updated_at: string;
  run_number: number;
  actor?: {
    login: string;
    avatar_url: string;
  };
}

export interface UploadedVideo {
  title: string;
  url: string;
  privacy: PrivacyType | string;
  time: string;
}

export interface RepoInfo {
  name: string;
  full_name: string;
  private: boolean;
  default_branch: string;
  html_url: string;
  description?: string;
}

export interface ConnectionConfig {
  repo: string;
  token: string;
}
