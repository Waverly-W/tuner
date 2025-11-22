import { useAppStore } from '@/store/app'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { FileText } from 'lucide-react'

export function ChapterList() {
    const { currentBook } = useAppStore()

    if (!currentBook) return null

    return (
        <div className="p-2 space-y-1">
            <h3 className="px-2 py-2 text-sm font-semibold text-muted-foreground">Chapters</h3>
            {currentBook.chapters.map((chapter, index) => (
                <Button
                    key={chapter.id}
                    variant="ghost"
                    size="sm"
                    className={cn(
                        "w-full justify-start font-normal truncate",
                        // For now just highlight first one or add selection state later
                        index === 0 && "bg-accent text-accent-foreground"
                    )}
                >
                    <FileText className="mr-2 h-4 w-4 shrink-0" />
                    <span className="truncate">{chapter.title}</span>
                </Button>
            ))}
        </div>
    )
}
