import { useEffect } from 'react'
import { useAppStore } from '@/store/app'
import { Button } from '@/components/ui/button'
import { ScrollArea } from '@/components/ui/scroll-area'
import { Separator } from '@/components/ui/separator'
import { ArrowLeft, Save, Play, Wand2, FileAudio } from 'lucide-react'
import { cn } from '@/lib/utils'

interface StudioLayoutProps {
    projectId: string
    onBack: () => void
    children: React.ReactNode
    sidebar: React.ReactNode
}

export function StudioLayout({ projectId, onBack, children, sidebar }: StudioLayoutProps) {
    const { currentProject, loadProject, loading } = useAppStore()

    useEffect(() => {
        loadProject(projectId)
    }, [projectId])

    if (loading || !currentProject) {
        return <div className="flex h-screen items-center justify-center">Loading Studio...</div>
    }

    const steps = [
        { id: 'structured', label: 'Structure', icon: FileAudio },
        { id: 'analyzed', label: 'Analysis', icon: Wand2 },
        { id: 'synthesized', label: 'Synthesis', icon: Play },
        { id: 'completed', label: 'Export', icon: Save },
    ]

    const currentStepIndex = steps.findIndex(s => s.id === currentProject.status)
    // Fallback if status is draft or unknown
    const activeIndex = currentStepIndex === -1 ? 0 : currentStepIndex

    return (
        <div className="flex h-screen flex-col bg-background">
            {/* Header */}
            <header className="flex h-14 items-center gap-4 border-b px-6 bg-card">
                <Button variant="ghost" size="icon" onClick={onBack}>
                    <ArrowLeft className="h-4 w-4" />
                </Button>
                <div className="flex-1">
                    <h1 className="text-lg font-semibold">{currentProject.name}</h1>
                </div>
                <div className="flex items-center gap-2">
                    {steps.map((step, i) => (
                        <div key={step.id} className={cn("flex items-center gap-2 text-sm",
                            i === activeIndex ? "text-primary font-medium" : "text-muted-foreground"
                        )}>
                            <step.icon className="h-4 w-4" />
                            <span className="hidden sm:inline">{step.label}</span>
                            {i < steps.length - 1 && <Separator orientation="vertical" className="h-4 mx-2" />}
                        </div>
                    ))}
                </div>
            </header>

            {/* Main Content */}
            <div className="flex flex-1 overflow-hidden">
                {/* Sidebar */}
                <aside className="w-64 border-r bg-muted/30 flex flex-col">
                    <ScrollArea className="flex-1">
                        {sidebar}
                    </ScrollArea>
                </aside>

                {/* Editor Area */}
                <main className="flex-1 overflow-auto p-6">
                    <div className="mx-auto max-w-4xl">
                        {children}
                    </div>
                </main>
            </div>
        </div>
    )
}
