import type { Metadata } from "next";
import { Figtree } from 'next/font/google';
import "./globals.css";

const figtree = Figtree({ 
  subsets: ["latin"],
  weight: ['400', '500', '600', '700'],
  variable: '--font-figtree',
});

export const metadata: Metadata = {
  title: "Xin Yi WMS® | Intelligent Food Warehouse Management",
  description: "AI-powered warehouse management system designed for fresh food logistics with FEFO intelligence",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${figtree.variable} font-sans antialiased`}>
        {children}
      </body>
    </html>
  );
}
