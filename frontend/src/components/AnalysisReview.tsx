import { useAppStore } from '@/store/app'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Play, Check, X, User, Smile } from 'lucide-react'
import { cn } from '@/lib/utils'

export function AnalysisReview() {
    const { currentBook, currentProject, runSynthesis } = useAppStore()

    if (!currentBook || !currentProject) return null

    const handleSynthesize = () => {
        runSynthesis(currentProject.id)
    }

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <div>
                    <h2 className="text-2xl font-bold">Analysis Review</h2>
                    <p className="text-muted-foreground">Review AI-detected noise, emotions, and speakers.</p>
                </div>
                <Button onClick={handleSynthesize}>
                    <Play className="mr-2 h-4 w-4" />
                    Start Synthesis
                </Button>
            </div>

            <div className="space-y-4">
                {currentBook.chapters.map((chapter) => (
                    <Card key={chapter.id} className="p-6">
                        <h3 className="text-xl font-semibold mb-4">{chapter.title}</h3>
                        <div className="space-y-2">
                            {chapter.sentences.map((sentence) => (
                                <div
                                    key={sentence.id}
                                    className={cn(
                                        "p-3 rounded-lg border transition-colors flex gap-4 items-start",
                                        sentence.is_noise ? "bg-muted/50 border-transparent opacity-60" : "bg-card border-border"
                                    )}
                                >
                                    {/* Status Icon */}
                                    <div className="mt-1">
                                        {sentence.is_noise ? (
                                            <X className="h-4 w-4 text-muted-foreground" />
                                        ) : (
                                            <Check className="h-4 w-4 text-green-500" />
                                        )}
                                    </div>

                                    {/* Content */}
                                    <div className="flex-1 space-y-2">
                                        <p className={cn("text-sm leading-relaxed", sentence.is_noise && "line-through decoration-muted-foreground")}>
                                            {sentence.text}
                                        </p>

                                        {!sentence.is_noise && (
                                            <div className="flex gap-2">
                                                {/* Speaker Badge */}
                                                <Badge variant="outline" className="gap-1">
                                                    <User className="h-3 w-3" />
                                                    {sentence.metadata?.speaker || 'Narrator'}
                                                </Badge>

                                                {/* Emotion Badge */}
                                                {sentence.metadata?.emotion && (
                                                    <Badge variant="secondary" className="gap-1">
                                                        <Smile className="h-3 w-3" />
                                                        {sentence.metadata.emotion}
                                                    </Badge>
                                                )}
                                            </div>
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </Card>
                ))}
            </div>
        </div>
    )
}
