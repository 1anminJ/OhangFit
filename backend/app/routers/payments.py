from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.adapters.payment import MockPaymentAdapter
from app.db import get_db
from app.models.account import Account
from app.models.payment import Payment
from app.models.profile import Profile
from app.schemas.payment import PaymentRead

router = APIRouter(prefix="/profiles/{profile_id}/payment", tags=["payments"])

AMOUNT = 9900  # ponytail: 가격 정책 TBD(PRD), 정해지면 설정값으로 분리

# ponytail: PG 벤더가 정해지기 전까지는 목업 어댑터 하나만 씀.
_payment_adapter = MockPaymentAdapter()


@router.post("", response_model=PaymentRead)
def create_payment(profile_id: UUID, db: Session = Depends(get_db)) -> Payment:
    profile = db.get(Profile, profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="프로필을 찾을 수 없습니다.")
    if profile.account_id is None:
        raise HTTPException(status_code=404, detail="이메일을 먼저 입력해주세요.")

    account = db.get(Account, profile.account_id)
    if account.role != "member":
        raise HTTPException(status_code=403, detail="회원가입이 필요합니다.")

    success = _payment_adapter.charge(AMOUNT)
    payment = Payment(
        account_id=account.id,
        profile_id=profile_id,
        amount=AMOUNT,
        status="success" if success else "failed",
        paid_at=datetime.now(timezone.utc) if success else None,
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)

    if not success:
        raise HTTPException(status_code=402, detail="결제에 실패했습니다.")

    return payment
