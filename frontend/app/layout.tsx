import "@livekit/components-styles";
import "./globals.css";
import { Public_Sans } from "next/font/google";
import Image from 'next/image';

const publicSans400 = Public_Sans({
  weight: "400",
  subsets: ["latin"],
});

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`h-full ${publicSans400.className}`}>
      <body className="h-full bg-white relative">
        <div className="absolute top-4 left-4 z-10">
          <Image 
            src="/images/logoGovlab.png"
            alt="Logo GovLab" 
            width={150}
            height={50}
            priority
          />
        </div>
        <div className="absolute top-4 right-4 z-10">
          <Image 
            src="/images/logo.jpg"
            alt="Logo Universidad de la Sabana" 
            width={150}
            height={50}
            priority
          />
        </div>
        {children}
      </body>
    </html>
  );
}