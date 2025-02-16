import { useState } from "react";

export default function RegisterPage() {
  const [step, setStep] = useState(0);
  const [formData, setFormData] = useState({
    email: "",
    username: "",
    password: "",
    confirmPassword: "",
  });
  const [errorMsg, setErrorMsg] = useState("");

  // Get error message based on step
  const getErrorMessage = () => {
    if (step === 0) return "Please enter a valid email.";
    if (step === 1) return "Please enter a valid username.";
    if (step === 2)
      return "Please enter a strong password (at least 8 characters, including letters and numbers).";
    if (step === 3) return "Passwords do not match.";
    return "";
  };

  // Validate current field based on step
  const isCurrentFieldValid = () => {
    if (step === 0) return formData.email.trim() !== "";
    if (step === 1) return formData.username.trim() !== "";
    if (step === 2)
      return /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$/.test(formData.password);
    if (step === 3)
      return (
        formData.confirmPassword.trim() !== "" &&
        formData.confirmPassword === formData.password
      );
    return false;
  };

  // Handle advancing steps or final submission via key press
  const handleKeyDown = (e) => {
    if (e.key === "Enter") {
      if (!isCurrentFieldValid()) {
        setErrorMsg(getErrorMessage());
        return;
      }
      setErrorMsg("");
      if (step < 3) {
        setStep((prev) => prev + 1);
      } else {
        handleRegister(formData);
      }
    }
  };

  const handleRegister = async (data) => {
    try {
      const response = await fetch("http://127.0.0.1:5000/users/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: data.email,
          username: data.username,
          password: data.password,
        }),
      });

      if (!response.ok) {
        throw new Error("Registration failed");
      }

      const result = await response.json();
      console.log("Registration successful:", result);
    } catch (error) {
      console.error("Error during registration:", error.message);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
    setErrorMsg("");
  };

  // Function to handle OK button click
  const handleOk = () => {
    if (!isCurrentFieldValid()) {
      setErrorMsg(getErrorMessage());
      return;
    }
    setErrorMsg("");
    if (step < 3) {
      setStep((prev) => prev + 1);
    } else {
      console.log(formData);
      handleRegister(formData);
    }
  };

  // Tailwind classes for transition animations
  const activeClass =
    "transition-transform transition-opacity duration-500 ease-in-out transform translate-x-0 opacity-100";
  const hiddenClass =
    "transition-transform transition-opacity duration-500 ease-in-out transform translate-x-full opacity-0 absolute inset-0";

  // Popup styling for error message
  const errorPopupClass =
    "absolute left-0 bottom-full mt-1 text-sm text-error bg-surface border border-error px-2 py-1 rounded ";

  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="relative overflow-hidden w-[400px] mx-auto my-8 p-6 rounded-lg ">
        {/* Step 0: Email */}
        <div className={step === 0 ? activeClass : hiddenClass}>
          <div className="flex flex-col items-center justify-center h-full">
            <h2 className="text-2xl font-bold text-foreground mb-8 text-center">
              Email
            </h2>
            <div className="relative w-full">
              <input
                type="email"
                name="email"
                placeholder="Enter your email"
                value={formData.email}
                onChange={handleChange}
                onKeyDown={handleKeyDown}
                className="w-full p-3 bg-transparent border border-muted rounded outline-none focus:ring-2 focus:ring-foreground"
              />
              {errorMsg && <div className={errorPopupClass}>{errorMsg}</div>}
            </div>
            <div className="flex mt-4">
              <button
                onClick={handleOk}
                className="bg-muted w-16 text-foreground px-4 py-2 rounded hover:bg-muted-dark transition"
              >
                OK
              </button>
            </div>
          </div>
        </div>

        {/* Step 1: Username */}
        <div className={step === 1 ? activeClass : hiddenClass}>
          <div className="flex flex-col items-center justify-center h-full">
            <h2 className="text-2xl font-bold text-foreground mb-8 text-center">
              Username
            </h2>
            <div className="relative w-full">
              <input
                type="text"
                name="username"
                placeholder="Enter your username"
                value={formData.username}
                onChange={handleChange}
                onKeyDown={handleKeyDown}
                className="w-full p-3 bg-transparent border border-muted rounded outline-none focus:ring-2 focus:ring-foreground"
              />
              {errorMsg && <div className={errorPopupClass}>{errorMsg}</div>}
            </div>
            <div className="flex mt-4 gap-2">
              <button
                onClick={() => {
                  setErrorMsg("");
                  setStep((prev) => prev - 1);
                }}
                className="bg-muted w-16 text-foreground px-4 py-2 rounded hover:bg-muted-dark transition"
              >
                Back
              </button>
              <button
                onClick={handleOk}
                className="bg-muted w-16 text-foreground px-4 py-2 rounded hover:bg-muted-dark transition"
              >
                OK
              </button>
            </div>
          </div>
        </div>

        {/* Step 2: Password */}
        <div className={step === 2 ? activeClass : hiddenClass}>
          <div className="flex flex-col items-center justify-center h-full">
            <h2 className="text-2xl font-bold text-foreground mb-8 text-center">
              Password
            </h2>
            <div className="relative w-full">
              <input
                type="password"
                name="password"
                placeholder="Enter your password"
                value={formData.password}
                onChange={handleChange}
                onKeyDown={handleKeyDown}
                className="w-full p-3 bg-transparent border border-muted rounded outline-none focus:ring-2 focus:ring-foreground"
              />
              {errorMsg && <div className={errorPopupClass}>{errorMsg}</div>}
            </div>
            <div className="flex mt-4 gap-2">
              <button
                onClick={() => {
                  setErrorMsg("");
                  setStep((prev) => prev - 1);
                }}
                className="bg-muted w-16 text-foreground px-4 py-2 rounded hover:bg-muted-dark transition"
              >
                Back
              </button>
              <button
                onClick={handleOk}
                className="bg-muted w-16 text-foreground px-4 py-2 rounded hover:bg-muted-dark transition"
              >
                OK
              </button>
            </div>
          </div>
        </div>

        {/* Step 3: Confirm Password */}
        <div className={step === 3 ? activeClass : hiddenClass}>
          <div className="flex flex-col items-center justify-center h-full">
            <h2 className="text-2xl font-bold text-foreground mb-8 text-center">
              Confirm Password
            </h2>
            <div className="relative w-full">
              <input
                type="password"
                name="confirmPassword"
                placeholder="Confirm your password"
                value={formData.confirmPassword}
                onChange={handleChange}
                onKeyDown={handleKeyDown}
                className="w-full p-3 bg-transparent border border-muted rounded outline-none focus:ring-2 focus:ring-foreground"
              />
              {errorMsg && <div className={errorPopupClass}>{errorMsg}</div>}
            </div>
            <div className="flex mt-4 gap-2">
              <button
                onClick={() => {
                  setErrorMsg("");
                  handleRegister(formData);
                }}
                className="bg-muted w-16 text-foreground px-4 py-2 rounded hover:bg-muted-dark transition"
              >
                Back
              </button>
              <button
                onClick={handleOk}
                className="bg-muted w-16 text-foreground px-4 py-2 rounded hover:bg-muted-dark transition"
              >
                OK
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
