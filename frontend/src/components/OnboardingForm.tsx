"use client";

import { useState, FormEvent } from "react";
import type { Gender, ProfileInput } from "@/lib/api";

// 숫자만 입력해도 구분자(-, :)를 자동으로 넣어준다 (예: "20040103" -> "2004-01-03").
function formatDateInput(raw: string): string {
  const digits = raw.replace(/\D/g, "").slice(0, 8);
  let result = digits.slice(0, 4);
  if (digits.length > 4) result += "-" + digits.slice(4, 6);
  if (digits.length > 6) result += "-" + digits.slice(6, 8);
  return result;
}

function formatTimeInput(raw: string): string {
  const digits = raw.replace(/\D/g, "").slice(0, 4);
  let result = digits.slice(0, 2);
  if (digits.length > 2) result += ":" + digits.slice(2, 4);
  return result;
}

export interface OnboardingFormProps {
  initialValues?: ProfileInput;
  submitLabel: string;
  onSubmit: (values: ProfileInput) => Promise<void>;
}

export function OnboardingForm({
  initialValues,
  submitLabel,
  onSubmit,
}: OnboardingFormProps) {
  const [birthDate, setBirthDate] = useState(initialValues?.birth_date ?? "");
  const [birthTime, setBirthTime] = useState(
    initialValues?.birth_time?.slice(0, 5) ?? ""
  );
  const [birthTimeUnknown, setBirthTimeUnknown] = useState(
    initialValues?.birth_time_unknown ?? false
  );
  const [gender, setGender] = useState<Gender>(initialValues?.gender ?? "female");
  const [birthRegion, setBirthRegion] = useState(initialValues?.birth_region ?? "");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await onSubmit({
        birth_date: birthDate,
        birth_time: birthTimeUnknown ? null : birthTime,
        birth_time_unknown: birthTimeUnknown,
        gender,
        birth_region: birthRegion,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "알 수 없는 오류가 발생했습니다.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4 max-w-sm">
      <label className="flex flex-col gap-1">
        생년월일
        <input
          type="text"
          required
          placeholder="YYYY-MM-DD (예: 1990-05-20)"
          value={birthDate}
          onChange={(e) => setBirthDate(formatDateInput(e.target.value))}
          className="border rounded px-3 py-2"
        />
      </label>

      <label className="flex items-center gap-2">
        <input
          type="checkbox"
          checked={birthTimeUnknown}
          onChange={(e) => setBirthTimeUnknown(e.target.checked)}
        />
        출생시간을 몰라요
      </label>

      {!birthTimeUnknown && (
        <label className="flex flex-col gap-1">
          출생시간
          <input
            type="text"
            required={!birthTimeUnknown}
            placeholder="HH:MM (예: 10:30)"
            value={birthTime ?? ""}
            onChange={(e) => setBirthTime(formatTimeInput(e.target.value))}
            className="border rounded px-3 py-2"
          />
        </label>
      )}

      <label className="flex flex-col gap-1">
        성별
        <select
          value={gender}
          onChange={(e) => setGender(e.target.value as Gender)}
          className="border rounded px-3 py-2"
        >
          <option value="female">여성</option>
          <option value="male">남성</option>
        </select>
      </label>

      <label className="flex flex-col gap-1">
        태어난 지역
        <input
          type="text"
          required
          placeholder="예: 서울특별시"
          value={birthRegion}
          onChange={(e) => setBirthRegion(e.target.value)}
          className="border rounded px-3 py-2"
        />
      </label>

      {error && <p className="text-red-600 text-sm">{error}</p>}

      <button
        type="submit"
        disabled={submitting}
        className="bg-black text-white rounded px-4 py-2 disabled:opacity-50"
      >
        {submitting ? "처리 중..." : submitLabel}
      </button>
    </form>
  );
}
