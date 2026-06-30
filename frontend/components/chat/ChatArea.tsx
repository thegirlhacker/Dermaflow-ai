import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import rehypeRaw from "rehype-raw";
import { Message } from "@/types/chat";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { User, Bot, FileText, ChevronDown, Sparkles } from "lucide-react";

const SKIN_FACTS = [
  "Fun fact: Your skin is your body's largest organ.",
  "Fun fact: You shed about 30,000 to 40,000 skin cells every minute.",
  "Fun fact: Your skin renews itself completely every 28 days.",
  "Fun fact: Melanin gives skin its color and protects against UV rays.",
  "Fun fact: The thickest skin is on your feet, the thinnest on your eyelids."
];

interface ChatAreaProps {
  messages: Message[];
  isLoading: boolean;
}

export function ChatArea({ messages, isLoading }: ChatAreaProps) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [factIndex, setFactIndex] = useState(0);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, isLoading]);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isLoading) {
      setFactIndex(Math.floor(Math.random() * SKIN_FACTS.length));
      interval = setInterval(() => {
        setFactIndex((prev) => (prev + 1) % SKIN_FACTS.length);
      }, 3500);
    }
    return () => clearInterval(interval);
  }, [isLoading]);

  return (
    <div className="flex-1 w-full overflow-y-auto bg-gradient-to-b from-[#faf8f7] to-[#fff] scroll-smooth">
      <div className="w-full max-w-3xl mx-auto py-8 px-4 flex flex-col gap-8 min-h-full">
        {messages.length === 0 && (
          <div className="flex-1 flex flex-col items-center justify-center text-center mt-32 gap-6 animate-in fade-in slide-in-from-bottom-6 duration-1000">
            <div className="p-8 bg-gradient-to-tr from-rose-100 to-pink-50 rounded-full shadow-lg border border-white/60 relative">
              <Sparkles className="w-16 h-16 text-rose-400 animate-pulse" />
              <div className="absolute -top-1 -right-1 w-4 h-4 bg-pink-300 rounded-full blur-sm" />
              <div className="absolute -bottom-1 -left-1 w-6 h-6 bg-rose-200 rounded-full blur-md" />
            </div>
            <div className="space-y-3 max-w-lg">
               <h2 className="text-4xl font-bold tracking-tight text-foreground/90">
                 Hello, how can I help your skin today?
               </h2>
               <p className="text-muted-foreground/80 text-lg font-light leading-relaxed">
                 Ask me anything about skincare, skin conditions, or treatment recommendations.
               </p>
            </div>
          </div>
        )}

        {messages.map((msg) => {
          const isUser = msg.role === "user";
          return (
            <div
              key={msg.id}
              className={`flex gap-4 group animate-in fade-in slide-in-from-bottom-3 duration-300 ${
                isUser ? "flex-row-reverse" : ""
              }`}
            >
              <Avatar
                className={`w-9 h-9 shrink-0 shadow-sm border ${
                  isUser
                    ? "bg-rose-100 border-rose-200 text-rose-700"
                    : "bg-gradient-to-tr from-rose-400 to-pink-400 border-white/40 text-white"
                }`}
              >
                {isUser ? (
                  <AvatarFallback className="bg-rose-100 text-rose-700">
                    <User className="w-4 h-4" />
                  </AvatarFallback>
                ) : (
                  <AvatarFallback className="bg-transparent text-white">
                    <Bot className="w-4 h-4" />
                  </AvatarFallback>
                )}
              </Avatar>

              <div
                className={`flex-1 flex flex-col gap-2 max-w-[85%] ${
                  isUser ? "items-end" : "items-start"
                }`}
              >
                <div className="font-semibold text-xs text-muted-foreground/80 px-1">
                  {isUser ? "You" : "DermaFlow AI"}
                </div>

                <div
                  className={`px-5 py-4 rounded-3xl shadow-sm text-sm md:text-base leading-relaxed overflow-hidden border ${
                    isUser
                      ? "bg-gradient-to-r from-rose-400 to-pink-400 text-white border-rose-300/40 rounded-tr-none"
                      : "bg-white/80 backdrop-blur-md text-foreground border-rose-100/50 rounded-tl-none"
                  }`}
                >
                  <div className={`prose prose-sm md:prose-base max-w-none break-words ${isUser ? "prose-invert text-white" : "prose-rose text-foreground/90"}`}>
                    <ReactMarkdown rehypePlugins={[rehypeRaw]}>{msg.content}</ReactMarkdown>
                  </div>
                </div>

                {!isUser && msg.sources && msg.sources.length > 0 && (
                  <details className="mt-2 w-full border border-rose-100/50 rounded-2xl group/details overflow-hidden bg-white/40 shadow-sm">
                    <summary className="flex items-center gap-2 cursor-pointer p-3.5 text-xs font-semibold hover:bg-rose-50/30 transition-colors select-none text-rose-500">
                      <FileText className="w-4 h-4 text-rose-400" />
                      <span>Medical Sources ({msg.sources.length})</span>
                      <ChevronDown className="w-4 h-4 ml-auto text-rose-400 transition-transform group-open/details:rotate-180" />
                    </summary>
                    <div className="p-3 bg-rose-50/10 grid gap-3 border-t border-rose-100/40">
                      {msg.sources.map((src, i) => (
                        <Card key={i} className="bg-white/80 border-rose-100/40 shadow-sm rounded-xl overflow-hidden">
                          <CardHeader className="py-2.5 px-4 border-b border-rose-50 flex flex-row items-center gap-2 bg-rose-50/20">
                            <Badge variant="outline" className="bg-rose-50/50 border-rose-100 text-rose-700 font-semibold px-2 py-0.5 rounded-full text-[10px]">
                              {src.condition.replace("_", " ")}
                            </Badge>
                            <CardTitle className="text-[10px] font-mono text-muted-foreground/80 truncate max-w-[180px]" title={src.source}>
                              {src.source}
                            </CardTitle>
                            <span className="text-[10px] text-rose-500 font-bold ml-auto bg-rose-50 px-2 py-0.5 rounded-full">
                              {(src.score * 100).toFixed(0)}% Match
                            </span>
                          </CardHeader>
                          <CardContent className="p-3.5 text-xs text-muted-foreground/80 italic leading-relaxed">
                            &quot;{src.preview}...&quot;
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  </details>
                )}
              </div>
            </div>
          );
        })}

        {isLoading && (
          <div className="flex gap-4 animate-in fade-in duration-300">
            <Avatar className="w-9 h-9 shrink-0 shadow-sm border border-rose-200 bg-gradient-to-tr from-rose-400 to-pink-400 text-white">
              <AvatarFallback className="bg-transparent text-white"><Bot className="w-4 h-4" /></AvatarFallback>
            </Avatar>
            <div className="flex-1 flex flex-col gap-2 mt-1">
              <div className="font-semibold text-xs text-muted-foreground/80">DermaFlow AI</div>
              <div className="bg-white/80 border border-rose-100/40 p-4 rounded-3xl rounded-tl-none shadow-sm flex items-center gap-4 max-w-[80%]">
                <div className="flex items-center gap-1.5 h-6">
                  <div className="w-2 h-2 rounded-full bg-rose-400 animate-bounce [animation-delay:-0.3s]"></div>
                  <div className="w-2 h-2 rounded-full bg-rose-400 animate-bounce [animation-delay:-0.15s]"></div>
                  <div className="w-2 h-2 rounded-full bg-rose-400 animate-bounce"></div>
                </div>
                <span key={factIndex} className="text-xs md:text-sm text-muted-foreground/80 italic animate-in fade-in slide-in-from-right-4 duration-500 font-light">
                  {SKIN_FACTS[factIndex]}
                </span>
              </div>
            </div>
          </div>
        )}
        <div ref={scrollRef} className="h-4" />
      </div>
    </div>
  );
}
