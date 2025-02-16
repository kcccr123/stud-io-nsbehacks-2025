import { useEffect } from "react";
import { useRouter } from "next/router";
import "@/styles/globals.css";
import "regenerator-runtime/runtime";

export default function App({ Component, pageProps }) {
  const router = useRouter();

  useEffect(() => {
    const userId = localStorage.getItem("userId");

    if (!userId) {
      router.push("/login"); // Redirect to login if userId is not found
    } else if (router.pathname === "/") {
      router.push("/dashboard"); // Redirect to dashboard if userId exists and the route is root
    }
  }, [router]);

  return <Component {...pageProps} />;
}
