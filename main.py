import os
import sys
from flask import Flask, render_template, request, redirect, url_for, session
from dotenv import load_dotenv

# 모듈 경로 설정 (현재 폴더를 path에 추가)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 필요한 모듈 임포트
from input.input_handler import get_user_input
from training.kote_inference import predict_emotions
from spotify.spotify_recommender import SpotifyRecommender
from feedback.feedback_handler import compute_feedback_factor

# .env 파일 로드
load_dotenv()

app = Flask(__name__)
app.secret_key = "emosic_secret_key"  # 세션 보안키

# 환경변수 확인
CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")

if not all([CLIENT_ID, CLIENT_SECRET, REDIRECT_URI]):
    print("❌ 오류: .env 파일에 Spotify API 키가 설정되지 않았습니다.")
    sys.exit(1)

# 추천기 객체 생성
recommender = SpotifyRecommender(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI)

# ----------------------
#  로그인 체크 (미들웨어)
# ----------------------
@app.before_request
def check_token():
    whitelist = ["home", "login", "callback", "static"]
    if request.endpoint in whitelist:
        return
    
    # 결과 페이지 접근 시 로그인이 안 되어 있으면 로그인 페이지로
    if request.endpoint == 'result' and not session.get('spotify_token'):
         return redirect(url_for('login'))

# ----------------------
#  라우트
# ----------------------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login")
def login():
    auth_url = recommender.get_auth_url()
    return redirect(auth_url)

@app.route("/callback")
def callback():
    code = request.args.get("code")
    if code:
        try:
            recommender.authenticate(code)
            session['spotify_token'] = True # 로그인 성공 표시
            return render_template("callback.html")
        except Exception as e:
            return f"로그인 오류: {e}"
    return "코드가 없습니다."

@app.route("/result", methods=["POST"])
def result():
    if not session.get('spotify_token'):
        return redirect(url_for('login'))

    try:
        text = request.form.get("text")
        cleaned = get_user_input(text)
        
        # 감정 분석
        raw_emotions = predict_emotions([cleaned])
        primary_emotion = raw_emotions[0][0] if raw_emotions and raw_emotions[0] else "평온함"
        
        # [피드백 반영] 세션에서 지난번 점수 가져오기 (없으면 0)
        last_score = int(session.get('last_score', 0))
        
        # 추천 요청 (감정과 지난 점수 전달)
        tracks = recommender.recommend(
            limit=9, 
            emotion=primary_emotion, 
            last_score=last_score
        )

        session["last_emotion"] = primary_emotion
        session["last_input"] = cleaned

        return render_template(
            "result.html",
            emotion_result=primary_emotion,
            tracks=tracks,
            user_text=cleaned
        )

    except Exception as e:
        print(f"🔥 서버 오류: {e}")
        return render_template("index.html", error="오류 발생")

@app.route("/feedback", methods=["POST"])
def feedback():
    match = request.form.get("match")
    score = request.form.get("score")

    if match and score:
        # [중요] 다음 추천을 위해 점수를 세션에 저장
        session['last_score'] = score
        
        # CSV 저장 (기존 코드 유지)
        # ... (CSV 저장 코드 생략) ...
        print(f"📝 피드백 반영: 다음 추천에 점수({score}) 적용됨")

    return redirect(url_for('home'))

@app.route("/logout")
def logout():
    # 세션에 저장된 모든 정보(토큰, 이전 점수, 감정 등)를 싹 지웁니다.
    session.clear()
    
    # 첫 화면으로 돌아갑니다.
    return redirect(url_for('home'))

if __name__ == "__main__":
    # 포트는 .env의 Redirect URI와 일치해야 함 (보통 8080)
    app.run(port=8080, debug=True)