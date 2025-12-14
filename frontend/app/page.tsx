/**
 * Home Page - Displays 2024 F1 Race Winners
 *
 * This is a Server Component (default in Next.js App Router)
 * It fetches data from your FastAPI backend and displays it.
 */

// Define the type for our race data (matches your Pydantic schema)
type RaceWinner = {
  round: number;
  race_name: string;
  date: string;
  winner_name: string;
  winner_team: string;
  winner_had_fastest_lap: boolean;
  driver_photo_url?: string;
};

// Fetch data from your FastAPI backend
async function getRaces(): Promise<RaceWinner[]> {
  const res = await fetch('http://localhost:8000/api/races/2024', {
    cache: 'no-store', // Always fetch fresh data (good for development)
  });

  if (!res.ok) {
    throw new Error('Failed to fetch races');
  }

  return res.json();
}

// Main page component
export default async function Home() {
  const races = await getRaces();

  return (
    <main className="min-h-screen bg-[#15151e] p-8">
      <div className="max-w-7xl mx-auto">
        {/* Page Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">
            2024 F1 Season
          </h1>
          <p className="text-gray-400">
            Race winners and fastest laps
          </p>
        </div>

        {/* Race Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {races.map((race) => (
            <div
              key={race.round}
              className="bg-[#1e1e28] border border-[#2a2a35] rounded-lg shadow-lg p-6 hover:border-[#a020f0] transition-all"
            >
              {/* Race Header */}
              <div className="mb-4">
                <div className="text-sm text-gray-400 mb-1">
                  Round {race.round}
                </div>
                <h2 className="text-xl font-bold text-white mb-2">
                  {race.race_name}
                </h2>
                <div className="text-sm text-gray-400">
                  {new Date(race.date).toLocaleDateString('en-US', {
                    month: 'long',
                    day: 'numeric',
                    year: 'numeric'
                  })}
                </div>
              </div>

              {/* Winner Info */}
              <div className="border-t border-[#2a2a35] pt-4">
                <div className="text-sm text-gray-400 mb-1">Winner</div>
                <div className="font-semibold text-lg text-white">
                  {race.winner_name}
                </div>
                <div className="text-sm text-gray-300 mt-1">
                  {race.winner_team}
                </div>

                {/* Fastest Lap Badge */}
                {race.winner_had_fastest_lap && (
                  <div className="mt-3">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-[#a020f0]/20 text-[#c77dff]">
                      ⚡ Fastest Lap
                    </span>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}
