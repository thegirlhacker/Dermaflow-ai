import { useState, useRef, useEffect } from "react";
import { Send } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

const CONDITIONS = [
  { value: "none", label: "Auto-detect Condition" },
  { value: "acne", label: "Acne" },
  { value: "eczema", label: "Eczema" },
  { value: "psoriasis", label: "Psoriasis" },
  { value: "rosacea", label: "Rosacea" },
  { value: "contact_dermatitis", label: "Contact Dermatitis" },
];

interface ChatInputProps {
  onSendMessage: (query: string, condition: string) => void;
  isLoading: boolean;
}

export function ChatInput({ onSendMessage, isLoading }: ChatInputProps) {
  const [query, setQuery] = useState("");
  const [condition, setCondition] = useState("none");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
    }
  }, [query]);

  const handleSubmit = (e?: React.FormEvent) => {
    e?.preventDefault();
    if (!query.trim() || isLoading) return;
    onSendMessage(query, condition);
    setQuery("");
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="w-full bg-background/80 backdrop-blur-sm border-t border-border p-4">
      <form onSubmit={handleSubmit} className="max-w-3xl mx-auto flex flex-col gap-2">
        <div className="flex flex-col sm:flex-row items-end gap-2 bg-muted/30 p-2 rounded-2xl border border-border focus-within:ring-1 focus-within:ring-ring focus-within:border-ring transition-all shadow-sm">
          <Select value={condition} onValueChange={(val) => setCondition(val || "none")} disabled={isLoading}>
            <SelectTrigger className="w-[180px] bg-background border-border text-foreground h-10 rounded-xl">
              <SelectValue placeholder="Condition" />
            </SelectTrigger>
            <SelectContent className="bg-popover border-border text-popover-foreground rounded-xl">
              {CONDITIONS.map((c) => (
                <SelectItem key={c.value} value={c.value} className="focus:bg-accent focus:text-accent-foreground cursor-pointer rounded-lg">
                  {c.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          
          <Textarea
            ref={textareaRef}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about skin conditions..."
            className="flex-1 min-h-[40px] max-h-[200px] resize-none border-0 focus-visible:ring-0 focus-visible:ring-offset-0 bg-transparent text-foreground placeholder:text-muted-foreground p-2"
            disabled={isLoading}
            rows={1}
          />

          <Button
            type="submit"
            size="icon"
            disabled={!query.trim() || isLoading}
            className="h-10 w-10 shrink-0 rounded-xl transition-all shadow-sm"
          >
            <Send className="w-4 h-4" />
          </Button>
        </div>
        <div className="text-center text-xs text-muted-foreground mt-1 font-medium">
          DermaFlow AI can make mistakes. Always consult a healthcare professional.
        </div>
      </form>
    </div>
  );
}
