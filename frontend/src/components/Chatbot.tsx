"use client";

import { useState, useEffect, useRef } from "react";
import { Button } from "@/components/ui/button";
import { MessageCircle, X } from "lucide-react";
import { Input } from "./ui/input";
import ChatMessageBubble, {
  type Message,
} from "@/components/ChatMessageBubble";

export default function Chatbot() {
  const [isOpen, setIsOpen] = useState(false);
  const [value, setValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [chatMessages, setChatMessages] = useState<Message[]>([
    { id: 3, text: "How can I assist you today?", from: "bot" },
  ]);

  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatMessages, isLoading]);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    if (!value.trim()) return;

    const userMessage: Message = {
      id: Date.now(),
      text: value,
      from: "user",
    };

    setChatMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    setValue("");

    try {
      const response = await fetch("http://127.0.0.1:5000/ask", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query: value }),
      });

      const data = await response.json();

      const botMessage: Message = {
        id: Date.now() + 1,
        text: data.response || "Sorry, I didn’t understand that.",
        from: "bot",
      };

      setChatMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      const errorMessage: Message = {
        id: Date.now() + 2,
        text: "An error occurred while fetching the response.",
        from: "bot",
      };
      console.error("Error fetching response:", error);
      setChatMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <Button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-4 right-4 z-50 bg-green-600 hover:bg-green-700 rounded-full w-14 h-14 flex items-center justify-center shadow-lg"
      >
        <MessageCircle className="w-6 h-6 text-white" />
      </Button>

      {isOpen && (
        <div className="fixed bottom-20 right-4 w-[320px] h-[450px] bg-white shadow-xl border rounded-lg flex flex-col z-40 overflow-hidden animate-in fade-in slide-in-from-bottom-5">
          <div className="flex items-center justify-between px-4 py-2 border-b bg-muted">
            <span className="font-semibold">Chat</span>
            <button onClick={() => setIsOpen(false)}>
              <X className="w-5 h-5" />
            </button>
          </div>

          <div className="flex-1 overflow-y-auto p-4 text-sm text-muted-foreground space-y-2">
            {chatMessages.map((msg) => (
              <ChatMessageBubble key={msg.id} message={msg} />
            ))}

            {isLoading && (
              <div className="flex items-center space-x-2 text-xs text-gray-500 pl-2">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:-0.3s]" />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce [animation-delay:-0.15s]" />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          <form
            onSubmit={handleSubmit}
            className="p-2 border-t bg-background flex gap-2"
          >
            <Input
              value={value}
              onChange={(e) => setValue(e.target.value)}
              type="text"
              placeholder="Type a message..."
              className="flex-1 border px-3 py-2 rounded text-sm outline-none"
            />
            <Button size="sm" type="submit">
              Send
            </Button>
          </form>
        </div>
      )}
    </>
  );
}
