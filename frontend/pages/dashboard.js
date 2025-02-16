import React, { useEffect, useState } from "react";
import { useRouter } from "next/router";
import { PROJECT_NAME } from "../utils/config";

const Dashboard = () => {
  const router = useRouter();
  const [classes, setClasses] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newClassName, setNewClassName] = useState("");

  const fetchClasses = async () => {
    try {
      const response = await fetch("http://localhost:5000/classes");
      if (!response.ok) {
        throw new Error("Failed to fetch classes");
      }
      const data = await response.json();
      return data.map((cls) => ({ id: cls._id, className: cls.className }));
    } catch (error) {
      console.error("Failed to fetch classes:", error);
      return [];
    }
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
      window.location.reload(); // Refresh the page to load updated classes

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
          className="bg-blue-500 hover:bg-blue-700 text-white px-4 py-2 rounded flex items-center"
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
                className="relative bg-surface border border-gray-300 rounded-2xl p-4 flex items-center justify-center transform transition-transform duration-300 hover:scale-105 cursor-pointer shadow-lg w-80 h-48 group m-2"
              >
                <button
                  className="absolute top-4 left-4 bg-red-500 text-white p-2 rounded-full opacity-0 group-hover:opacity-100 transition-opacity w-10 h-10 flex items-center justify-center"
                  onClick={(e) => {
                    e.stopPropagation();
                    fetch(`http://localhost:5000/classes/${cls.id}`, {
                      method: "DELETE",
                    })
                      .then((response) => {
                        if (response.ok) {
                          alert("Class deleted successfully");
                          window.location.reload(); // Refresh the page to load updated classes
                        } else {
                          alert("Failed to delete class");
                        }
                      })
                      .catch((err) =>
                        console.error("Error deleting class:", err)
                      );
                  }}
                >
                  ✕
                </button>
                <div onClick={() => handleClassClick(cls.id)}>
                  <h2 className="text-2xl font-bold text-center text-foreground">
                    {cls.className}
                  </h2>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
          <div className="bg-white p-6 rounded-lg shadow-md w-96">
            <h2 className="text-2xl font-bold text-black mb-4">Join a Class</h2>
            <input
              type="text"
              value={newClassName}
              onChange={(e) => setNewClassName(e.target.value)}
              placeholder="Enter class name"
              className="w-full p-2 border rounded mb-4 text-black"
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
                className="bg-blue-500 hover:bg-blue-700 text-white px-4 py-2 rounded"
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
