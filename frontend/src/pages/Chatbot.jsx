import { useState, useRef, useEffect } from "react";
import { Send, ChevronDown } from "lucide-react";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const initialMessages = [
  { id: 1, text: "السلام علیکم! \n\nبراہ کرم اپنی کہانی کا آغاز لکھیں، اور میں آپ کے لیے ایک مکمل کہانی تیار کروں گا۔", sender: "bot" },
];

const Chatbot = () => {
  const [messages, setMessages] = useState(initialMessages);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [selectedModel, setSelectedModel] = useState("default");
  const [selectedNgramType, setSelectedNgramType] = useState("trigram");
  const [availableModels, setAvailableModels] = useState({});
  const [isLoadingModels, setIsLoadingModels] = useState(true);
  const [showModelDropdown, setShowModelDropdown] = useState(false);
  const [showNgramDropdown, setShowNgramDropdown] = useState(false);
  const bottomRef = useRef(null);
  const dropdownRef = useRef(null);
  const ngramDropdownRef = useRef(null);
  const typingTimeoutRef = useRef(null);
  
  const ngramTypes = [
    { value: "trigram", label: "Tri-gram" },
    { value: "5gram", label: "Five-gram" },
    { value: "7gram", label: "Seven-gram" },
  ];

  // Fetch available models on mount
  useEffect(() => {
    const fetchModels = async () => {
      try {
        console.log(`Fetching models from ${API_BASE_URL}/api/models`);
        const response = await fetch(`${API_BASE_URL}/api/models`);
        console.log("Response status:", response.status, response.statusText);

        if (response.ok) {
          const data = await response.json();
          console.log("Received models data:", data);
          setAvailableModels(data.models || {});
          setSelectedModel(data.default || "default");

          if (!data.models || Object.keys(data.models).length === 0) {
            console.warn("No models found in API response");
            setAvailableModels({ default: "Default Model" });
          }
        } else {
          console.error(`API error: ${response.status} ${response.statusText}`);
          setAvailableModels({ default: "Default Model" });
        }
      } catch (error) {
        console.error("Error fetching models:", error);
        setAvailableModels({ default: "Default Model" });
      } finally {
        setIsLoadingModels(false);
      }
    };
    fetchModels();
  }, []);

  // Cleanup typing timeout on unmount
  useEffect(() => {
    return () => {
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current);
      }
    };
  }, []);

  // Close dropdowns when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setShowModelDropdown(false);
      }
      if (ngramDropdownRef.current && !ngramDropdownRef.current.contains(event.target)) {
        setShowNgramDropdown(false);
      }
    };
    if (showModelDropdown || showNgramDropdown) {
      document.addEventListener("mousedown", handleClickOutside);
      return () => document.removeEventListener("mousedown", handleClickOutside);
    }
  }, [showModelDropdown, showNgramDropdown]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Process story text: remove <EOS>, replace <EOP> with newline
  const processStoryText = (text) => {
    if (!text) return text;
    return text
      .replace(/<EOS>/g, '') // Remove <EOS> tags
      .replace(/<EOP>/g, '\n') // Replace <EOP> with newline
      .replace(/<EOT>/g, '') // Also remove <EOT> if present
      .trim();
  };

  // Smooth type-out effect for bot messages (word by word)
  const typeOutMessage = (fullText, messageId) => {
    if (!fullText) return;

    // Split into tokens but keep spaces/newlines as separate items
    const tokens = fullText.split(/(\s+)/);
    let index = 0;
    let current = "";

    const step = () => {
      if (index >= tokens.length) {
        typingTimeoutRef.current = null;
        return;
      }

      current += tokens[index];
      index += 1;

      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === messageId ? { ...msg, text: current } : msg
        )
      );

      typingTimeoutRef.current = setTimeout(step, 60); // adjust speed here (ms per token)
    };

    step();
  };

  const handleSend = async () => {
    const text = input.trim();
    if (!text || isLoading) return;

    const userMsg = { id: Date.now(), text, sender: "user" };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/api/generate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          prompt: text,
          max_length: 500,
          temperature: 0.8,
          top_k: 50,
          model_key: selectedModel,
          ngram_type: selectedNgramType,
        }),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();
      const rawStory = data.story || "Sorry, I couldn't generate a story. Please try again.";
      const processedStory = processStoryText(rawStory);

      const botId = Date.now() + 1;
      // Add an empty bot message that will be filled gradually
      setMessages((prev) => [
        ...prev,
        { id: botId, text: "", sender: "bot" },
      ]);

      // Start typing effect
      typeOutMessage(processedStory, botId);
    } catch (error) {
      console.error("Error generating story:", error);
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          text: "Sorry, I encountered an error. Please make sure the backend API is running.",
          sender: "bot",
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="border-b border-border px-6 py-4">
        <div className="flex items-center justify-between mb-2">
          <div>
            <h1 className="text-lg font-semibold text-foreground">Chatbot</h1>
            <p className="text-xs text-muted-foreground">Ask me anything</p>
          </div>
          {/* Model Selectors */}
          <div className="flex items-center gap-3">
            {/* N-gram Type Selector */}
            <div className="relative" ref={ngramDropdownRef}>
              <button
                type="button"
                onClick={() => setShowNgramDropdown(!showNgramDropdown)}
                className="flex items-center gap-2 px-3 py-1.5 text-xs font-medium bg-secondary hover:bg-secondary/80 rounded-lg text-foreground transition-colors"
              >
                <span>{ngramTypes.find(n => n.value === selectedNgramType)?.label || selectedNgramType}</span>
                <ChevronDown className={`h-3 w-3 transition-transform ${showNgramDropdown ? "rotate-180" : ""}`} />
              </button>
              {showNgramDropdown && (
                <div className="absolute right-0 mt-2 w-40 bg-card border border-border rounded-lg shadow-lg z-[100]">
                  {ngramTypes.map((ngram) => (
                    <button
                      key={ngram.value}
                      type="button"
                      onClick={(e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        setSelectedNgramType(ngram.value);
                        setShowNgramDropdown(false);
                      }}
                      className={`w-full text-left px-4 py-2 text-sm hover:bg-secondary transition-colors first:rounded-t-lg last:rounded-b-lg ${
                        selectedNgramType === ngram.value
                          ? "bg-primary text-primary-foreground"
                          : "text-foreground"
                      }`}
                    >
                      {ngram.label}
                    </button>
                  ))}
                </div>
              )}
            </div>
            {/* Model Selector */}
            <div className="relative" ref={dropdownRef}>
              <button
                type="button"
                onClick={() => setShowModelDropdown(!showModelDropdown)}
                className="flex items-center gap-2 px-3 py-1.5 text-xs font-medium bg-secondary hover:bg-secondary/80 rounded-lg text-foreground transition-colors disabled:opacity-50"
                disabled={isLoadingModels}
              >
                <span>
                  {isLoadingModels 
                    ? "Loading models..." 
                    : (availableModels[selectedModel] || selectedModel || "Select model")}
                </span>
                <ChevronDown className={`h-3 w-3 transition-transform ${showModelDropdown ? "rotate-180" : ""}`} />
              </button>
              {showModelDropdown && !isLoadingModels && (
                <div className="absolute right-0 mt-2 w-56 bg-card border border-border rounded-lg shadow-lg z-[100] max-h-64 overflow-auto">
                  {Object.keys(availableModels).length > 0 ? (
                    Object.entries(availableModels).map(([key, label]) => (
                      <button
                        key={key}
                        type="button"
                        onClick={(e) => {
                          e.preventDefault();
                          e.stopPropagation();
                          setSelectedModel(key);
                          setShowModelDropdown(false);
                        }}
                        className={`w-full text-left px-4 py-2 text-sm hover:bg-secondary transition-colors first:rounded-t-lg last:rounded-b-lg ${
                          selectedModel === key
                            ? "bg-primary text-primary-foreground"
                            : "text-foreground"
                        }`}
                      >
                        {label}
                      </button>
                    ))
                  ) : (
                    <div className="px-4 py-2 text-sm text-muted-foreground">
                      No models available. Check backend connection.
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-auto p-6 space-y-4">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.sender === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[70%] rounded-2xl px-4 py-3 whitespace-pre-wrap ${
                msg.sender === "user"
                  ? "bg-chat-user text-chat-user-foreground rounded-br-md text-sm"
                  : "bg-chat-bot text-chat-bot-foreground rounded-bl-md urdu-text"
              }`}
            >
              {msg.text}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-chat-bot text-chat-bot-foreground rounded-2xl rounded-bl-md px-4 py-2.5 text-sm">
              <div className="flex gap-1">
                <span className="w-2 h-2 bg-current rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                <span className="w-2 h-2 bg-current rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                <span className="w-2 h-2 bg-current rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
              </div>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="border-t border-border p-4">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="flex items-center gap-2 bg-secondary rounded-xl px-4 py-2"
        >
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type a message..."
            className="flex-1 bg-transparent text-sm text-foreground placeholder:text-muted-foreground outline-none"
            disabled={isLoading}
          />
          <button
            type="submit"
            className="h-8 w-8 rounded-lg bg-primary text-primary-foreground flex items-center justify-center hover:opacity-90 transition-opacity disabled:opacity-40"
            disabled={!input.trim() || isLoading}
          >
            <Send className="h-4 w-4" />
          </button>
        </form>
      </div>
    </div>
  );
};

export default Chatbot;
