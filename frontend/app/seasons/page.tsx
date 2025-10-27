"use client";

import Image from "next/image";
import { useEffect, useState } from "react";

type RacePodium = {
	year: number;
	round: number;
	race_name: string;
	date: string; // Will be ISO date string from API
	podium_drivers: string[]; // 3 drivers
	podium_teams: string[]; // 3 teams
	podium_colors: string[]; // 3 hex colors
	podium_fastest_laps: boolean[]; // 3 booleans
	headshot_urls: string[]; // 3 URLs
};

export default function SeasonsPage() {
	const [selectedYear, setSelectedYear] = useState<number | null>(null);
	const [availableYears, setAvailableYears] = useState<number[]>([]);
	const [podiums, setPodiums] = useState<RacePodium[]>([]);
	const [loading, setLoading] = useState<boolean>(true);

	useEffect(() => {
		// async function to fetch years auto-called
		(async () => {
			try {
				setLoading(true);
				const response = await fetch(
					"http://localhost:8000/api/races/seasons",
					{
						cache: "no-store",
					},
				);
				const years = await response.json();
				setAvailableYears(years);

				if (years.length > 0) {
					setSelectedYear(years[0]);
				}
			} catch (error) {
				console.log("Failed to fetch years:", error);
			} finally {
				setLoading(false);
			}
		})(); //extra parens call the function immediately
	}, []);

	useEffect(() => {
		//resets podiums on change of selected year
		if (!selectedYear) return;

		(async () => {
			try {
				setLoading(true);
				const response = await fetch(
					`http://localhost:8000/api/podiums/${selectedYear}`,
					{
						cache: "no-store",
					},
				);
				const data = await response.json();
				setPodiums(data);
				console.log("Podiums:", data);
			} catch (error) {
				console.log("Failed to fetch podiums:", error);
			} finally {
				setLoading(false);
			}
		})();
	}, [selectedYear]);

	return (
		<main className="min-h-screen bg-gray-50 p-8">
			<div className="max-w-7xl mx-auto">
				{/* Header with year selector */}

				<div className="mb-8 flex items-center justify-between">
					<div>
						<h1 className="text-4xl font-bold text-gray-900 mb-2">
							{selectedYear} Race Results
						</h1>
					</div>

					{/* Year Dropdown */}
					<select
						value={selectedYear || ""}
						onChange={(e) => setSelectedYear(Number(e.target.value))}
						className="px-4 py-2 border border-gray-300 rounded-lg bg-white text-lg text-gray-900 font-semibold focus:outline-none focus:ring-2 focus:ring-blue-500"
					>
						{availableYears.map((year) => (
							<option key={year} value={year}>
								{year}
							</option>
						))}
					</select>
				</div>

				{/* Loading state */}
				{loading ? (
					<p className="text-center text-gray-600">Loading races...</p>
				) : (
					<div className="space-y-6">
						{podiums.map((race) => (
							<div
								key={race.round}
								className="bg-white rounded-lg shadow-md p-4 hover:shadow-lg transition-shadow"
							>
								{/* Race Header - Compact */}
								<div className="flex items-center justify-between mb-3 pb-2 border-b border-gray-200">
									<h2 className="text-lg font-bold text-gray-900">
										<span className="text-gray-500 font-normal">
											Round {race.round}
										</span>{" "}
										• {race.race_name}
									</h2>
									<div className="text-sm text-gray-600">
										{new Date(race.date).toLocaleDateString("en-US", {
											month: "short",
											day: "numeric",
										})}
									</div>
								</div>

								{/* Podium Finishers - Horizontal Rows */}
								<div className="space-y-2">
									{[0, 1, 2].map((position) => {
										const medals = ["🥇", "🥈", "🥉"];

										return (
											<div key={position} className="flex items-center gap-3">
												{/* Driver Photo */}
												<Image
													src={race.headshot_urls[position]}
													alt={race.podium_drivers[position]}
													width={40}
													height={40}
													className="rounded-full object-cover border-2 border-gray-200"
												/>

												{/* Medal */}
												<span className="text-2xl">{medals[position]}</span>

												{/* Driver Name */}
												<span className="font-semibold text-gray-900">
													{race.podium_drivers[position]}
												</span>

												{/* Separator */}
												<span className="text-gray-400">•</span>

												{/* Team Name with Color */}
												<span
													className="font-bold"
													style={{ color: `#${race.podium_colors[position]}` }}
												>
													{race.podium_teams[position]}
												</span>

												{/* Fastest Lap Indicator */}
												{race.podium_fastest_laps[position] && (
													<span className="ml-2 text-purple-600 font-semibold text-sm">
														⚡ Fastest Lap
													</span>
												)}
											</div>
										);
									})}
								</div>
							</div>
						))}
					</div>
				)}
			</div>
		</main>
	);
}
