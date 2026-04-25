import type { Metadata } from "next";
import type { JSX, ReactNode } from "react";

import "./globals.css";

export const metadata: Metadata = {
  title: "Keystone",
  description: "Keystone — full-stack platform.",
};

interface RootLayoutProps {
  readonly children: ReactNode;
}

export default function RootLayout({
  children,
}: RootLayoutProps): JSX.Element {
  return (
    <html lang="en" data-theme="light">
      <body className="bg-bg-canvas text-fg antialiased">{children}</body>
    </html>
  );
}
