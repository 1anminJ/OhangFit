"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { getProfileIdByToken } from "@/lib/api";

export default function MagicLinkPage() {
  const params = useParams<{ token: string }>();
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getProfileIdByToken(params.token)
      .then((result) => router.replace(`/onboarding/${result.profile_id}`))
      .catch((err) =>
        setError(err instanceof Error ? err.message : "유효하지 않은 링크입니다.")
      );
  }, [params.token, router]);

  if (error) return <main className="p-6 text-red-600">{error}</main>;
  return <main className="p-6">이동 중...</main>;
}
