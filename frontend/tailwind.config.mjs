/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "#1E1E2E", // Main background
        surface: "#252537", // Slightly lighter surface color
        foreground: "#CDD6F4", // Default text color
        muted: "#A6ADC8", // Muted text

        primary: {
          DEFAULT: "#89B4FA", // Base blue for buttons, links
          hover: "#7399E6", // Hover state
          focus: "#5C83D2",
          disabled: "#4A6EB8",
        },

        secondary: {
          DEFAULT: "#FAB387", // Warm orange for highlights
          hover: "#E69A73",
          focus: "#D68A63",
          disabled: "#B87553",
        },

        accent: {
          DEFAULT: "#A6E3A1", // Green for success and interactive elements
          hover: "#91CF8D",
          focus: "#7DBB79",
          disabled: "#6AA765",
        },

        warning: {
          DEFAULT: "#F9E2AF", // Soft yellow for warnings
          hover: "#E3CD9B",
          focus: "#CDB788",
          disabled: "#B7A175",
        },

        error: {
          DEFAULT: "#F38BA8", // Red for errors
          hover: "#E07894",
          focus: "#CC6680",
          disabled: "#B8556D",
        },

        border: "#313244", // Borders and dividers
        card: "#1E1E2E", // Same as background for uniformity
        overlay: "#181825AA", // Semi-transparent black for modals
      },
    },
  },
  plugins: [],
};
