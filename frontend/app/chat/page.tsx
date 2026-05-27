"use client";

import { useChat } from "@/hooks/use-chat";
import { Sidebar } from "@/components/chat/Sidebar";
import { ChatArea } from "@/components/chat/ChatArea";
import { ChatInput } from "@/components/chat/ChatInput";
import { Menu } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useState } from "react";

export default function Home() {
  const {
    sessions,
    currentSessionId,
    setCurrentSessionId,
    messages,
    isLoading,
    handleNewChat,
    sendMessage,
  } = useChat();

  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="flex h-screen w-full bg-background text-foreground overflow-hidden font-sans">
      {/* Mobile Sidebar Overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-background/80 backdrop-blur-sm z-40 md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <div
        className={`fixed inset-y-0 left-0 z-50 transform ${
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        } md:relative md:translate-x-0 transition-transform duration-200 ease-in-out shrink-0`}
      >
        <Sidebar
          sessions={sessions}
          currentSessionId={currentSessionId}
          onSelectSession={(id) => {
            setCurrentSessionId(id);
            setSidebarOpen(false);
          }}
          
          onNewChat={() => {
            handleNewChat();
            setSidebarOpen(false);
          }}
        />
      </div>

      {/* Main Chat Area */}
      <div className="flex flex-col flex-1 min-w-0 h-full relative">
        {/* Mobile Header */}
        <div className="md:hidden flex items-center p-3 border-b border-border bg-background shadow-sm shrink-0">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setSidebarOpen(true)}
            className="text-muted-foreground hover:text-foreground"
          >
            <Menu className="w-5 h-5" />
          </Button>
          <span className="font-semibold ml-2">DermaFlow AI</span>
        </div>

        <div className="flex-1 overflow-hidden flex flex-col min-h-0">
          <ChatArea messages={messages} isLoading={isLoading} />
        </div>
        <div className="shrink-0">
          <ChatInput onSendMessage={sendMessage} isLoading={isLoading} />
        </div>
      </div>
    </div>
  );
}
