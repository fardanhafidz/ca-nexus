import "./globals.css";
export const metadata = { title: "Manufacturing Knowledge Hub" };
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-canvas text-slate-900">{children}</body>
    </html>
  );
}
