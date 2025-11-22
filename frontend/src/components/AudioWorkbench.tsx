import { useAppStore } from '@/store/app'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Play, RefreshCw, Download } from 'lucide-react'

export function AudioWorkbench() {
    const { currentBook, currentProject } = useAppStore()

    if (!currentBook || !currentProject) return null

    // Mock audio path construction since we don't have a file server yet
    // In real app, backend would serve these files via static mount
    const getAudioUrl = (sentenceId: string) => {
        // This is a placeholder. We need a way to serve these files.
        // For MVP, we might need a static file server in backend.
        return `http://localhost:8002/static/projects/${currentProject.id}/clips/${sentenceId}.wav`
    }

    const handleExport = () => {
        // Trigger download
        // For MVP, we assume the zip is ready at a specific URL
        const url = `http://localhost:8002/static/outputs/${currentProject.id}/${currentProject.name}.zip`
        window.open(url, '_blank')
    }

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <div>
                    <h2 className="text-2xl font-bold">Audio Workbench</h2>
                    <p className="text-muted-foreground">Listen to generated clips and regenerate if needed.</p>
                </div>
                <Button onClick={handleExport}>
                    <Download className="mr-2 h-4 w-4" />
                    Export Audiobook
                </Button>
            </div>

            <div className="space-y-4">
                {currentBook.chapters.map((chapter) => (
                    <Card key={chapter.id} className="p-6">
                        <h3 className="text-xl font-semibold mb-4">{chapter.title}</h3>
                        <div className="space-y-2">
                            {chapter.sentences.map((sentence) => {
                                if (sentence.is_noise) return null

                                return (
                                    <div
                                        key={sentence.id}
                                        className="p-3 rounded-lg border bg-card flex gap-4 items-center"
                                    >
                                        <Button size="icon" variant="outline" className="shrink-0">
                                            <Play className="h-4 w-4" />
                                        </Button>

                                        <div className="flex-1 min-w-0">
                                            <p className="text-sm truncate">{sentence.text}</p>
                                            <div className="flex gap-2 mt-1">
                                                <Badge variant="secondary" className="text-xs">
                                                    {sentence.metadata?.speaker || 'Narrator'}
                                                </Badge>
                                                {sentence.metadata?.emotion && (
                                                    <Badge variant="outline" className="text-xs">
                                                        {sentence.metadata.emotion}
                                                    </Badge>
                                                )}
                                            </div>
                                        </div>

                                        <div className="flex gap-2">
                                            <Button size="sm" variant="ghost">
                                                <RefreshCw className="h-4 w-4" />
                                            </Button>
                                            <div className="w-24 h-8 bg-muted rounded flex items-center justify-center text-xs text-muted-foreground">
                                                Waveform
                                            </div>
                                        </div>
                                    </div>
                                )
                            })}
                        </div>
                    </Card>
                ))}
            </div>
        </div>
    )
}
