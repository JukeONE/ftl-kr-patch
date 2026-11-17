// =====================================================================
//  게임별 설정 — 새 한글패치를 만들 때 이 파일만 고치면 됩니다
// =====================================================================
static class GameConfig
{
    // 창 제목(작업 표시줄)과 화면 위 큰 제목
    public const string WindowTitle = "FTL 한글패치";
    public const string ScreenTitle = "FTL: FASTER THAN LIGHT";

    // 화면 제목 아래 작은 글씨 (기본: "한글패치 v1.0")
    public const string SubTitle = "한글패치 v" + Version;

    // 설치기 안내 문구에 쓰는 패치 이름 ("~가 적용됩니다", "~ 적용됨" 등). 받침 없는 말로 끝나게 (가/를)
    public const string PatchName = "한글패치";

    // 패치 버전. 올리면 이미 설치한 사람에게 "업데이트 있음"으로 표시됨
    public const string Version = "1.0";

    // 스팀 앱 번호 ([실행] 버튼: steam://rungameid/번호)
    public const string SteamAppId = "212680";

    // 스팀 라이브러리 안 폴더 이름 (steamapps\common\여기)
    public const string SteamFolder = "FTL Faster Than Light";

    // 게임 폴더인지 확인할 파일 (게임 폴더 기준 상대 경로)
    public const string CheckFile = "FTLGame.exe";

    // 게임 실행 중인지 확인할 프로세스 이름 (.exe 빼고)
    public const string ProcessName = "FTLGame";

    // 게임 폴더에 남길 설치 기록 파일 이름
    public const string RecordFile = "kimjuke_patch.txt";
}
