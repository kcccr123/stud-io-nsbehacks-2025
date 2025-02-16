import React, { useEffect, useState } from "react";
import { useRouter } from "next/router";
import { PROJECT_NAME } from "../utils/config";

const Dashboard = () => {
  const router = useRouter();
  const [classes, setClasses] = useState([]);

  // Empty function to fetch classes.
  const fetchClasses = async () => {
    // TODO: Fetch classes from the backend
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
        <button className="bg-primary hover:bg-primary-hover text-white px-4 py-2 rounded flex items-center">
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
    </div>
  );
};

export default Dashboard;
