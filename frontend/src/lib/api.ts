import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8002'

export interface Project {
  id: string
  name: string
  status: 'draft' | 'structured' | 'analyzed' | 'synthesized' | 'completed' | 'failed'
  created_at: string
  updated_at: string
}

export interface Book {
  id: string
  title: string
  author: string
  chapters: Chapter[]
}

export interface Chapter {
  id: string
  title: string
  sentences: Sentence[]
}

export interface Sentence {
  id: string
  text: string
  is_noise: boolean
  speaker?: string
  emotion_vector?: number[]
  metadata: Record<string, any>
}

export const api = {
  // Projects
  listProjects: async () => {
    const res = await axios.get<Project[]>(`${API_URL}/api/projects`)
    return res.data
  },
  
  createProject: async (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    const res = await axios.post<Project>(`${API_URL}/api/projects`, formData)
    return res.data
  },

  getProject: async (id: string) => {
    const res = await axios.get<Project>(`${API_URL}/api/projects/${id}`)
    return res.data
  },

  // Content
  getProjectContent: async (id: string) => {
    const res = await axios.get<Book>(`${API_URL}/api/projects/${id}/content`)
    return res.data
  },

  updateProjectContent: async (id: string, book: Book) => {
    const res = await axios.put<Project>(`${API_URL}/api/projects/${id}/content`, book)
    return res.data
  },

  // Actions
  analyzeProject: async (id: string) => {
    const res = await axios.post<Project>(`${API_URL}/api/projects/${id}/analyze`)
    return res.data
  },

  synthesizeProject: async (id: string) => {
    const res = await axios.post<Project>(`${API_URL}/api/projects/${id}/synthesize`)
    return res.data
  },
  
  checkHealth: async () => {
    const res = await axios.get(`${API_URL}/health`)
    return res.data
  }
}
