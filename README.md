# 🔮 Emosic: 감정 기반 음악 추천 시스템 (Emotion-based Music Recommendation)

> **"당신의 기분을 음악으로 번역해 드립니다."** > 사용자의 감정(자연어)을 분석하여, Spotify API를 통해 분위기에 딱 맞는 음악을 추천해주는 AI 큐레이션 서비스입니다.

<br>

## 📌 프로젝트 소개 (Introduction)
기존 음악 스트리밍 서비스의 단순 장르/인기도 기반 추천의 한계를 넘어, **사용자의 구체적인 감정 상태(Context)**를 반영하는 음악 추천 시스템입니다.  
사용자가 일기 쓰듯 자신의 기분을 적으면, KoTE(한국어 감정 분석) 모델이 44가지 미세 감정을 분석하고, 스포티파이의 Audio Features(Valence, Energy)와 매핑하여 최적의 곡을 추천합니다.

<br>

## ✨ 주요 기능 (Key Features)
* **🎶 감정 분석 (Emotion Analysis)**: KoTE(Korean Online Text Emotions) 모델을 활용하여 텍스트에서 44가지 세밀한 감정을 추출합니다.
* **🎯 맞춤형 추천 (Personalized Curation)**: 사용자의 스포티파이 청취 기록(Top Artists)을 기반으로 취향을 반영한 추천을 제공합니다.
* **🔄 피드백 루프 (Feedback Loop)**: 추천 결과에 대한 만족도를 반영하여, 다음 추천 시 알고리즘(정밀 매칭 vs 랜덤 탐색)을 자동으로 조정합니다.
* **🔐 소셜 로그인 (Social Login)**: Spotify OAuth 2.0을 통해 안전하게 로그인하고 개인화된 서비스를 이용할 수 있습니다.
* **🎨 감성 UI (Glassmorphism)**: 몰입감을 높이는 글래스모피즘 디자인을 적용했습니다.

<br>

## 🛠 기술 스택 (Tech Stack)

| 분류 | 기술 |
| :--- | :--- |
| **Frontend** | HTML5, CSS3 (Glassmorphism UI) |
| **Backend** | Python, Flask |
| **AI / NLP** | PyTorch, Hugging Face Transformers (KoTE Model) |
| **API** | Spotify Web API (Spotipy Library) |
| **Deployment** | Local Server (Port 8080) |

<br>

## 🚀 설치 및 실행 방법 (Installation)

이 프로젝트를 로컬 환경에서 실행하려면 **Spotify Developer 계정**이 필요합니다.

### 1. 레포지토리 클론 (Clone)
```bash
git clone [https://github.com/sunwoo0421/Emosic.git](https://github.com/sunwoo0421/Emosic.git)
cd Emosic
```

### 2. 가상 환경 설정 (Optional)
파이썬 프로젝트의 독립적인 실행 환경을 위해 가상 환경 생성을 권장합니다.

**Windows**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. 필수 라이브러리 설치
프로젝트 실행에 필요한 Python 패키지들을 설치합니다.

```bash
pip install -r requirements.txt
```

### 4. 환경 변수 설정 (.env)

보안을 위해 API Key는 소스 코드에 포함되지 않습니다.
프로젝트 최상위 경로에 .env 파일을 생성하고, Spotify for Developers에서 발급받은 키를 입력하세요.
파일명: .env

```Ini, TOML
SPOTIFY_CLIENT_ID=your_client_id_here
SPOTIFY_CLIENT_SECRET=your_client_secret_here
SPOTIFY_REDIRECT_URI=http://localhost:8080/callback
FLASK_SECRET_KEY=emosic_secret_key_1234
```

5. 서버 실행
모든 설정이 완료되면 아래 명령어로 Flask 서버를 실행합니다.

```Bash
python main.py
```

터미널에 서버 실행 로그가 뜨면 브라우저를 엽니다.

주소창에 http://localhost:8080 을 입력하여 접속합니다.

[Spotify 로그인] 버튼을 눌러 인증 후 서비스를 이용합니다. (최초 실행 시 AI 모델 다운로드로 인해 약 1~2분 정도 소요될 수 있습니다.)



