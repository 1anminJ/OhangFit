"use client";

import { useEffect, useState, FormEvent } from "react";
import { useParams } from "next/navigation";
import { OnboardingForm } from "@/components/OnboardingForm";
import {
  getProfile,
  updateProfile,
  getAnalysis,
  createAnalysis,
  getCuration,
  createLead,
  signup,
  login,
  createPayment,
} from "@/lib/api";
import type { Profile, ProfileInput, AnalysisResult, Curation } from "@/lib/api";

export default function ProfileDetailPage() {
  const params = useParams<{ id: string }>();
  const [profile, setProfile] = useState<Profile | null>(null);
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [curation, setCuration] = useState<Curation | null>(null);
  const [needsEmail, setNeedsEmail] = useState(false);
  const [editing, setEditing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [email, setEmail] = useState("");
  const [emailSubmitting, setEmailSubmitting] = useState(false);
  const [emailError, setEmailError] = useState<string | null>(null);
  const [magicLinkUrl, setMagicLinkUrl] = useState<string | null>(null);

  const [password, setPassword] = useState("");
  const [payingSubmitting, setPayingSubmitting] = useState(false);
  const [payError, setPayError] = useState<string | null>(null);

  useEffect(() => {
    getProfile(params.id)
      .then(setProfile)
      .catch((err) =>
        setError(err instanceof Error ? err.message : "불러오지 못했습니다.")
      );
  }, [params.id]);

  useEffect(() => {
    if (!profile) return;
    getAnalysis(profile.id)
      .catch(() => createAnalysis(profile.id))
      .then(setAnalysis)
      .catch((err) =>
        setError(err instanceof Error ? err.message : "분석에 실패했습니다.")
      );
  }, [profile]);

  function loadCuration(profileId: string) {
    getCuration(profileId)
      .then((result) => {
        setCuration(result);
        setNeedsEmail(false);
      })
      .catch(() => setNeedsEmail(true));
  }

  useEffect(() => {
    if (!analysis) return;
    loadCuration(analysis.profile_id);
  }, [analysis]);

  async function handleUpdate(values: ProfileInput) {
    const updated = await updateProfile(params.id, values);
    setProfile(updated);
    setEditing(false);
    setAnalysis(await createAnalysis(updated.id));
  }

  async function handleEmailSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!profile) return;
    setEmailError(null);
    setEmailSubmitting(true);
    try {
      const lead = await createLead(profile.id, email);
      setMagicLinkUrl(lead.magic_link_url);
      loadCuration(profile.id);
    } catch (err) {
      setEmailError(err instanceof Error ? err.message : "이메일 등록에 실패했습니다.");
    } finally {
      setEmailSubmitting(false);
    }
  }

  async function handlePaySubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!profile) return;
    setPayError(null);
    setPayingSubmitting(true);
    try {
      try {
        await signup(email, password);
      } catch {
        await login(email, password);
      }
      await createPayment(profile.id);
      loadCuration(profile.id);
    } catch (err) {
      setPayError(err instanceof Error ? err.message : "결제에 실패했습니다.");
    } finally {
      setPayingSubmitting(false);
    }
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

      {needsEmail && (
        <form onSubmit={handleEmailSubmit} className="flex flex-col gap-3 max-w-sm">
          <p>이메일을 입력하면 결과를 보내드려요.</p>
          <input
            type="email"
            required
            placeholder="you@example.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="border rounded px-3 py-2"
          />
          {emailError && <p className="text-red-600 text-sm">{emailError}</p>}
          <button
            type="submit"
            disabled={emailSubmitting}
            className="bg-black text-white rounded px-4 py-2 disabled:opacity-50"
          >
            {emailSubmitting ? "처리 중..." : "이메일 제출"}
          </button>
        </form>
      )}

      {magicLinkUrl && (
        <p className="text-sm text-gray-500 mt-2">
          (개발용) 결과 조회 링크: {magicLinkUrl}
        </p>
      )}

      {curation && curation.locked && (
        <div className="mt-4">
          <p className="mb-3">
            컬러/아이템은 결제 후에 볼 수 있어요. 회원가입하고 결제하면 바로 잠금
            해제됩니다. (이메일은 위에서 입력한 것을 그대로 쓰는 걸 권장해요)
          </p>
          <form onSubmit={handlePaySubmit} className="flex flex-col gap-3 max-w-sm">
            <input
              type="email"
              required
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="border rounded px-3 py-2"
            />
            <input
              type="password"
              required
              placeholder="비밀번호"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="border rounded px-3 py-2"
            />
            {payError && <p className="text-red-600 text-sm">{payError}</p>}
            <button
              type="submit"
              disabled={payingSubmitting}
              className="bg-black text-white rounded px-4 py-2 disabled:opacity-50"
            >
              {payingSubmitting ? "처리 중..." : "회원가입하고 결제하기"}
            </button>
          </form>
        </div>
      )}

      {curation && !curation.locked && (
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
