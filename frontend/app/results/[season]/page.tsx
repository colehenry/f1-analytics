"use client";

import Image from "next/image";
import { useParams, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

// Type definitions matching our API responses
type DriverStanding = {
  position: number;
  driver_code: string;
  full_name: string;
  team_name: string;
  team_color: string | null;
  total_points: number;
  headshot_url: string | null;
};

type ConstructorStanding = {
  position: number;
  team_name: string;
  team_color: string | null;
  total_points: number;
};

type RoundPodiumDriver = {
  full_name: string;
  driver_code: string;
  team_name: string;
  team_color: string | null;
  headshot_url: string | null;
  fastest_lap: boolean;
};

type RoundSummary = {
  round: number;
  event_name: string;
  date: string;
  circuit_name: string;
  session_type: string;
  podium: RoundPodiumDriver[];
};

type StandingsData = {
  year: number;
  drivers: DriverStanding[];
  constructors: ConstructorStanding[];
};

type RoundsData = {
  year: number;
  rounds: RoundSummary[];
};

export default function ResultsPage() {
  const params = useParams();
  const router = useRouter();
  const season = params.season as string;

  const [standings, setStandings] = useState<StandingsData | null>(null);
  const [rounds, setRounds] = useState<RoundsData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [expandedStandings, setExpandedStandings] = useState<boolean>(false);
  const [availableYears, setAvailableYears] = useState<number[]>([]);

  // Fetch available years once on mount
  useEffect(() => {
    (async () => {
      try {
        const response = await fetch(
          "http://localhost:8000/api/results/seasons",
          {
            cache: "no-store",
          },
        );
        const years = await response.json();
        setAvailableYears(years);
      } catch (error) {
        console.error("Failed to fetch available seasons:", error);
        // Fallback to current year if fetch fails
        setAvailableYears([2024]);
      }
    })();
  }, []);

  // Fetch standings and rounds when season changes
  useEffect(() => {
    if (!season) return;

    (async () => {
      try {
        setLoading(true);

        // Fetch standings and rounds in parallel
        const [standingsRes, roundsRes] = await Promise.all([
          fetch(`http://localhost:8000/api/results/${season}/standings`, {
            cache: "no-store",
          }),
          fetch(`http://localhost:8000/api/results/${season}`, {
            cache: "no-store",
          }),
        ]);

        const standingsData = await standingsRes.json();
        const roundsData = await roundsRes.json();

        setStandings(standingsData);
        setRounds(roundsData);
      } catch (error) {
        console.error("Failed to fetch results:", error);
      } finally {
        setLoading(false);
      }
    })();
  }, [season]);

  const handleYearChange = (newYear: string) => {
    router.push(`/results/${newYear}`);
  };

  const handleRoundClick = (round: number, sessionType: string) => {
    if (sessionType === "sprint_race") {
      router.push(`/results/${season}/${round}/sprint`);
    } else {
      router.push(`/results/${season}/${round}`);
    }
  };

  if (loading) {
    return (
      <main className="min-h-screen bg-[#15151e] p-8">
        <div className="max-w-7xl mx-auto">
          <p className="text-center text-gray-400">Loading results...</p>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-[#15151e] p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header with year selector */}
        <div className="mb-8 flex items-center justify-between">
          <h1 className="text-4xl font-bold text-white">
            {season} Season Results
          </h1>

          {/* Year Dropdown */}
          <select
            value={season}
            onChange={(e) => handleYearChange(e.target.value)}
            className="px-4 py-2 border border-[#2a2a35] rounded-lg bg-[#1e1e28] text-lg text-white font-semibold focus:outline-none focus:ring-2 focus:ring-[#a020f0]"
          >
            {availableYears.map((year) => (
              <option key={year} value={year}>
                {year}
              </option>
            ))}
          </select>
        </div>

        {/* Final Standings Section */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-bold text-white">
              {season} Final Standings
            </h2>
            <button
              type="button"
              onClick={() => setExpandedStandings(!expandedStandings)}
              className="px-4 py-2 bg-[#a020f0] text-white rounded-lg hover:bg-[#7209b7] transition-colors"
            >
              {expandedStandings ? "Show Top 5" : "Show All"}
            </button>
          </div>

          {/* Driver and Constructor Standings Side by Side */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Driver Standings */}
            <div className="bg-[#1e1e28] rounded-lg border border-[#2a2a35] shadow-lg p-6">
              <h3 className="text-xl font-bold text-white mb-4">
                Driver Standings
              </h3>
              <div className="space-y-3">
                {standings?.drivers
                  .slice(0, expandedStandings ? undefined : 5)
                  .map((driver, idx) => (
                    <div
                      key={`${driver.driver_code}-${driver.team_name}-${idx}`}
                      className="flex items-center gap-3 pb-3 border-b border-[#2a2a35] last:border-0"
                    >
                      {/* Position */}
                      <div className="text-2xl font-bold text-gray-500 w-8">
                        {driver.position}
                      </div>

                      {/* Driver Photo */}
                      {driver.headshot_url &&
                        driver.headshot_url !== "None" && (
                          <Image
                            src={driver.headshot_url}
                            alt={driver.full_name}
                            width={48}
                            height={48}
                            className="rounded-full object-cover border-2 border-white"
                          />
                        )}

                      {/* Driver Info */}
                      <div className="flex-1">
                        <div className="font-semibold text-white">
                          {driver.full_name}
                        </div>
                        <div
                          className="text-sm font-medium"
                          style={{
                            color: driver.team_color
                              ? `#${driver.team_color}`
                              : "#999",
                          }}
                        >
                          {driver.team_name}
                        </div>
                      </div>

                      {/* Points */}
                      <div className="text-xl font-bold text-white">
                        {driver.total_points}
                      </div>
                    </div>
                  ))}
              </div>
            </div>

            {/* Constructor Standings */}
            <div className="bg-[#1e1e28] rounded-lg border border-[#2a2a35] shadow-lg p-6">
              <h3 className="text-xl font-bold text-white mb-4">
                Constructor Standings
              </h3>
              <div className="space-y-3">
                {standings?.constructors
                  .slice(0, expandedStandings ? undefined : 5)
                  .map((team, idx) => (
                    <div
                      key={`${team.team_name}-${idx}`}
                      className="flex items-center gap-3 pb-3 border-b border-[#2a2a35] last:border-0"
                    >
                      {/* Position */}
                      <div className="text-2xl font-bold text-gray-500 w-8">
                        {team.position}
                      </div>

                      {/* Team Info */}
                      <div className="flex-1">
                        <div
                          className="font-bold text-lg"
                          style={{
                            color: team.team_color
                              ? `#${team.team_color}`
                              : "#fff",
                          }}
                        >
                          {team.team_name}
                        </div>
                      </div>

                      {/* Points */}
                      <div className="text-xl font-bold text-white">
                        {team.total_points}
                      </div>
                    </div>
                  ))}
              </div>
            </div>
          </div>
        </div>

        {/* Races Section */}
        <div>
          <h2 className="text-2xl font-bold text-white mb-4">All Races</h2>
          <div className="space-y-4">
            {rounds?.rounds.map((round) => (
              <button
                type="button"
                key={`${round.round}-${round.session_type}`}
                onClick={() =>
                  handleRoundClick(round.round, round.session_type)
                }
                className="w-full bg-[#1e1e28] border border-[#2a2a35] rounded-lg shadow-lg p-6 hover:border-[#a020f0] transition-all cursor-pointer text-left"
              >
                {/* Race Header - Horizontal */}
                <div className="flex items-center justify-between mb-4 pb-3 border-b border-[#2a2a35]">
                  <div>
                    <h3 className="text-xl font-bold text-white">
                      <span className="text-gray-400 font-normal">
                        Round {round.round}
                      </span>{" "}
                      • {round.event_name}
                    </h3>
                    <p className="text-sm text-gray-400">
                      {round.circuit_name} •{" "}
                      {new Date(round.date).toLocaleDateString("en-US", {
                        month: "long",
                        day: "numeric",
                        year: "numeric",
                      })}
                    </p>
                  </div>
                  {round.session_type === "sprint_race" && (
                    <span className="bg-[#a020f0] text-white px-3 py-1 rounded-full text-sm font-semibold">
                      SPRINT
                    </span>
                  )}
                </div>

                {/* Podium - Horizontal Layout */}
                <div className="flex items-center justify-between gap-6">
                  {round.podium.map((driver, idx) => {
                    const medals = ["🥇", "🥈", "🥉"];

                    return (
                      <div
                        key={driver.driver_code}
                        className="flex items-center gap-3 flex-1"
                      >
                        {/* Medal */}
                        <span className="text-3xl">{medals[idx]}</span>

                        {/* Driver Photo */}
                        {driver.headshot_url &&
                          driver.headshot_url !== "None" && (
                            <Image
                              src={driver.headshot_url}
                              alt={driver.full_name}
                              width={56}
                              height={56}
                              className="rounded-full object-cover border-2 border-white"
                            />
                          )}

                        {/* Driver Info */}
                        <div className="flex-1">
                          <div className="font-bold text-white">
                            {driver.driver_code}
                          </div>
                          <div
                            className="text-sm font-semibold"
                            style={{
                              color: driver.team_color
                                ? `#${driver.team_color}`
                                : "#999",
                            }}
                          >
                            {driver.team_name}
                          </div>
                          {driver.fastest_lap && (
                            <div className="text-xs text-[#c77dff] font-semibold">
                              ⚡ Fastest Lap
                            </div>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </button>
            ))}
          </div>
        </div>
      </div>
    </main>
  );
}
