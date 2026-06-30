import { useState, useRef, useEffect } from "react";
import { Send, Upload, X, Image as ImageIcon } from "lucide-react";
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
  onSendMessage: (query: string, condition: string, image_base64?: string) => void;
  isLoading: boolean;
}

export function ChatInput({ onSendMessage, isLoading }: ChatInputProps) {
  const [query, setQuery] = useState("");
  const [condition, setCondition] = useState("none");
  const [imageBase64, setImageBase64] = useState<string | undefined>();
  const [imageName, setImageName] = useState<string | undefined>();
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
    }
  }, [query]);

  const handleSubmit = (e?: React.FormEvent) => {
    e?.preventDefault();
    if ((!query.trim() && !imageBase64) || isLoading) return;
    onSendMessage(query, condition, imageBase64);
    setQuery("");
    setImageBase64(undefined);
    setImageName(undefined);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setImageName(file.name);
      const reader = new FileReader();
      reader.onloadend = () => {
        setImageBase64(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  return (
    <div className="w-full bg-gradient-to-t from-white via-white/90 to-transparent p-6">
      <form onSubmit={handleSubmit} className="max-w-3xl mx-auto flex flex-col gap-2">
        <div className="flex flex-col bg-white/90 backdrop-blur-md border border-rose-100/50 shadow-xl shadow-rose-100/40 rounded-3xl p-3.5 focus-within:ring-2 focus-within:ring-rose-300 focus-within:border-transparent transition-all duration-300 overflow-hidden relative">
          <Textarea
            ref={textareaRef}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Write your query..."
            className="w-full min-h-[50px] max-h-[200px] resize-none border-0 focus-visible:ring-0 focus-visible:ring-offset-0 bg-transparent text-foreground placeholder:text-muted-foreground/60 text-lg px-2 pb-4 outline-none shadow-none"
            disabled={isLoading}
            rows={1}
          />

          {imageBase64 && (
            <div className="mx-2 mb-3 relative inline-block group">
              <div className="flex items-center gap-2 bg-rose-50/60 text-rose-600 px-3 py-1.5 rounded-xl border border-rose-100/50 w-fit">
                <ImageIcon className="w-4 h-4" />
                <span className="text-sm font-medium truncate max-w-[150px]">{imageName}</span>
                <button
                  type="button"
                  onClick={() => {
                    setImageBase64(undefined);
                    setImageName(undefined);
                    if (fileInputRef.current) fileInputRef.current.value = '';
                  }}
                  className="ml-1 hover:bg-rose-200 p-0.5 rounded-full transition-colors cursor-pointer"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          )}

          <div className="flex items-center justify-between px-2 pt-2 border-t border-rose-50/50">
            <div className="flex items-center gap-3">
              <Select value={condition} onValueChange={(val) => setCondition(val || "none")} disabled={isLoading}>
                <SelectTrigger className="w-[185px] bg-rose-50/40 hover:bg-rose-50 border-rose-100/50 text-rose-600 h-10 rounded-2xl shadow-none transition-colors cursor-pointer focus:ring-0 focus:ring-offset-0">
                  <SelectValue placeholder="Condition (Optional)" />
                </SelectTrigger>
                <SelectContent className="bg-white border border-rose-100 text-foreground rounded-2xl shadow-lg">
                  {CONDITIONS.map((c) => (
                    <SelectItem key={c.value} value={c.value} className="focus:bg-rose-50 focus:text-rose-600 cursor-pointer rounded-xl py-2">
                      {c.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              
              <input 
                type="file" 
                accept="image/*" 
                className="hidden" 
                ref={fileInputRef}
                onChange={handleFileChange}
              />
              <Button
                type="button"
                variant="outline"
                onClick={() => fileInputRef.current?.click()}
                className="h-10 rounded-2xl border-rose-100/50 text-rose-600 bg-white/80 hover:bg-rose-50 hover:text-rose-700 shadow-none transition-all duration-300 gap-2 cursor-pointer"
                disabled={isLoading}
              >
                <Upload className="w-4 h-4" />
                Upload image
              </Button>
            </div>

            <Button
              type="submit"
              size="icon"
              disabled={(!query.trim() && !imageBase64) || isLoading}
              className="h-10 w-10 shrink-0 rounded-2xl bg-gradient-to-r from-rose-400 to-pink-400 hover:from-rose-500 hover:to-pink-500 text-white shadow-md shadow-rose-200 transition-all transform hover:scale-105 duration-300 cursor-pointer border-0"
            >
              <Send className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </form>
    </div>
  );
}
