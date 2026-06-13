import { Routes, Route } from "react-router-dom";
import Layout from "@/components/layout/Layout";
import HomePage from "@/pages/HomePage";
import LivePage from "@/pages/LivePage";
import MatchDetailPage from "@/pages/MatchDetailPage";
import CompetitionPage from "@/pages/CompetitionPage";
import TeamPage from "@/pages/TeamPage";
import NotFoundPage from "@/pages/NotFoundPage";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<HomePage />} />
        <Route path=":sport/scores/live" element={<LivePage />} />
        <Route path=":sport/match/:matchId" element={<MatchDetailPage />} />
        <Route path=":sport/competition/:competitionId" element={<CompetitionPage />} />
        <Route path=":sport/team/:teamId" element={<TeamPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  );
}
