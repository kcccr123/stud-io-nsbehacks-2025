import React, { useEffect, useState } from "react";
import { useRouter } from "next/router";
import SpeechRecognition, {
  useSpeechRecognition,
} from "react-speech-recognition";

async function fetchClass(id) {
  return { id, name: "CSC111" };
}

async function fetchUnderstanding(id) {
  return 78;
}

export default function ClassPage() {
  const router = useRouter();

  const {
    transcript,
    listening,
    resetTranscript,
    browserSupportsSpeechRecognition,
  } = useSpeechRecognition();

  // Update the state when the transcript changes
  React.useEffect(() => {
    setAnswer(transcript);
  }, [transcript]);

  const { id } = useRouter().query;
  const [classData, setClassData] = useState(null);
  const [error, setError] = useState(null);
  const [progress, setProgress] = useState(50);

  const [question, setQuestion] = useState("");
  const [flashcards, setFlashcards] = useState([]);
  const [currentFlashcard, setCurrentFlashcard] = useState(null);
  const [recommendedFlashcard, SetRecommendedFlashcard] = useState(null);
  const [aiText, setAiText] = useState("Generate some questions!");
  const [answer, setAnswer] = useState("");
  const [flip, setFlip] = useState(false);
  const [answerError, setAnswerError] = useState(false);
  const [isReviewMode, setIsReviewMode] = useState(false);

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [studyNotification, setStudyNotification] = useState(false);
  const [topic, setTopic] = useState(null);

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

  useEffect(() => {
    setFlip(true);
    const timer = setTimeout(() => setFlip(false), 600);
    return () => clearTimeout(timer);
  }, [aiText]);

  if (error) return <div className="text-muted">Error: {error}</div>;
  if (!classData) return <div className="text-muted">Loading...</div>;

  function handleNextQuestion() {
    if (flashcards.length > 0) {
      const nextFlashcard = flashcards.pop();
      setCurrentFlashcard(nextFlashcard);
      setAiText(nextFlashcard.question);
      setFlashcards([...flashcards]);
    } else {
      if (recommendedFlashcard !== null) {
        setAiText(recommendedFlashcard.question);
        SetRecommendedFlashcard(null);
        return;
      }

      setAiText("No more flashcards.");
    }
  }

  async function handleAnswer() {
    if (!answer.trim()) {
      setAnswerError(true);
      return;
    }
    setAnswerError(false);

    const formData = new FormData();
    formData.append("chat_id", "CSC111");
    formData.append("user_id", "67b0e038fede027c6a136c03");
    formData.append("flashcard_id", currentFlashcard._id);
    formData.append("question", aiText);
    formData.append("answer", answer);

    try {
      const response = await fetch("http://localhost:5000/answer", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Failed to submit answer");
      }

      const result = await response.json();
      setAiText(result.correct ? "Good job!" : result.correct_answer);
    } catch (error) {
      console.error("Error submitting answer:", error.message);
    }
  }

  function handleFileUpload(event) {
    setSelectedFile(event.target.files[0]);
  }

  async function handleUpload() {
    if (!question.trim()) {
      alert("Question field must be filled before uploading.");
      return;
    }

    console.log(question);
    if (selectedFile) {
      const formData = new FormData();
      formData.append("chat_id", "CSC111");
      formData.append("user_id", "67b0e038fede027c6a136c03");
      formData.append("user_request", question);
      formData.append("pdfs", selectedFile); // Key `pdfs` matches your backend expectation

      try {
        let response;

        if (isReviewMode) {
          response = await fetch("http://localhost:5000/question/review", {
            method: "POST",
            body: formData,
          });
        } else {
          response = await fetch("http://localhost:5000/question/study", {
            method: "POST",
            body: formData,
          });

          setStudyNotification(true);
          setTopic(response.topic);
        }

        if (!response.ok) {
          throw new Error("Upload failed");
        }

        const result = await response.json();
        console.log("Upload successful:", result);
        setFlashcards(result.flashcards);
        SetRecommendedFlashcard(result.recommended_flashcard);
        setUploadedFiles((prevFiles) => [...prevFiles, selectedFile]);
        setSelectedFile(null);
      } catch (error) {
        console.error("Error during upload:", error.message);
      }
    }
  }

  function handleRemoveFile(index) {
    setUploadedFiles((prevFiles) => prevFiles.filter((_, i) => i !== index));
  }

  if (!browserSupportsSpeechRecognition) {
    return <span>Browser does not support speech recognition.</span>;
  }

  return (
    <>
      <style jsx>{`
        @keyframes flip {
          0% {
            transform: rotateY(0);
          }
          50% {
            transform: rotateY(90deg);
          }
          100% {
            transform: rotateY(180deg);
          }
        }
        .flip-animation {
          animation: flip 0.6s ease-in-out;
        }

        .disabled {
          background-color: grey;
          cursor: not-allowed;
        }
        .modal {
          position: fixed;
          top: 0;
          left: 0;
          width: 100%;
          height: 100%;
          background: rgba(0, 0, 0, 0.5);
          display: flex;
          justify-content: center;
          align-items: center;
        }
        .modal-content {
          padding: 20px;
          border-radius: 8px;
          min-width: 400px;
          min-height: 400px;
          text-align: center;
        }
        .file-input {
          display: none;
        }
        .file-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
        }
      `}</style>

      <div className="fixed flex flex-col top-0 right-0 p-4 bg-transparent text-foreground">
        <input
          className="bg-transparent border-b border-foreground focus:outline-none text-foreground"
          type="number"
          value={progress}
          onChange={(e) => setProgress(Number(e.target.value))}
          placeholder="Set progress"
        />
        <input
          className="bg-transparent border-b border-foreground focus:outline-none text-foreground"
          type="text"
          value={aiText}
          onChange={(e) => setAiText(e.target.value)}
          placeholder="Set ai text"
        />
      </div>

      <nav className="min-h-screen w-screen flex justify-center items-start pt-10 bg-background">
        <div className="w-full max-w-3xl">
          <div className="flex items-center space-x-4 p-4 rounded justify-between">
            <h1 className="text-5xl font-bold text-foreground">
              {classData.name}
            </h1>
            <div className="flex space-x-4 p-4">
              <button
                className="flex items-center bg-primary hover:bg-primary-hover text-foreground px-4 py-2 rounded focus:outline-none"
                onClick={() => setIsModalOpen(true)}
              >
                Manage Materials
              </button>
              <button
                className="flex items-center bg-primary hover:bg-primary-hover text-foreground px-4 py-2 rounded focus:outline-none"
                onClick={() => router.back()}
              >
                ← Back
              </button>
            </div>
          </div>

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

          <div className="px-4 mt-6">
            <div
              className={`flex items-center justify-center border border-foreground p-2 rounded bg-background text-foreground mb-4 h-80 ${
                flip ? "flip-animation" : ""
              }`}
              onAnimationEnd={() => setFlip(false)}
            >
              <p>{aiText}</p>
            </div>
            <input
              className={`border p-2 rounded w-full mb-2 bg-background text-foreground ${
                answerError ? "error" : "border-foreground"
              }`}
              placeholder="Your answer"
              value={answer}
              onChange={(e) => {
                setAnswer(e.target.value);
                if (e.target.value.trim()) {
                  setAnswerError(false);
                }
              }}
            />
            <div className="flex justify-center space-x-4">
              {studyNotification && (
                <div className="fixed bottom-4 right-4 bg-blue-500 text-white p-4 rounded-lg shadow-lg w-64">
                  <h3 className="text-lg font-bold mb-2">
                    Topics You're Struggling With!
                  </h3>
                  <p>You seem to be struggling with ${topic}</p>
                  <button
                    className="mt-2 bg-white text-blue-500 px-3 py-1 rounded hover:bg-gray-100"
                    onClick={() => {
                      setStudyNotification(false);
                      setTopic(null);
                    }}
                  >
                    Dismiss
                  </button>
                </div>
              )}
              <button
                className="px-6 py-2 w-40 bg-primary text-foreground rounded hover:bg-primary-hover focus:outline-none text-center"
                onClick={() => {
                  handleNextQuestion();
                  setFlip(true);
                }}
              >
                Next Question
              </button>
              <button
                className={`px-6 py-2 w-40 bg-surface text-foreground rounded hover:bg-surface-hover focus:outline-none text-center ${
                  !answer.trim() ? "disabled" : ""
                }`}
                onClick={() => {
                  handleAnswer();
                  setAnswer("");
                  setFlip(true);
                }}
                disabled={!answer.trim()}
              >
                Answer
              </button>
              <p>Microphone: {listening ? "on" : "off"}</p>
              <button
                onClick={() =>
                  SpeechRecognition.startListening({ continuous: true })
                }
                className="ml-2 bg-blue-500 text-white p-2 rounded"
              >
                🎤 Start Recording
              </button>
              <button
                onClick={SpeechRecognition.stopListening}
                className="ml-2 bg-red-500 text-white p-2 rounded"
              >
                ⏹ Stop
              </button>
              <button
                onClick={resetTranscript}
                className="ml-2 bg-gray-500 text-white p-2 rounded"
              >
                🔄 Reset
              </button>
              <button
                onClick={() => setIsReviewMode((prev) => !prev)}
                className="px-6 py-2 w-40 bg-primary text-foreground rounded hover:bg-primary-hover focus:outline-none text-center"
              >
                {isReviewMode
                  ? "Switch to Study Mode"
                  : "Switch to Review Mode"}
              </button>
            </div>
          </div>
        </div>
      </nav>

      {isModalOpen && (
        <div className="modal w-80" onClick={() => setIsModalOpen(false)}>
          <div
            className="modal-content flex flex-col items-center gap-4 bg-surface"
            onClick={(e) => e.stopPropagation()}
          >
            <input
              className="border border-foreground p-2 rounded w-full mb-4 bg-background text-foreground"
              placeholder="what would you like to work on"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
            />
            <h2 className="mb-4 text-2xl">Upload Course Material</h2>
            <label
              className="border rounded p-2 inline-block cursor-pointer min-w-32"
              htmlFor="file-upload"
            >
              {selectedFile ? selectedFile.name : "Choose File"}
            </label>
            <input
              id="file-upload"
              className="file-input"
              type="file"
              accept="application/pdf"
              onChange={handleFileUpload}
            />
            <button
              className="p-2 w-28 bg-primary rounded hover:bg-primary-hover text-foreground"
              onClick={handleUpload}
            >
              Upload
            </button>

            <div className="mt-4">
              <h3>Uploaded Files:</h3>
              <ul>
                {uploadedFiles.map((file, index) => (
                  <li key={index} className="file-item">
                    {file.name}
                    <button
                      className=" text-foreground p-1 rounded"
                      onClick={() => handleRemoveFile(index)}
                    >
                      &times;
                    </button>
                  </li>
                ))}
              </ul>
              <button
                className="p-2 mt-4 bg-primary rounded hover:bg-primary-hover text-foreground"
                onClick={() => setIsModalOpen(false)}
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
