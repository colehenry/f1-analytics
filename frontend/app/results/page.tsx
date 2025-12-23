import { redirect } from "next/navigation";
import { apiUrl, apiHeaders } from "@/lib/api";

async function getLatestSeason(): Promise<number> {
  const res = await fetch(apiUrl("/api/results/seasons"), {
        headers: apiHeaders(),
    cache: "no-store",
  });

  if (!res.ok) {
    // Fallback to 2024 if API fails
    return 2024;
  }

  const seasons: number[] = await res.json();
  // Return the highest season number
  return Math.max(...seasons);
}

export default async function ResultsPage() {
  const latestSeason = await getLatestSeason();
  redirect(`/results/${latestSeason}`);
}
