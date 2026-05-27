import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { ChatSession } from "@/types/chat";
import { PlusCircle, MessageSquare } from "lucide-react";

interface SidebarProps {
  sessions: ChatSession[];
  currentSessionId: string | null;
  onSelectSession: (id: string) => void;
  onNewChat: () => void;
}

export function Sidebar({ sessions, currentSessionId, onSelectSession, onNewChat }: SidebarProps) {
  return (
    <div className="w-64 bg-sidebar/95 backdrop-blur-xl border-r border-border flex flex-col h-full">
      <div className="p-4">
        <Button
          onClick={onNewChat}
          className="w-full justify-start gap-2 shadow-sm font-medium"
          variant="default"
        >
          <PlusCircle className="w-4 h-4" />
          New Chat
        </Button>
      </div>

      <ScrollArea className="flex-1 px-3">
        <div className="space-y-1 pb-4">
          {sessions.map((session) => (
            <button
              key={session.session_id}
              onClick={() => onSelectSession(session.session_id)}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-md text-sm text-left transition-all duration-200 ${
                currentSessionId === session.session_id
                  ? "bg-accent text-accent-foreground font-medium shadow-sm"
                  : "text-muted-foreground hover:bg-muted/80 hover:text-foreground"
              }`}
            >
              <MessageSquare className={`w-4 h-4 shrink-0 ${currentSessionId === session.session_id ? 'text-primary' : 'text-muted-foreground'}`} />
              <span className="truncate">{session.title || "Previous Chat"}</span>
            </button>
          ))}
        </div>
      </ScrollArea>
    </div>
  );
}
