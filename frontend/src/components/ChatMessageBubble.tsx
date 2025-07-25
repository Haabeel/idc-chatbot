"use client";

import React from "react";
import { User } from "lucide-react";
import { cn } from "@/lib/utils";

export type Message = {
	id: string | number;
	text: string;
	from: "user" | "bot";
	type?: "initial";
	suggestions?: string[];
};

interface ChatMessageBubbleProps {
	message: Message;
	onSuggestionClick?: (suggestion: string) => void;
}

const ChatMessageBubble: React.FC<ChatMessageBubbleProps> = ({
	message,
	onSuggestionClick,
}) => {
	const isUser = message.from === "user";

	return (
		<div
			className={cn(
				"flex w-full items-end mb-3",
				isUser ? "justify-end" : "justify-start"
			)}
		>
			{!isUser && (
				<div className="w-9 h-9 mr-2 rounded-full flex items-center justify-center bg-gradient-to-br from-blue-500 to-purple-500 text-white shadow-lg flex-shrink-0">
					<img
						src="/idc-bot.png"
						alt="IDC Bot"
						className="size-full rounded-full"
					/>
				</div>
			)}

			<div
				className={cn(
					"max-w-[85%] px-4 py-3 rounded-2xl shadow backdrop-blur-md relative",
					isUser
						? "bg-white/60 text-right text-gray-900 rounded-br-md"
						: "bg-gradient-to-br from-blue-200/80 to-purple-200/70 text-gray-900 rounded-bl-md"
				)}
			>
				{/* Render the main text, preserving line breaks */}
				<p className="whitespace-pre-line">{message.text}</p>

				{/* Conditionally render suggestion buttons */}
				{message.type === "initial" && message.suggestions && (
					<div className="mt-3 pt-3 border-t border-black/10 flex flex-col items-start gap-2">
						{message.suggestions.map((suggestion, index) => (
							<button
								key={index}
								onClick={() => onSuggestionClick?.(suggestion)}
								className="w-full text-left text-sm text-blue-800 bg-white/40 hover:bg-white/70 transition-colors p-2 rounded-lg"
							>
								{suggestion}
							</button>
						))}
					</div>
				)}
			</div>

			{isUser && (
				<div className="w-9 h-9 ml-2 rounded-full flex items-center justify-center bg-gray-200 text-gray-700 shadow flex-shrink-0">
					<User className="w-5 h-5" />
				</div>
			)}
		</div>
	);
};

export default ChatMessageBubble;
