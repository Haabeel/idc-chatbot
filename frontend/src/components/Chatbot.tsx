"use client";

import { useState, useEffect, useRef } from "react";
import { Button } from "@/components/ui/button";
import { MessageCircle, X } from "lucide-react";
import { Input } from "./ui/input";
import ChatMessageBubble, {
	type Message,
} from "@/components/ChatMessageBubble"; // Adjust path if needed

export default function Chatbot() {
	const [isOpen, setIsOpen] = useState(false);
	const [value, setValue] = useState("");
	const [isLoading, setIsLoading] = useState(false);

	// State for user verification
	const [isVerified, setIsVerified] = useState(false);
	const [userName, setUserName] = useState("");
	const [userEmail, setUserEmail] = useState("");

	const [chatMessages, setChatMessages] = useState<Message[]>([]);
	const messagesEndRef = useRef<HTMLDivElement | null>(null);

	useEffect(() => {
		messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
	}, [chatMessages, isLoading]);

	// Function to initialize the chat *after* verification
	const startChat = () => {
		setChatMessages([
			{
				id: 1,
				from: "bot",
				type: "initial",
				text: `Hi ${userName}, I’m IDC Bot – your digital guide to IDC Technologies.\n\nHow can I help you today?`,
				suggestions: [
					"What are IDC’s capabilities & service areas?",
					"Show me industry-specific solutions.",
					"Tell me about client success stories.",
					"How can I request a proposal?",
				],
			},
		]);
	};

	const sendMessage = async (messageText: string) => {
		if (!messageText.trim()) return;

		const userMessage: Message = {
			id: Date.now(),
			text: messageText,
			from: "user",
		};

		setChatMessages(prev => [...prev, userMessage]);
		setIsLoading(true);

		try {
			const response = await fetch("http://127.0.0.1:5000/ask", {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				// Include user details in the request body
				body: JSON.stringify({
					query: messageText,
					user: { name: userName, email: userEmail },
				}),
			});
			const data = await response.json();
			const botMessage: Message = {
				id: Date.now() + 1,
				text: data.response || "Sorry, I didn’t understand that.",
				from: "bot",
			};
			setChatMessages(prev => [...prev, botMessage]);
		} catch (error) {
			console.error("Error fetching response:", error);
			const errorMessage: Message = {
				id: Date.now() + 2,
				text: "An error occurred while fetching the response.",
				from: "bot",
			};
			setChatMessages(prev => [...prev, errorMessage]);
		} finally {
			setIsLoading(false);
		}
	};

	const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
		e.preventDefault();
		sendMessage(value);
		setValue("");
	};

	const handleSuggestionClick = (suggestion: string) => {
		sendMessage(suggestion);
	};

	// Handler for the verification form
	const handleVerificationSubmit = (e: React.FormEvent<HTMLFormElement>) => {
		e.preventDefault();
		if (userName.trim() && userEmail.trim()) {
			setIsVerified(true);
			startChat(); // Initialize chat messages after verification
		}
	};

	return (
		<>
			<Button
				onClick={() => setIsOpen(!isOpen)}
				className="fixed bottom-4 right-4 z-50 bg-gradient-to-tr from-blue-600 to-purple-500  hover:scale-105 rounded-full size-12 flex items-center justify-center shadow-2xl transition-transform duration-200 ease-in-out"
				aria-label="Open chat"
			>
				<MessageCircle className="w-7 h-7 text-white drop-shadow-lg" />
			</Button>

			{isOpen && (
				<div className="fixed bottom-24 right-6 w-[360px] h-[520px] z-50">
					<div
						className="flex flex-col h-full rounded-lg border-none shadow-2xl overflow-hidden backdrop-blur-xl"
						style={{ border: "none", boxShadow: "0 16px 48px 0 #4f51d550" }}
					>
						<div className="flex items-center justify-between px-5 py-3 bg-gradient-to-tr from-blue-600/50 to-purple-500/50 backdrop-blur-sm border-b border-white/20">
							<span className="font-semibold text-gray-800 text-lg">
								Ask IDC
							</span>
							<button
								onClick={() => setIsOpen(false)}
								aria-label="Close chat"
								className="cursor-pointer"
							>
								<X className="w-5 h-5 text-gray-700" />
							</button>
						</div>

						{/* --- CONDITIONAL UI: Verification Form or Chat --- */}
						{isVerified ? (
							<>
								{/* Chat Area */}
								<div className="flex-1 overflow-y-auto p-5 text-sm space-y-4">
									{chatMessages.map(msg => (
										<ChatMessageBubble
											key={msg.id}
											message={msg}
											onSuggestionClick={handleSuggestionClick}
										/>
									))}
									{isLoading && (
										<div className="flex items-center gap-1 text-xs text-purple-600 pl-12 pt-2">
											<span className="animate-bounce w-2 h-2 bg-purple-300 rounded-full"></span>
											<span className="animate-bounce w-2 h-2 bg-purple-300 rounded-full [animation-delay:0.15s]"></span>
											<span className="animate-bounce w-2 h-2 bg-purple-300 rounded-full [animation-delay:0.3s]"></span>
										</div>
									)}
									<div ref={messagesEndRef}></div>
								</div>

								{/* Chat Input Form */}
								<form
									onSubmit={handleSubmit}
									className="p-3 bg-white/40 backdrop-blur-md border-t border-white/30 flex gap-2"
								>
									<Input
										value={value}
										onChange={e => setValue(e.target.value)}
										type="text"
										placeholder="Type a message..."
										className="flex-1 bg-white/60 border-none px-4 py-2 rounded-sm text-sm outline-none focus:ring-2 focus:ring-blue-400"
									/>
									<Button
										size="sm"
										type="submit"
										disabled={isLoading}
										className="bg-gradient-to-tr from-blue-500 to-purple-500 text-white hover:bg-purple-600 px-4 rounded-sm h-full shadow"
									>
										Send
									</Button>
								</form>
							</>
						) : (
							<>
								{/* Verification Form */}
								<div className="flex-1 flex flex-col justify-center p-6 text-gray-800">
									<h2 className="text-xl font-bold mb-2 text-center">
										Welcome!
									</h2>
									<p className="text-sm mb-6 text-center text-gray-800/80">
										Please enter your details to start chatting with IDC bot.
									</p>
									<form
										onSubmit={handleVerificationSubmit}
										className="flex flex-col gap-4"
									>
										<Input
											type="text"
											placeholder="Your Name"
											value={userName}
											onChange={e => setUserName(e.target.value)}
											required
											className="bg-gray-800/30 border-gray-700/40 placeholder:text-white/70 text-gray-800 rounded-lg focus:ring-2 focus:ring-white"
										/>
										<Input
											type="email"
											placeholder="Your Email"
											value={userEmail}
											onChange={e => setUserEmail(e.target.value)}
											required
											className="bg-gray-800/30 border-gray-700/40 placeholder:text-white/70 text-gray-800 rounded-lg focus:ring-2 focus:ring-white"
										/>
										<Button
											type="submit"
											className="bg-blue-800 text-white font-bold hover:bg-blue-700 cursor-pointer mt-2 rounded-lg py-2"
										>
											Start Chat
										</Button>
									</form>
								</div>
							</>
						)}
					</div>
				</div>
			)}
		</>
	);
}
