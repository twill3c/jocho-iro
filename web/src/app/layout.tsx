import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "jocho-iro — 情緒の色",
  description:
    "青空文庫 300 作品を八つの情緒(喜怒哀怖好驚厭安)で分析。色相バーコードの壁・情緒レーダー・情緒の川で物語の色を眺める",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ja">
      <body>{children}</body>
    </html>
  );
}
