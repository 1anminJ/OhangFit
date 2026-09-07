"use client";

import { useRouter } from "next/navigation";
import { OnboardingForm } from "@/components/OnboardingForm";
import { createProfile } from "@/lib/api";
import type { ProfileInput } from "@/lib/api";

export default function OnboardingPage() {
  const router = useRouter();

  async function handleSubmit(values: ProfileInput) {
    const profile = await createProfile(values);
    router.push(`/onboarding/${profile.id}`);
  }

  return (
    <main className="p-6">
      <h1 className="text-xl font-bold mb-4">사주 정보 입력</h1>
      <OnboardingForm submitLabel="저장하기" onSubmit={handleSubmit} />
    </main>
  );
}
