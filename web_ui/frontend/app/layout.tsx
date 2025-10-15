import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Coding Agent",
  description: "AI-powered coding assistant with real-time streaming",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  );
}

