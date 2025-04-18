import type { Metadata } from "next";
import { GeistSans, GeistMono } from "geist/font";
import "./globals.css";
import Navbar from "../components/Navbar";

// const geistSans = Geist({
//   variable: "--font-geist-sans",
//   subsets: ["latin"],
// });
//
// const geistMono = Geist_Mono({
//   variable: "--font-geist-mono",
//   subsets: ["latin"],
// });

export const metadata: Metadata = {
  title: "HSI Strategy App",
  description: "恆生指數策略分析平台",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-Hant">
      <body
        className={`${GeistSans.variable} ${GeistMono.variable} antialiased flex`}
      >
        <Navbar />
        <main className="flex-1 p-8 ml-64">
          {children}
        </main>
      </body>
    </html>
  );
}
