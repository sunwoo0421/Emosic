import spotipy
from spotipy.oauth2 import SpotifyOAuth
import random
# 방금 만든 맵핑 함수 가져오기
from spotify.emotion_map import get_target_features

class SpotifyRecommender:
    def __init__(self, client_id, client_secret, redirect_uri):
        self.scope = "user-read-private user-read-email user-top-read user-read-recently-played"
        self.oauth = SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope=self.scope
        )
        self.sp = spotipy.Spotify(auth_manager=self.oauth)

    def get_auth_url(self):
        return self.oauth.get_authorize_url()
    
    def authenticate(self, code):
        token_info = self.oauth.get_access_token(code)
        self.sp = spotipy.Spotify(auth=token_info["access_token"])

    # ★ 핵심 수정: limit 외에 emotion(현재 감정), last_score(이전 피드백)를 받음
    def recommend(self, limit=9, emotion="평온함", last_score=0):
        if not self.sp:
            raise Exception("Spotify 인증이 필요합니다.")

        recommended_tracks = []
        
        # 1. 감정 -> 목표 수치 변환
        target = get_target_features(emotion)
        target_val = target["valence"]
        target_eng = target["energy"]

        # 2. 전략 결정 (피드백 반영)
        # 점수가 4점 이상이면 '정밀 매칭', 아니면 '랜덤 탐색'
        use_smart_matching = (last_score >= 4)
        mode_text = "🎯 정밀 매칭 (피드백 긍정)" if use_smart_matching else "🎲 랜덤 탐색 (피드백 부족/부정)"
        
        print(f"📡 [Logic] 감정: {emotion} ({target_val}, {target_eng}) | 모드: {mode_text}")

        try:
            top_artists_data = self.sp.current_user_top_artists(limit=5, time_range='short_term')
            
            if top_artists_data and len(top_artists_data['items']) > 0:
                for artist in top_artists_data['items']:
                    artist_id = artist['id']
                    
                    try:
                        # 아티스트의 인기곡 10개 가져오기
                        top_tracks_data = self.sp.artist_top_tracks(artist_id, country='KR')
                        track_list = top_tracks_data['tracks']
                        
                        if not track_list: continue

                        if use_smart_matching:
                            # [전략 A] 정밀 매칭: 오디오 특징을 분석해 감정과 가장 가까운 곡 선택
                            track_ids = [t['id'] for t in track_list]
                            audio_features = self.sp.audio_features(track_ids)
                            
                            # (노래, 특징) 짝짓기
                            scored_tracks = []
                            for t, f in zip(track_list, audio_features):
                                if f:
                                    # 거리 계산 (차이가 작을수록 감정과 비슷함)
                                    diff = abs(f['valence'] - target_val) + abs(f['energy'] - target_eng)
                                    scored_tracks.append((diff, t))
                            
                            # 차이가 적은 순서로 정렬해서 상위 2~3곡 선택
                            scored_tracks.sort(key=lambda x: x[0])
                            selected_tracks = [item[1] for item in scored_tracks[:3]]
                            
                            for t in selected_tracks:
                                recommended_tracks.append(self._format_track(t))
                                
                        else:#예외사항 처리
                            
                            num_to_pick = min(len(track_list), 3)
                            random_picks = random.sample(track_list, num_to_pick)
                            for t in random_picks:
                                recommended_tracks.append(self._format_track(t))

                    except Exception as e:
                        print(f"⚠️ 트랙 처리 중 오류: {e}")
                        continue
            
            if not recommended_tracks:
                return self._get_fallback_recommendations(limit)

            random.shuffle(recommended_tracks)
            return recommended_tracks[:limit]

        except Exception as e:
            print(f"🔥 추천 로직 오류: {e}")
            return self._get_fallback_recommendations(limit)

    def _format_track(self, t):
        return {
            "name": t["name"],
            "artists": ", ".join([a["name"] for a in t["artists"]]),
            "url": t["external_urls"]["spotify"],
            "img": t["album"]["images"][0]["url"] if t["album"]["images"] else "https://via.placeholder.com/300"
        }

    def _get_fallback_recommendations(self, limit):
        # Fallback은 랜덤 유지
        FALLBACK_SEEDS = ["3HqSLMAZ3g3d5poBuWerCq", "3Nrfpe0tUJi4K4DXYWgMUX"]
        tracks = []
        try:
            seed = random.choice(FALLBACK_SEEDS)
            results = self.sp.artist_top_tracks(seed, country='KR')
            for t in results['tracks'][:limit]:
                tracks.append(self._format_track(t))
            return tracks
        except:
            return []