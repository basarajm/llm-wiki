---
description: 두 엔티티 간 관계 경로 추적 (공급망·주주망·계열·겸직)
argument-hint: <엔티티A> <엔티티B> | <엔티티> --shareholders|--customers|--suppliers
---

`engine\OPERATIONS.md` > "6. Connect" 절차로 관계를 추론하라.

대상: $ARGUMENTS

1. 시작 엔티티 페이지(`wiki\`)의 아웃바운드 링크를 수집한다.
2. 링크 그래프(공급사·고객사·주주·계열사·겸직 임원)를 따라 목표까지 경로를 탐색한다.
3. 경로상 각 관계를 출처와 함께 서술한다.
4. 시각화가 필요하면 `engine\scripts\build-viz.py`로 `wiki\viz.html`을 생성한다.
5. 가치 있는 결과는 `wiki\outputs\`에 저장한다.
