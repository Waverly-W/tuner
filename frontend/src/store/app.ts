import { create } from 'zustand'
import { api } from '@/lib/api'
import type { Project, Book } from '@/lib/api'

interface AppState {
  projects: Project[]
  currentProject: Project | null
  currentBook: Book | null
  loading: boolean
  error: string | null
  
  // Actions
  fetchProjects: () => Promise<void>
  createProject: (file: File) => Promise<void>
  loadProject: (id: string) => Promise<void>
  updateBook: (book: Book) => Promise<void>
  runAnalysis: (id: string) => Promise<void>
  runSynthesis: (id: string) => Promise<void>
}

export const useAppStore = create<AppState>((set, get) => ({
  projects: [],
  currentProject: null,
  currentBook: null,
  loading: false,
  error: null,

  fetchProjects: async () => {
    set({ loading: true })
    try {
      const projects = await api.listProjects()
      set({ projects, loading: false })
    } catch (err) {
      set({ error: 'Failed to fetch projects', loading: false })
    }
  },

  createProject: async (file: File) => {
    set({ loading: true })
    try {
      const project = await api.createProject(file)
      set((state) => ({ 
        projects: [project, ...state.projects],
        loading: false 
      }))
    } catch (err) {
      set({ error: 'Failed to create project', loading: false })
    }
  },

  loadProject: async (id: string) => {
    set({ loading: true })
    try {
      const [project, book] = await Promise.all([
        api.getProject(id),
        api.getProjectContent(id)
      ])
      set({ currentProject: project, currentBook: book, loading: false })
    } catch (err) {
      set({ error: 'Failed to load project', loading: false })
    }
  },

  updateBook: async (book: Book) => {
    const { currentProject } = get()
    if (!currentProject) return
    
    // Optimistic update
    set({ currentBook: book })
    
    try {
      await api.updateProjectContent(currentProject.id, book)
    } catch (err) {
      set({ error: 'Failed to save changes' })
      // Revert? For now just show error
    }
  },

  runAnalysis: async (id: string) => {
    set({ loading: true })
    try {
      const project = await api.analyzeProject(id)
      set({ currentProject: project, loading: false })
      // Reload book to get new tags
      await get().loadProject(id)
    } catch (err) {
      set({ error: 'Analysis failed', loading: false })
    }
  },

  runSynthesis: async (id: string) => {
    // This might be async background task
    try {
      const project = await api.synthesizeProject(id)
      set({ currentProject: project })
    } catch (err) {
      set({ error: 'Synthesis failed' })
    }
  }
}))
