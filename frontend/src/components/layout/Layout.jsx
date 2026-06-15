import { Outlet } from "react-router-dom";
import Navbar from "./Navbar";
import Footer from "./Footer";
import AdSlot, { MobileStickyAd } from "@/components/ads/AdSlot";

export default function Layout() {
  return (
    <div className="min-h-screen flex flex-col bg-pitch-dark text-slate-100">

      {/* Header banner ad — loads after first paint to protect LCP */}
      <div style={{ minHeight: 90 }} className="w-full bg-pitch-mid border-b border-white/5">
        <div className="max-w-screen-xl mx-auto px-4 py-1">
          <AdSlot slot="header_banner" />
        </div>
      </div>

      <Navbar />

      <main className="flex-1 max-w-screen-xl mx-auto w-full px-4 py-6">
        <div className="flex gap-6">
          {/* Main content */}
          <div className="flex-1 min-w-0">
            <Outlet />
          </div>

          {/* Sidebar — desktop only */}
          <aside className="hidden xl:block w-72 shrink-0">
            <AdSlot slot="sidebar_top" sticky />
          </aside>
        </div>
      </main>

      <Footer />

      {/* Sticky mobile footer ad */}
      <MobileStickyAd />
    </div>
  );
}