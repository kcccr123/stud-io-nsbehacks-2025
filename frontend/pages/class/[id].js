import React, { useEffect, useState } from "react";
import { useRouter } from "next/router";

async function fetchClass(id) {
  return { id, name: "CSC111" };
}

async function fetchUnderstanding(id) {
  return 78;
}

export default function ClassPage() {
  const { id } = useRouter().query;
  const [classData, setClassData] = useState(null);
  const [error, setError] = useState(null);
  const [progress, setProgress] = useState(50);
  const [messages, setMessages] = useState([]);
  const [chatInput, setChatInput] = useState("");

  useEffect(() => {
    if (!id) return;
    (async () => {
      try {
        const data = await fetchClass(id);
        setClassData(data);
        const understanding = await fetchUnderstanding(id);
        setProgress(understanding);
      } catch (err) {
        setError(err.message);
      }
    })();
  }, [id]);

  const handleSendMessage = () => {
    if (!chatInput.trim()) return;
    const newMessage = { sender: "user", text: chatInput };
    setMessages((prev) => [...prev, newMessage]);
    setChatInput("");

    // Simulate AI response
    setTimeout(() => {
      const aiMessage = {
        sender: "ai",
        text: `AI response to "${newMessage.text}"`,
      };
      setMessages((prev) => [...prev, aiMessage]);
    }, 500);
  };

  if (error) return <div className="text-muted">Error: {error}</div>;
  if (!classData) return <div className="text-muted">Loading...</div>;

  return (
    <>
      {/* Temporary input for setting progress */}
      <div className="fixed top-0 right-0 p-4 bg-transparent text-foreground">
        <input
          className="bg-transparent border-b border-foreground focus:outline-none text-foreground"
          type="number"
          value={progress}
          onChange={(e) => setProgress(Number(e.target.value))}
          placeholder="Set progress"
        />
      </div>

      <nav className="min-h-screen w-screen flex justify-center items-start pt-10 bg-background">
        <div className="w-full max-w-3xl">
          <div className="flex items-center space-x-4 p-4 rounded justify-between">
            <h1 className="text-5xl font-bold text-foreground">
              {classData.name}
            </h1>
            <button className="flex items-center bg-primary hover:bg-primary-hover text-foreground px-4 py-2 rounded focus:outline-none">
              Manage Materials
            </button>
          </div>

          {/* Progress Bar Section */}
          <div className="px-4 mt-4">
            <p className="text-lg font-semibold text-foreground mb-2">
              Understanding
            </p>
            <div
              className="w-full h-4 rounded-full border-2 border-foreground overflow-hidden"
              style={{ backgroundColor: "transparent" }}
            >
              <div
                className="h-full rounded-full"
                style={{
                  width: `${progress}%`,
                  background: "linear-gradient(to right, #4caf50, #8bc34a)",
                  transition: "width 0.5s ease",
                }}
              />
            </div>
          </div>

          {/* Chat Window Section */}
          <div className="px-4 mt-6">
            <div className="mb-2 text-lg font-semibold text-foreground">
              Chat
            </div>
            <div
              className="flex flex-col border border-foreground rounded bg-background"
              style={{ height: "600px" }}
            >
              <div className="flex-1 overflow-y-auto p-2">
                {messages.length === 0 && (
                  <p className="text-muted">No messages yet...</p>
                )}
                {messages.map((msg, index) => (
                  <div
                    key={index}
                    className={`mb-1 ${
                      msg.sender === "user" ? "text-right" : "text-left"
                    }`}
                  >
                    <span className="inline-block rounded px-2 py-1 text-foreground">
                      {msg.text}
                    </span>
                  </div>
                ))}
              </div>
              <div className="flex space-x-2 p-2 border-t border-foreground">
                <input
                  className="flex-1 px-2 py-1 border border-foreground rounded bg-transparent text-foreground focus:outline-none"
                  type="text"
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  placeholder="Type a message"
                  onKeyDown={(e) => {
                    if (e.key === "Enter") handleSendMessage();
                  }}
                />
                <button
                  className="px-4 py-1 bg-primary hover:bg-primary-hover text-foreground rounded focus:outline-none"
                  onClick={handleSendMessage}
                >
                  Send
                </button>
              </div>
            </div>
          </div>
        </div>
      </nav>
    </>
  );
}
