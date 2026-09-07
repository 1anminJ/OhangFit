"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { OnboardingForm } from "@/components/OnboardingForm";
import { getProfile, updateProfile } from "@/lib/api";
import type { Profile, ProfileInput } from "@/lib/api";

export default function ProfileDetailPage() {
  const params = useParams<{ id: string }>();
  const [profile, setProfile] = useState<Profile | null>(null);
  const [editing, setEditing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getProfile(params.id)
      .then(setProfile)
      .catch((err) =>
        setError(err instanceof Error ? err.message : "불러오지 못했습니다.")
      );
  }, [params.id]);

  async function handleUpdate(values: ProfileInput) {
    const updated = await updateProfile(params.id, values);
    setProfile(updated);
    setEditing(false);
  }

  if (error) return <main className="p-6 text-red-600">{error}</main>;
  if (!profile) return <main className="p-6">불러오는 중...</main>;

  if (editing) {
    return (
      <main className="p-6">
        <h1 className="text-xl font-bold mb-4">정보 수정</h1>
        <OnboardingForm
          initialValues={profile}
          submitLabel="수정 완료"
          onSubmit={handleUpdate}
        />
      </main>
    );
  }

  return (
    <main className="p-6">
      <h1 className="text-xl font-bold mb-4">저장된 사주 정보</h1>
      <dl className="flex flex-col gap-2 mb-4">
        <div>생년월일: {profile.birth_date}</div>
        <div>
          출생시간: {profile.birth_time_unknown ? "모름" : profile.birth_time?.slice(0, 5)}
        </div>
        <div>성별: {profile.gender === "male" ? "남성" : "여성"}</div>
        <div>태어난 지역: {profile.birth_region}</div>
      </dl>
      <button onClick={() => setEditing(true)} className="border rounded px-4 py-2">
        수정하기
      </button>
    </main>
  );
}
