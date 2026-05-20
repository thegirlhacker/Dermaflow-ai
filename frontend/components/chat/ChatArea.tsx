import { useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";
import { Message } from "@/types/chat";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { User, Bot, FileText, ChevronDown } from "lucide-react";

interface ChatAreaProps {
  messages: Message[];
  isLoading: boolean;
}

export function ChatArea({ messages, isLoading }: ChatAreaProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, isLoading]);

  return (
    <ScrollArea className="flex-1 w-full bg-background relative">
      <div className="w-full max-w-3xl mx-auto py-8 px-4 flex flex-col gap-6">
        {messages.length === 0 && (
          <div className="h-full flex flex-col items-center justify-center text-center mt-32 gap-6 animate-in fade-in slide-in-from-bottom-4 duration-1000">
            <div className="p-4 bg-primary/10 rounded-full shadow-inner border border-primary/20">
               <Bot className="w-12 h-12 text-primary" />
            </div>
            <div className="space-y-2">
               <h2 className="text-2xl font-semibold tracking-tight text-foreground">DermaFlow AI</h2>
               <p className="text-muted-foreground max-w-md mx-auto">Your intelligent dermatology assistant. Ask me anything about skin conditions, treatments, or ingredients.</p>
            </div>
          </div>
        )}

        {messages.map((msg) => (
          <div key={msg.id} className="flex gap-4 group animate-in fade-in slide-in-from-bottom-2">
            <Avatar className="w-8 h-8 shrink-0 shadow-sm border border-border">
              {msg.role === "user" ? (
                <AvatarFallback className="bg-secondary text-secondary-foreground"><User className="w-4 h-4" /></AvatarFallback>
              ) : (
                <AvatarFallback className="bg-primary text-primary-foreground"><Bot className="w-4 h-4" /></AvatarFallback>
              )}
            </Avatar>
            <div className="flex-1 flex flex-col gap-2 overflow-hidden mt-1">
              <div className="font-semibold text-sm text-foreground">
                {msg.role === "user" ? "You" : "DermaFlow AI"}
              </div>
              
              <div className="prose prose-sm md:prose-base prose-invert max-w-none text-foreground/90 leading-relaxed">
                <ReactMarkdown>{msg.content}</ReactMarkdown>
              </div>

              {msg.sources && msg.sources.length > 0 && (
                <details className="mt-4 border border-border rounded-xl group/details overflow-hidden bg-card shadow-sm">
                  <summary className="flex items-center gap-2 cursor-pointer p-3 text-sm font-medium hover:bg-muted/50 transition-colors select-none text-muted-foreground">
                    <FileText className="w-4 h-4 text-primary" />
                    <span className="text-foreground">Sources ({msg.sources.length})</span>
                    <ChevronDown className="w-4 h-4 ml-auto transition-transform group-open/details:rotate-180" />
                  </summary>
                  <div className="p-3 bg-muted/30 grid gap-3 border-t border-border">
                    {msg.sources.map((src, i) => (
                      <Card key={i} className="bg-background border-border shadow-sm">
                        <CardHeader className="py-2 px-4 border-b border-border flex flex-row items-center gap-2 bg-muted/20">
                          <Badge variant="outline" className="bg-background border-border text-foreground font-medium">
                            {src.condition.replace("_", " ")}
                          </Badge>
                          <CardTitle className="text-xs font-mono text-muted-foreground truncate max-w-[200px]" title={src.source}>
                            {src.source}
                          </CardTitle>
                          <span className="text-xs text-primary font-medium ml-auto">{(src.score * 100).toFixed(1)}% Match</span>
                        </CardHeader>
                        <CardContent className="p-4 text-sm text-muted-foreground italic leading-relaxed">
                          "{src.preview}..."
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </details>
              )}
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex gap-4 animate-in fade-in">
             <Avatar className="w-8 h-8 shrink-0 shadow-sm border border-border">
                <AvatarFallback className="bg-primary text-primary-foreground"><Bot className="w-4 h-4" /></AvatarFallback>
            </Avatar>
            <div className="flex flex-col gap-2 mt-1">
              <div className="font-semibold text-sm text-foreground">DermaFlow AI</div>
              <div className="flex items-center gap-1.5 mt-2 h-6">
                <div className="w-1.5 h-1.5 rounded-full bg-primary/60 animate-bounce [animation-delay:-0.3s]"></div>
                <div className="w-1.5 h-1.5 rounded-full bg-primary/60 animate-bounce [animation-delay:-0.15s]"></div>
                <div className="w-1.5 h-1.5 rounded-full bg-primary/60 animate-bounce"></div>
              </div>
            </div>
          </div>
        )}
        <div ref={scrollRef} className="h-4" />
      </div>
    </ScrollArea>
  );
}
