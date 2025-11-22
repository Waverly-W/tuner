import { useAppStore } from '@/store/app'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Wand2 } from 'lucide-react'

export function StructureEditor() {
    const { currentBook, runAnalysis, currentProject } = useAppStore()

    if (!currentBook) return null

    const handleAnalyze = () => {
        if (currentProject) {
            runAnalysis(currentProject.id)
        }
    }

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <div>
                    <h2 className="text-2xl font-bold">Structure & Content</h2>
                    <p className="text-muted-foreground">Review and edit the text before analysis.</p>
                </div>
                <Button onClick={handleAnalyze}>
                    <Wand2 className="mr-2 h-4 w-4" />
                    Run AI Analysis
                </Button>
            </div>

            <div className="space-y-4">
                {currentBook.chapters.map((chapter) => (
                    <Card key={chapter.id} className="p-6">
                        <h3 className="text-xl font-semibold mb-4">{chapter.title}</h3>
                        <div className="space-y-4">
                            {chapter.sentences.map((sentence) => (
                                <div key={sentence.id} className="flex gap-4 items-start group">
                                    <div className="w-12 text-xs text-muted-foreground pt-3 text-right">
                                        {sentence.id.split('_').pop()}
                                    </div>
                                    <Textarea
                                        defaultValue={sentence.text}
                                        className="flex-1 min-h-[2.5rem] resize-y"
                                        rows={1}
                                    />
                                    {sentence.is_noise && (
                                        <Badge variant="destructive" className="shrink-0">Noise</Badge>
                                    )}
                                </div>
                            ))}
                        </div>
                    </Card>
                ))}
            </div>
        </div>
    )
}
