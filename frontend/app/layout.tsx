import "../styles/globals.css";
import type { ReactNode } from "react";
import { Inter } from "next/font/google";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

export const metadata = {
  title: "Smart Audit Agent",
  description: "Next.js frontend for Smart Audit Agent",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body className={`${inter.variable} min-h-screen bg-background text-foreground`}>
        {children}
      </body>
    </html>
  );
}
