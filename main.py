import streamlit as st
import json
import os
from itertools import combinations

DATA_FILE = 'teams.json'

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    else:
        return {"teams": [], "members": []}

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False)

def balance_teams(members):
    best_diff = float('inf')
    best_teams = None
    for combo in combinations(members, len(members) // 2):
        team1 = list(combo)
        team2 = [m for m in members if m not in team1]
        score_team1 = sum(m['score'] for m in team1)
        score_team2 = sum(m['score'] for m in team2)
        diff = abs(score_team1 - score_team2)
        if diff < best_diff:
            best_diff = diff
            best_teams = (team1, team2)
    return best_teams

# Streamlit 앱 레이아웃
st.title("팀 선택기")

# 선택된 버튼의 색상을 변경하는 사용자 정의 CSS 삽입
st.markdown("""
    <style>
    .selected {
        background-color: #4CAF50 !important;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

data = load_data()

# 멤버 추가 폼
st.header("멤버 추가")
name = st.text_input("멤버 이름 입력")
score = st.number_input("멤버 점수 입력", min_value=0, step=1)
if st.button("멤버 추가"):
    if name and score is not None:
        data["members"].append({"name": name, "score": score})
        save_data(data)
        st.success(f"'{name}' 멤버가 점수 {score}로 성공적으로 추가되었습니다!")
    else:
        st.error("멤버 이름과 점수를 입력하세요.")

# 팀을 위한 멤버 선택
st.header("멤버 선택")
if 'selected_members' not in st.session_state:
    st.session_state['selected_members'] = []

selected_members = st.session_state['selected_members']

# 멤버 버튼을 가로로 표시
st.write("### 사용 가능한 멤버")
cols = st.columns(5)
for idx, member in enumerate(data["members"]):
    button_label = f"{member['name']}: {member['score']}"
    button_key = f"{member['name']}-{member['score']}"
    if member in selected_members:
        button_style = "selected"
    else:
        button_style = ""

    # 멤버 선택/해제 버튼 표시
    if cols[idx % 5].button(button_label, key=button_key, help="클릭하여 선택/해제"):
        if member in selected_members:
            selected_members.remove(member)
        else:
            if len(selected_members) < 10:
                selected_members.append(member)
            else:
                st.error("최대 10명의 멤버만 선택할 수 있습니다.")
        st.session_state['selected_members'] = selected_members
        st.experimental_rerun()

    # 멤버 점수를 변경할 수 있는 입력 필드 표시
    new_score = cols[idx % 5].number_input(f"{member['name']}의 점수", value=member['score'], min_value=0, key=f"score-{member['name']}")
    if new_score != member['score']:
        member['score'] = new_score
        save_data(data)
        st.experimental_rerun()

# 선택된 멤버 표시
st.write(f"선택된 멤버 ({len(selected_members)}/10): {[m['name'] for m in selected_members]}")

# 팀 생성 로직
if len(selected_members) == 10:
    if st.button("균형 잡힌 팀 생성"):
        team1, team2 = balance_teams(selected_members)
        data["teams"] = [team1, team2]
        save_data(data)
        st.success("균형 잡힌 팀이 성공적으로 생성되었습니다!")
        st.session_state['selected_members'] = []

# 팀 초기화 및 재생성 버튼 추가
if data["teams"]:
    if st.button("팀 초기화"):
        data["teams"] = []
        save_data(data)
        st.success("팀이 성공적으로 초기화되었습니다!")
        st.experimental_rerun()

    if st.button("팀 재생성"):
        team1, team2 = balance_teams(selected_members)
        data["teams"] = [team1, team2]
        save_data(data)
        st.success("팀이 성공적으로 재생성되었습니다!")
        st.experimental_rerun()

# 멤버 표시
st.header("멤버")
if data["members"]:
    st.write([f"{member['name']}, {member['score']}" for member in data["members"]])
else:
    st.write("아직 추가된 멤버가 없습니다.")

# 팀 표시
st.header("팀")
for i, team in enumerate(data["teams"], start=1):
    st.subheader(f"팀 {i}")
    st.write([f"{member['name']}: {member['score']}" for member in team])
