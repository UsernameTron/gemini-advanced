export interface CommandResult {
  success: boolean;
  output: string;
  type: 'text' | 'image' | 'error' | 'system';
  data?: any;
}

export interface ImageGenerationResult {
  success: boolean;
  images?: string[];
  text?: string;
  sessionId?: string;
  error?: string;
}

export interface EditingSession {
  id: string;
  original: string;
  current: string;
  history: string[];
  prompts: string[];
  timestamp: Date;
}

export interface ImageData {
  id: string;
  path: string;
  sessionId: string;
  timestamp: string;
  metadata: {
    type?: string;
    name?: string;
    size?: number;
    model?: string;
    prompt?: string;
  };
}

export interface AppPreferences {
  apiKey?: string;
  fontSize: string;
  theme: 'green' | 'amber' | 'blue';
  timestamp: string;
}

export interface SessionData {
  timestamp: string;
  terminal: {
    history: string[];
    currentSession: string | null;
  };
  gallery: {
    images: ImageData[];
    selectedImage: ImageData | null;
  };
}

export interface ServerConfig {
  imageEngine: any;
  commandProcessor: any;
}

export interface ApiResponse<T = any> {
  success: boolean;
  result?: T;
  error?: string;
}
