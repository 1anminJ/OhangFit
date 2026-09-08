const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type Gender = "male" | "female";

export interface ProfileInput {
  birth_date: string; // YYYY-MM-DD
  birth_time: string | null; // HH:MM:SS
  birth_time_unknown: boolean;
  gender: Gender;
  birth_region: string;
}

export interface Profile extends ProfileInput {
  id: string;
  created_at: string;
  updated_at: string;
}

export interface AnalysisResult {
  id: string;
  profile_id: string;
  five_elements: Record<string, number>;
  missing_elements: string[];
  excess_elements: string[];
  sinsal: string[];
  created_at: string;
  updated_at: string;
}

export interface ColorMapping {
  element: string;
  color_name: string;
  hex_code: string | null;
}

export interface CurationItem {
  id: string;
  element: string;
  name: string;
  category: string;
  image_url: string;
}

export interface Curation {
  missing_elements: string[];
  colors: ColorMapping[];
  items: CurationItem[];
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const body = await response.json().catch(() => ({ detail: null }));
    const detail = (body as { detail?: unknown }).detail;
    if (typeof detail === "string") {
      throw new Error(detail);
    }
    if (Array.isArray(detail)) {
      const messages = detail
        .map((item) =>
          item && typeof item === "object" && "msg" in item
            ? String((item as { msg: unknown }).msg).replace(/^Value error,\s*/, "")
            : null
        )
        .filter((msg): msg is string => Boolean(msg));
      if (messages.length > 0) {
        throw new Error(messages.join(" / "));
      }
    }
    throw new Error("요청을 처리하지 못했습니다.");
  }
  return response.json() as Promise<T>;
}

export async function createProfile(input: ProfileInput): Promise<Profile> {
  const response = await fetch(`${API_BASE_URL}/profiles`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });
  return handleResponse<Profile>(response);
}

export async function getProfile(id: string): Promise<Profile> {
  const response = await fetch(`${API_BASE_URL}/profiles/${id}`);
  return handleResponse<Profile>(response);
}

export async function updateProfile(
  id: string,
  input: Partial<ProfileInput>
): Promise<Profile> {
  const response = await fetch(`${API_BASE_URL}/profiles/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });
  return handleResponse<Profile>(response);
}

export async function createAnalysis(profileId: string): Promise<AnalysisResult> {
  const response = await fetch(`${API_BASE_URL}/profiles/${profileId}/analysis`, {
    method: "POST",
  });
  return handleResponse<AnalysisResult>(response);
}

export async function getAnalysis(profileId: string): Promise<AnalysisResult> {
  const response = await fetch(`${API_BASE_URL}/profiles/${profileId}/analysis`);
  return handleResponse<AnalysisResult>(response);
}

export async function getCuration(profileId: string): Promise<Curation> {
  const response = await fetch(`${API_BASE_URL}/profiles/${profileId}/curation`);
  return handleResponse<Curation>(response);
}
