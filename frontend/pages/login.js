import React, { useState } from "react";
import { PROJECT_NAME } from "../utils/config";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch("http://127.0.0.1:5000/users/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        throw new Error("Login failed");
      }

      const result = await response.json();
      console.log("Login successful:", result);
    } catch (error) {
      console.error("Error during login:", error.message);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="bg-surface p-8 rounded shadow-md w-full max-w-md m-4">
        <h2 className="text-2xl font-bold mb-6 text-center">
          Welcome to {PROJECT_NAME}
        </h2>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="email" className="block text-foreground">
              Email Address
            </label>
            <input
              type="email"
              id="email"
              className="mt-1 block w-full border border-gray-300 bg-transparent rounded-md p-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <div>
            <label htmlFor="password" className="block text-foreground">
              Password
            </label>
            <input
              type="password"
              id="password"
              className="mt-1 block w-full border border-gray-300 bg-transparent rounded-md p-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          <button
            type="submit"
            className="block bg-primary text-white p-2 rounded hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-primary-dark mx-auto w-1/2 "
          >
            Log In
          </button>
        </form>
      </div>
    </div>
  );
}
