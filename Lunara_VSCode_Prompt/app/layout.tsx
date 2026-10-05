import type { Metadata, Viewport } from "next";
import "./globals.css";
import { AppShell } from "@/components/app-shell";
import { PwaRegister } from "@/components/pwa-register";

export const metadata: Metadata = {
  title: "Lunara — Your safer way home",
  description: "Safety-aware route recommendations with transparent confidence and community context.",
  manifest: "/manifest.webmanifest",
  appleWebApp: { capable: true, title: "Lunara", statusBarStyle: "default" },
};
export const viewport: Viewport = { themeColor: "#462f68", width: "device-width", initialScale: 1 };

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body><PwaRegister/><AppShell>{children}</AppShell></body></html>;
}
