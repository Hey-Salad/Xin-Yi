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
  icons: {
    icon: '/HeySalad_Launchericon.jpg',
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        <link href='https://api.mapbox.com/mapbox-gl-js/v3.0.0/mapbox-gl.css' rel='stylesheet' />
      </head>
      <body className={`${figtree.variable} font-sans antialiased`}>
        {children}
      </body>
    </html>
  );
}
