import React, { useEffect, useState } from "react";
import { useRouter } from "next/router";
import { PROJECT_NAME } from "../utils/config";

const Dashboard = () => {
  const router = useRouter();
  const [classes, setClasses] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newClassName, setNewClassName] = useState("");

  const fetchClasses = async () => {
    return [
      { id: 1, name: "CSC111" },
      { id: 2, name: "CSC110" },
      { id: 3, name: "CSC369" },
      { id: 4, name: "CSC373" },
      { id: 5, name: "CSC420" },
    ];
  };

  const handleClassClick = (id) => {
    router.push(`/class/${id}`);
  };

  const handleJoinClass = async () => {
    try {
      const response = await fetch("http://localhost:5000/classes", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ className: newClassName }),
      });
      if (!response.ok) throw new Error("Failed to join class");
      setIsModalOpen(false);
      setNewClassName("");
      alert("Class joined successfully");
    } catch (error) {
      alert(error.message);
    }
  };

  useEffect(() => {
    const getClasses = async () => {
      const data = await fetchClasses();
      setClasses(data);
    };
    getClasses();
  }, []);

  return (
    <div className="bg-background text-foreground min-h-screen">
      <nav className="bg-surface p-4 shadow-md flex items-center justify-between">
        <h1 className="text-2xl font-bold">{PROJECT_NAME}</h1>
        <button
          className="bg-primary hover:bg-primary-hover text-white px-4 py-2 rounded flex items-center"
          onClick={() => setIsModalOpen(true)}
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth={2}
            stroke="currentColor"
            className="w-5 h-5"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M12 4v16m8-8H4"
            />
          </svg>
          <span className="ml-2">Join Class</span>
        </button>
      </nav>
      <div className="p-4">
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
          {classes.length === 0 ? (
            <p className="text-muted">No classes enrolled.</p>
          ) : (
            classes.map((cls) => (
              <div
                key={cls.id}
                onClick={() => handleClassClick(cls.id)}
                className="bg-surface border border-gray-300 rounded-lg p-6 transform transition-transform duration-300 hover:scale-105 cursor-pointer"
              >
                <h2 className="text-xl font-semibold mb-2">{cls.name}</h2>
              </div>
            ))
          )}
        </div>
      </div>

      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
          <div className="bg-white p-6 rounded-lg shadow-md w-96">
            <h2 className="text-2xl font-bold mb-4">Join a Class</h2>
            <input
              type="text"
              value={newClassName}
              onChange={(e) => setNewClassName(e.target.value)}
              placeholder="Enter class name"
              className="w-full p-2 border rounded mb-4"
            />
            <div className="flex justify-end space-x-2">
              <button
                onClick={() => setIsModalOpen(false)}
                className="bg-gray-500 text-white px-4 py-2 rounded"
              >
                Cancel
              </button>
              <button
                onClick={handleJoinClass}
                className="bg-primary text-white px-4 py-2 rounded"
              >
                Join
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
