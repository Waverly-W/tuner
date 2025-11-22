import { useState } from 'react'
import { useAppStore } from '@/store/app'
import { ProjectList } from './components/ProjectList'
import { StudioLayout } from './components/StudioLayout'
import { StructureEditor } from './components/StructureEditor'
import { ChapterList } from './components/ChapterList'
import { AnalysisReview } from './components/AnalysisReview'

function App() {
  const { currentProject } = useAppStore()
  const [currentProjectId, setCurrentProjectId] = useState<string | null>(null)

  return (
    <div className="min-h-screen bg-background text-foreground">
      {currentProjectId ? (
        <StudioLayout
          projectId={currentProjectId}
          onBack={() => setCurrentProjectId(null)}
          sidebar={<ChapterList />}
        >
          <StageRouter />
        </StudioLayout>
      ) : (
        <ProjectList onSelect={setCurrentProjectId} />
      )}
    </div>
  )
}

import { AudioWorkbench } from './components/AudioWorkbench'

function StageRouter() {
  const { currentProject } = useAppStore()
  if (!currentProject) return null

  switch (currentProject.status) {
    case 'analyzed':
      return <AnalysisReview />
    case 'synthesized':
    case 'completed':
      return <AudioWorkbench />
    case 'structured':
    default:
      return <StructureEditor />
  }
}

export default App
