import re

def is_korean(text):
    return bool(re.search("[가-힣]", text))

def get_user_input(text):
    """
    웹 폼에서 받은 텍스트를 검증하고 정제하여 반환
    """
    if not text:
        return "텍스트가 없습니다" # 빈 값 반환

    text = text.strip()
    
    # 한국어가 없으면 그냥 원본 반환하거나, 빈 문자열 반환 (정책에 따라 결정)
    if not is_korean(text):
        return "한국어가 아닙니다" # 혹은 raise Exception("한국어가 아닙니다") 처리

    return " ".join(text.split())