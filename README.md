# 별사탕인편 봇

훈련병에게 사회 소식을 인터넷으로 자동으로 발송해주는 (별사탕인편)[https://star-candy-letter.netlify.app/]의 크롤링 & 발송 봇입니다.

크롤링 by (@CRISPYTYPER)[https://github.com/CRISPYTYPER]

## 문의

세팅, 사용법, 버그 제보 등은 이슈로 남기거나 suno.vivid@gmail.com 으로 연락주세요.

## 프로젝트 세팅

```
git clone https://github.com/sunovivid/starcandyletter-transferbot-public.git

pip install -r requirements.txt
```

## 설정

다음의 환경 변수를 직접 추가하거나 .env 파일로 설정해주어야 합니다.

```
# .env

ADMIN_EMAIL=Firebase Realtime Database 보안 규칙에 관리자 권한으로 추가한 계정
ADMIN_PASSWORD=위 **Firebase** 계정의 비밀번호
FIREBASE_API_KEY=Firebase API Key (Firebase 콘솔에서 확인가능)
FIREBASE_AUTH_DOMAIN=Firebase Auth Domain (Firebase 콘솔에서 확인가능)
FIREBASE_DATABASE_URL=Firebase Realtime Database 주소 (Firebase 콘솔에서 확인가능)
MAIL_PASSWORD=공군 별사탕인편의 인터넷편지 비밀번호 설정
THECAMP_ADMIN_EMAIL=육군 인터넷편지를 보낼 THE CAMP 계정
THECAMP_ADMIN_PASSWORD=위 계정의 비밀번호
```

## Prerequisite

Firebase의 Authentication과 Realtime Database를 백엔드로 이용합니다.

Realtime Database의 구조는 별사탕인편 웹페이지 레포지토리(공개 전환 작업 중)를 확인하세요.
