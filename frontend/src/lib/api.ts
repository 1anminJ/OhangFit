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
  locked: boolean;
}

export interface LeadResult {
  account_id: string;
  email: string;
  role: string;
  magic_link_url: string;
}

export interface AuthResult {
  profile_id: string;
}

export interface Payment {
  id: string;
  profile_id: string;
  amount: number;
  status: string;
  paid_at: string | null;
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

export async function createLead(profileId: string, email: string): Promise<LeadResult> {
  const response = await fetch(`${API_BASE_URL}/leads`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ profile_id: profileId, email }),
  });
  return handleResponse<LeadResult>(response);
}

export async function getProfileIdByToken(token: string): Promise<AuthResult> {
  const response = await fetch(`${API_BASE_URL}/leads/by-token/${token}`);
  return handleResponse<AuthResult>(response);
}

export async function signup(email: string, password: string): Promise<AuthResult> {
  const response = await fetch(`${API_BASE_URL}/signup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  return handleResponse<AuthResult>(response);
}

export async function login(email: string, password: string): Promise<AuthResult> {
  const response = await fetch(`${API_BASE_URL}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  return handleResponse<AuthResult>(response);
}

export async function createPayment(profileId: string): Promise<Payment> {
  const response = await fetch(`${API_BASE_URL}/profiles/${profileId}/payment`, {
    method: "POST",
  });
  return handleResponse<Payment>(response);
}
