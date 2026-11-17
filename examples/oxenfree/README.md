# 예제: 코드 패치 (Oxenfree 한글패치)

파일을 덮어쓰는 대신 게임 코드(Assembly-CSharp.dll)를 직접 고치는 패치의 예입니다.
- 언어 목록의 러시아어 칸을 한국어로 교체, 언어 메뉴 표시 수정, 레지스트리 언어 지정
- 자막 바탕 이미지 끄기 + 글씨 테두리 (Unity UI 컴포넌트를 IL로 추가)
- Mono.Cecil로 코드를 이름으로 찾아 고침 → 게임 업데이트 뒤에도 다시 적용 가능

## 이 방식으로 쓰려면
1. `installer/Patcher.cs`를 지우고 `OxenfreePatcher.cs`를 `installer/`에 복사
2. 클래스 안 게임 경로·표식 이름을 새 게임에 맞게 수정
3. `CECIL=1 sh tools/build.sh`로 빌드 (Mono.Cecil을 exe 안에 넣음)

완성본: https://github.com/JukeONE/oxenfree-kr-patch
