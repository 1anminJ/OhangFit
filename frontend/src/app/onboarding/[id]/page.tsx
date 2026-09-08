"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { OnboardingForm } from "@/components/OnboardingForm";
import {
  getProfile,
  updateProfile,
  getAnalysis,
  createAnalysis,
  getCuration,
} from "@/lib/api";
import type { Profile, ProfileInput, AnalysisResult, Curation } from "@/lib/api";

export default function ProfileDetailPage() {
  const params = useParams<{ id: string }>();
  const [profile, setProfile] = useState<Profile | null>(null);
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [curation, setCuration] = useState<Curation | null>(null);
  const [editing, setEditing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getProfile(params.id)
      .then(setProfile)
      .catch((err) =>
        setError(err instanceof Error ? err.message : "불러오지 못했습니다.")
      );
  }, [params.id]);

  useEffect(() => {
    if (!profile) return;
    // 저장된 분석이 있으면 그대로 쓰고, 없으면(첫 방문) 자동으로 분석을 실행한다.
    getAnalysis(profile.id)
      .catch(() => createAnalysis(profile.id))
      .then(setAnalysis)
      .catch((err) =>
        setError(err instanceof Error ? err.message : "분석에 실패했습니다.")
      );
  }, [profile]);

  useEffect(() => {
    if (!analysis) return;
    getCuration(analysis.profile_id)
      .then(setCuration)
      .catch((err) =>
        setError(err instanceof Error ? err.message : "큐레이션을 불러오지 못했습니다.")
      );
  }, [analysis]);

  async function handleUpdate(values: ProfileInput) {
    const updated = await updateProfile(params.id, values);
    setProfile(updated);
    setEditing(false);
    setAnalysis(await createAnalysis(updated.id));
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

      <h2 className="text-lg font-bold mt-8 mb-2">오행 분석</h2>
      {!analysis ? (
        <p>분석 중...</p>
      ) : (
        <dl className="flex flex-col gap-2">
          <div>
            오행 분포:{" "}
            {Object.entries(analysis.five_elements)
              .map(([element, count]) => `${element} ${count}`)
              .join(" · ")}
          </div>
          <div>부족한 오행: {analysis.missing_elements.join(", ")}</div>
          <div>과다한 오행: {analysis.excess_elements.join(", ")}</div>
        </dl>
      )}

      <h2 className="text-lg font-bold mt-8 mb-2">오늘의 컬러</h2>
      {!curation ? (
        <p>불러오는 중...</p>
      ) : (
        <>
          <ul className="flex gap-3 mb-6">
            {curation.colors.map((color) => (
              <li key={color.color_name} className="flex flex-col items-center gap-1">
                <span
                  className="w-8 h-8 rounded-full border"
                  style={{ backgroundColor: color.hex_code ?? undefined }}
                />
                <span className="text-sm">{color.color_name}</span>
              </li>
            ))}
          </ul>

          <h2 className="text-lg font-bold mb-2">오늘의 추천 아이템</h2>
          <ul className="flex flex-col gap-2">
            {curation.items.map((item) => (
              <li key={item.id} className="flex items-center gap-3 border rounded p-2">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src={item.image_url} alt={item.name} className="w-12 h-12 object-cover" />
                <div>
                  <div>{item.name}</div>
                  <div className="text-sm text-gray-500">{item.category}</div>
                </div>
              </li>
            ))}
          </ul>
        </>
      )}
    </main>
  );
}
