import "./App.css";
import Chatbot from "./components/Chatbot";

function App() {
	return (
		<div className="min-h-screen min-w-screen overflow-x-hidden overflow-y-auto">
			<img
				src="/idc-bot.png"
				className="w-screen h-screen object-cover fixed top-0 left-0 z-[-1]"
			/>
			<Chatbot />
		</div>
	);
}

export default App;
