import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { ChatSession } from "@/types/chat";
import { Plus, MessageSquare, Settings } from "lucide-react";

interface SidebarProps {
  sessions: ChatSession[];
  currentSessionId: string | null;
  onSelectSession: (id: string) => void;
  onNewChat: () => void;
}

export function Sidebar({ sessions, currentSessionId, onSelectSession, onNewChat }: SidebarProps) {
  return (
    <div className="w-66 bg-white/70 backdrop-blur-xl border-r border-rose-100/60 flex flex-col h-full">
      {/* Brand Header */}
      <div className="p-6 pb-4">
        <h1 className="text-2xl font-bold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-rose-500 to-pink-400">
          DermaFlow AI
        </h1>
      </div>

      {/* New Chat Button */}
      <div className="px-4 mb-4">
        <Button
          onClick={onNewChat}
          className="w-full justify-center gap-2 shadow-md shadow-rose-200/50 hover:shadow-rose-300/60 font-medium bg-gradient-to-r from-rose-400 to-pink-400 hover:from-rose-500 hover:to-pink-500 text-white rounded-2xl py-6 transition-all duration-300 border-0 cursor-pointer"
        >
          <Plus className="w-5 h-5" />
          New Chat
        </Button>
      </div>

      {/* Recents Header */}
      <div className="px-6 py-2">
        <span className="text-[10px] font-bold tracking-wider text-rose-300 uppercase">
          Recent Conversations
        </span>
      </div>

      {/* Sessions list */}
      <ScrollArea className="flex-1 px-3">
        <div className="space-y-2 pb-4">
          {sessions.map((session) => {
            const isActive = currentSessionId === session.session_id;
            return (
              <button
                key={session.session_id}
                onClick={() => onSelectSession(session.session_id)}
                className={`w-full flex items-start gap-3 px-4 py-3 rounded-2xl text-left transition-all duration-300 border cursor-pointer ${
                  isActive
                    ? "bg-rose-50/60 border-rose-100 text-rose-700 shadow-sm font-medium"
                    : "border-transparent text-muted-foreground hover:bg-rose-50/20 hover:text-foreground"
                }`}
              >
                <MessageSquare
                  className={`w-4 h-4 shrink-0 mt-0.5 ${
                    isActive ? "text-rose-500" : "text-rose-300"
                  }`}
                />
                <div className="flex flex-col min-w-0 leading-tight">
                  <span className={`text-sm truncate ${isActive ? "text-rose-900 font-semibold" : "text-foreground/90 font-medium"}`}>
                    {session.title || "New Chat"}
                  </span>
                  {session.preview && (
                    <span className="text-xs text-muted-foreground/80 truncate mt-1">
                      {session.preview}
                    </span>
                  )}
                </div>
              </button>
            );
          })}
        </div>
      </ScrollArea>

      {/* Sidebar Footer with Settings */}
      <div className="p-4 border-t border-rose-50">
        <Button
          variant="ghost"
          className="w-full justify-start gap-3 text-muted-foreground hover:text-rose-600 hover:bg-rose-50/50 rounded-2xl py-5 transition-colors cursor-pointer"
        >
          <Settings className="w-5 h-5 text-rose-300" />
          Settings
        </Button>
      </div>
    </div>
  );
}
