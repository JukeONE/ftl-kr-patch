// =====================================================================
//  FTL: Faster Than Light 한글패치 방식 (1.6.x, ftl.dat 한 파일에 모든 자료가 들어 있음)
//  - exe 안 patch.zip의 파일(경로 = ftl.dat 안 경로)을 ftl.dat "끝에 덧붙이고"
//    목차(색인)의 해당 항목만 새 위치를 가리키게 바꾼다 → 280MB 파일을 통째로 백업하지 않음
//  - 복원: 기록해 둔 목차 원본을 되돌리고 파일을 원래 길이로 잘라 내면 원본과 완전히 같아짐
//  - 게임에 한국어 칸이 없어서 중국어(zh-Hans) 칸을 한국어로 사용:
//    글(data/text-zh-Hans.xml), 폰트(fonts/zh-Hans/black.ttf), 그림(img/loc-zh-Hans/*)
//    승무원 이름 목록(data/names.xml)은 설치할 때 게임 파일에서 직접 고쳐 만든다
//  - settings.ini의 language 값을 zh-Hans로 맞춰 바로 한국어로 뜨게 함(복원 때 되돌림)
// =====================================================================
using System;
using System.IO;
using System.IO.Compression;
using System.Linq;
using System.Collections.Generic;
using System.Text;
using System.Text.RegularExpressions;

static class Patcher
{
    public static string Version { get { return GameConfig.Version; } }
    public static Action<string> Log = s => { };
    const string BackupExt = ".kjbak";

    // ---------------------------------------------------------------- 게임 폴더 찾기
    public static bool IsGameDir(string d)
    {
        try { return !string.IsNullOrEmpty(d) && File.Exists(Path.Combine(d, GameConfig.CheckFile)); } catch { return false; }
    }

    public static string FindGameDir(string hint)
    {
        var cands = new List<string>();
        if (!string.IsNullOrEmpty(hint)) cands.Add(hint);
        cands.Add(AppDomain.CurrentDomain.BaseDirectory);
        cands.Add(Directory.GetCurrentDirectory());
        foreach (var c0 in cands)
        {
            try
            {
                var c = Path.GetFullPath(c0);
                for (int i = 0; i < 4 && c != null; i++)
                {
                    if (IsGameDir(c)) return c;
                    c = Path.GetDirectoryName(c);
                }
            }
            catch { }
        }
        foreach (var lib in SteamLibraries())
        {
            var d = Path.Combine(lib, "steamapps", "common", GameConfig.SteamFolder);
            if (IsGameDir(d)) return d;
        }
        return null;
    }

    static IEnumerable<string> SteamLibraries()
    {
        var roots = new List<string>();
        try
        {
            using (var k = Microsoft.Win32.Registry.CurrentUser.OpenSubKey(@"Software\Valve\Steam"))
                if (k != null && k.GetValue("SteamPath") != null) roots.Add(k.GetValue("SteamPath").ToString().Replace('/', '\\'));
        }
        catch { }
        try
        {
            using (var k = Microsoft.Win32.Registry.LocalMachine.OpenSubKey(@"SOFTWARE\WOW6432Node\Valve\Steam"))
                if (k != null && k.GetValue("InstallPath") != null) roots.Add(k.GetValue("InstallPath").ToString());
        }
        catch { }
        var libs = new List<string>(roots);
        foreach (var r in roots)
        {
            try
            {
                var vdf = Path.Combine(r, "steamapps", "libraryfolders.vdf");
                if (!File.Exists(vdf)) continue;
                foreach (Match m in Regex.Matches(File.ReadAllText(vdf), "\"path\"\\s*\"([^\"]+)\""))
                    libs.Add(m.Groups[1].Value.Replace("\\\\", "\\"));
            }
            catch { }
        }
        return libs.Distinct(StringComparer.OrdinalIgnoreCase);
    }

    public static bool IsGameRunning()
    {
        try { return System.Diagnostics.Process.GetProcessesByName(GameConfig.ProcessName).Length > 0; } catch { return false; }
    }

    // ---------------------------------------------------------------- 설치 기록
    // 1줄: 버전
    // L|원래 길이|패치 후 길이
    // E|목차 번호|원래 목차 항목(20바이트, 16진수)
    // S|settings.ini 경로|원래 language 값("=값") 또는 "-"(원래 줄이 없었음)
    const string Lang = "zh-Hans";
    const string DatName = "ftl.dat";
    static string RecordPath(string gameDir) { return Path.Combine(gameDir, GameConfig.RecordFile); }
    static string DatPath(string gameDir) { return Path.Combine(gameDir, DatName); }

    static string[] ReadRecord(string gameDir)
    {
        try { var p = RecordPath(gameDir); return File.Exists(p) ? File.ReadAllLines(p) : null; } catch { return null; }
    }

    static long RecordedNewLength(string[] rec)
    {
        foreach (var l in rec)
            if (l.StartsWith("L|")) { var a = l.Split(new[] { '|' }); long v; if (a.Length >= 3 && long.TryParse(a[2], out v)) return v; }
        return -1;
    }

    // 기록이 있어도 스팀 업데이트·무결성 검사로 ftl.dat이 새로 받아졌으면(길이가 다름) 적용 안 된 것으로 본다
    public static bool IsPatched(string gameDir)
    {
        try
        {
            var rec = ReadRecord(gameDir);
            if (rec == null || rec.Length == 0) return false;
            var dat = DatPath(gameDir);
            return File.Exists(dat) && new FileInfo(dat).Length == RecordedNewLength(rec);
        }
        catch { return false; }
    }

    public static bool NeedsUpdate(string gameDir)
    {
        if (!IsPatched(gameDir)) return false;
        var rec = ReadRecord(gameDir);
        return rec[0].Trim() != Version;
    }

    static ZipArchive OpenPatch()
    {
        var st = typeof(Patcher).Assembly.GetManifestResourceStream("patch.zip");
        if (st == null) throw new Exception("패치 파일(patch.zip)이 설치기에 들어 있지 않습니다.");
        return new ZipArchive(st, ZipArchiveMode.Read);
    }

    // ---------------------------------------------------------------- ftl.dat (PKG) 읽기
    // 머리말 16바이트: "PKG\n", 머리말 크기(2), 항목 크기(2), 항목 수(4), 이름 영역 크기(4)  ※ 모두 빅엔디언
    // 항목 20바이트: 이름 해시(4), 플래그(1)+이름 위치(3), 자료 위치(4), 자료 크기(4), 풀린 크기(4)
    const int HeaderSize = 16, EntrySize = 20, Align = 64;

    class Pkg
    {
        public int Count;
        public byte[] Entries;                       // Count * 20
        public Dictionary<string, int> Index = new Dictionary<string, int>(StringComparer.Ordinal);
    }

    static uint BE32(byte[] b, int o) { return ((uint)b[o] << 24) | ((uint)b[o + 1] << 16) | ((uint)b[o + 2] << 8) | b[o + 3]; }
    static void PutBE32(byte[] b, int o, uint v) { b[o] = (byte)(v >> 24); b[o + 1] = (byte)(v >> 16); b[o + 2] = (byte)(v >> 8); b[o + 3] = (byte)v; }

    static void ReadFull(Stream s, byte[] buf)
    {
        int got = 0;
        while (got < buf.Length)
        {
            int n = s.Read(buf, got, buf.Length - got);
            if (n <= 0) throw new Exception("ftl.dat을 끝까지 읽지 못했습니다.");
            got += n;
        }
    }

    static Pkg ReadPkg(FileStream fs)
    {
        var h = new byte[HeaderSize];
        fs.Position = 0; ReadFull(fs, h);
        if (h[0] != 'P' || h[1] != 'K' || h[2] != 'G' || h[3] != '\n') throw new Exception("ftl.dat 형식이 예상과 다릅니다. (FTL 1.6.x 전용 패치)");
        int hs = (h[4] << 8) | h[5], es = (h[6] << 8) | h[7];
        if (hs != HeaderSize || es != EntrySize) throw new Exception("ftl.dat 목차 형식이 예상과 다릅니다.");
        var pkg = new Pkg();
        pkg.Count = (int)BE32(h, 8);
        int pathSize = (int)BE32(h, 12);
        if (pkg.Count <= 0 || pkg.Count > 100000 || pathSize <= 0 || pathSize > 16 * 1024 * 1024) throw new Exception("ftl.dat 목차 크기가 이상합니다.");
        pkg.Entries = new byte[pkg.Count * EntrySize]; ReadFull(fs, pkg.Entries);
        var paths = new byte[pathSize]; ReadFull(fs, paths);
        for (int i = 0; i < pkg.Count; i++)
        {
            int po = (int)(BE32(pkg.Entries, i * EntrySize + 4) & 0xFFFFFF);
            int e = po; while (e < paths.Length && paths[e] != 0) e++;
            pkg.Index[Encoding.UTF8.GetString(paths, po, e - po)] = i;
        }
        return pkg;
    }

    static byte[] ReadEntryData(FileStream fs, Pkg pkg, int idx)
    {
        int o = idx * EntrySize;
        if (pkg.Entries[o + 4] != 0) throw new Exception("압축된 항목은 지원하지 않습니다.");
        var buf = new byte[BE32(pkg.Entries, o + 12)];
        fs.Position = BE32(pkg.Entries, o + 8); ReadFull(fs, buf);
        return buf;
    }

    static string Hex(byte[] b, int o, int n) { var sb = new StringBuilder(n * 2); for (int i = 0; i < n; i++) sb.Append(b[o + i].ToString("x2")); return sb.ToString(); }
    static byte[] UnHex(string s) { var b = new byte[s.Length / 2]; for (int i = 0; i < b.Length; i++) b[i] = Convert.ToByte(s.Substring(i * 2, 2), 16); return b; }

    // 승무원 이름: 중국어 칸 이름 목록을 기본(영문) 이름으로 바꾼 names.xml을 만든다
    static byte[] BuildNames(byte[] original)
    {
        var enc = new UTF8Encoding(false);
        var text = enc.GetString(original);
        var rx = new Regex("<nameList race=\"human\" sex=\"(male|female)\"( language=\"([^\"]+)\")?>(.*?)</nameList>", RegexOptions.Singleline);
        var nameRx = new Regex("<name[^>]*>.*?</name>", RegexOptions.Singleline);
        var baseNames = new Dictionary<string, List<string>> { { "male", new List<string>() }, { "female", new List<string>() } };
        foreach (Match m in rx.Matches(text))
            if (!m.Groups[3].Success)
                foreach (Match n in nameRx.Matches(m.Groups[4].Value)) baseNames[m.Groups[1].Value].Add(n.Value);
        if (baseNames["male"].Count == 0 || baseNames["female"].Count == 0) return null;
        string nl = text.Contains("\r\n") ? "\r\n" : "\n";
        bool changed = false;
        var result = rx.Replace(text, m =>
        {
            if (m.Groups[3].Value != Lang) return m.Value;
            changed = true;
            return "<nameList race=\"human\" sex=\"" + m.Groups[1].Value + "\" language=\"" + Lang + "\">" + nl + "\t"
                 + string.Join(nl + "\t", baseNames[m.Groups[1].Value].ToArray()) + nl + "</nameList>";
        });
        return changed ? enc.GetBytes(result) : null;
    }

    // ---------------------------------------------------------------- settings.ini 언어 값
    static IEnumerable<string> SettingsFiles(string gameDir)
    {
        var list = new List<string> { Path.Combine(gameDir, "settings.ini") };
        try { list.Add(Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments), "My Games", "FasterThanLight", "settings.ini")); } catch { }
        return list.Where(File.Exists);
    }

    // value가 null이면 language 줄을 지운다. 돌려주는 값: 원래 값("=값") 또는 "-"
    // 다른 줄·줄바꿈·인코딩은 1바이트도 건드리지 않도록 Latin-1로 읽고 쓴다
    static string SetLanguage(string path, string value)
    {
        var enc = Encoding.GetEncoding(28591);
        var text = File.ReadAllText(path, enc);
        string nl = text.Contains("\r\n") ? "\r\n" : "\n";
        string old = "-";
        var m = Regex.Match(text, "^language=([^\r\n]*)(\r?\n)?", RegexOptions.Multiline | RegexOptions.IgnoreCase);
        if (m.Success)
        {
            old = "=" + m.Groups[1].Value.Trim();
            string rep = value == null ? "" : "language=" + value + m.Groups[2].Value;
            text = text.Substring(0, m.Index) + rep + text.Substring(m.Index + m.Length);
        }
        else if (value != null) text = "language=" + value + nl + text;
        File.WriteAllText(path, text, enc);
        return old;
    }

    // ---------------------------------------------------------------- 설치
    public static bool Install(string gameDir)
    {
        if (IsGameRunning()) { Log("! 게임이 실행 중입니다. 게임을 끄고 다시 시도하세요."); return false; }
        var dat = DatPath(gameDir);
        if (!File.Exists(dat))
        {
            if (File.Exists(Path.Combine(gameDir, "resources", "data.dat"))) Log("! 예전 버전(1.5.x) 게임입니다. 이 패치는 1.6.x 전용입니다.");
            else Log("! ftl.dat을 찾지 못했습니다.");
            return false;
        }
        if (File.Exists(RecordPath(gameDir)))
        {
            if (IsPatched(gameDir))
            {
                Log("이전 패치를 먼저 되돌립니다...");
                if (!Restore(gameDir)) return false;
            }
            else File.Delete(RecordPath(gameDir));   // 게임이 새로 받아져 쓸모없어진 기록
        }

        var record = new List<string> { Version };
        int count = 0;
        try
        {
            using (var zip = OpenPatch())
            using (var fs = new FileStream(dat, FileMode.Open, FileAccess.ReadWrite, FileShare.None))
            {
                var pkg = ReadPkg(fs);
                long origLen = fs.Length;

                // 1) 넣을 자료 준비 + 모두 ftl.dat 안에 있는 경로인지 먼저 확인 (하나라도 없으면 아무것도 건드리지 않음)
                var items = new List<KeyValuePair<int, byte[]>>();
                foreach (var e in zip.Entries.Where(e => !string.IsNullOrEmpty(e.Name)))
                {
                    int idx;
                    if (!pkg.Index.TryGetValue(e.FullName, out idx))
                        throw new Exception("이 버전의 게임에는 '" + e.FullName + "'가 없습니다. (지원하지 않는 게임 버전)");
                    using (var src = e.Open())
                    using (var ms = new MemoryStream()) { src.CopyTo(ms); items.Add(new KeyValuePair<int, byte[]>(idx, ms.ToArray())); }
                }
                int nameIdx;
                if (pkg.Index.TryGetValue("data/names.xml", out nameIdx))
                {
                    var names = BuildNames(ReadEntryData(fs, pkg, nameIdx));
                    if (names != null) items.Add(new KeyValuePair<int, byte[]>(nameIdx, names));
                }

                // 2) 위치 계산
                long pos = (origLen + Align - 1) / Align * Align;
                var newEntries = (byte[])pkg.Entries.Clone();
                var offsets = new List<long>();
                foreach (var it in items)
                {
                    offsets.Add(pos);
                    int o = it.Key * EntrySize;
                    newEntries[o + 4] = 0;
                    PutBE32(newEntries, o + 8, (uint)pos);
                    PutBE32(newEntries, o + 12, (uint)it.Value.Length);
                    PutBE32(newEntries, o + 16, (uint)it.Value.Length);
                    record.Add("E|" + it.Key + "|" + Hex(pkg.Entries, o, EntrySize));
                    pos = (pos + it.Value.Length + Align - 1) / Align * Align;
                }
                long newLen = offsets[offsets.Count - 1] + items[items.Count - 1].Value.Length;
                if (newLen > uint.MaxValue) throw new Exception("ftl.dat이 너무 큽니다.");
                record.Insert(1, "L|" + origLen + "|" + newLen);

                // 3) 기록을 먼저 남기고(중간에 꺼져도 복원 가능) → 자료 덧붙이기 → 목차 고치기
                File.WriteAllLines(RecordPath(gameDir), record);
                Log("파일 " + items.Count + "개 적용 중...");
                fs.SetLength(newLen);
                for (int i = 0; i < items.Count; i++)
                {
                    fs.Position = offsets[i];
                    fs.Write(items[i].Value, 0, items[i].Value.Length);
                    count++;
                }
                fs.Flush(true);
                fs.Position = HeaderSize;
                fs.Write(newEntries, 0, newEntries.Length);
                fs.Flush(true);
            }
        }
        catch (Exception ex)
        {
            Log("! 오류: " + ex.Message);
            if (File.Exists(RecordPath(gameDir))) { Log("변경을 되돌립니다..."); try { Restore(gameDir); } catch { } }
            return false;
        }

        // 4) 언어 설정
        int set = 0;
        foreach (var ini in SettingsFiles(gameDir))
        {
            try { var old = SetLanguage(ini, Lang); File.AppendAllLines(RecordPath(gameDir), new[] { "S|" + ini + "|" + old }); set++; }
            catch (Exception ex) { Log("! 언어 설정 실패: " + ex.Message); }
        }
        Log(count + "개 항목 적용 (ftl.dat 뒤에 덧붙임, 복원 가능)");
        if (set > 0) Log("게임 언어를 한국어 칸으로 맞췄습니다.");
        Log("영어로 나오면: OPTIONS → Change Language → 한국어");
        return true;
    }

    // ---------------------------------------------------------------- 복원
    public static bool Restore(string gameDir)
    {
        if (IsGameRunning()) { Log("! 게임이 실행 중입니다. 게임을 끄고 다시 시도하세요."); return false; }
        var rp = RecordPath(gameDir);
        var rec = ReadRecord(gameDir);
        if (rec == null || rec.Length == 0) { Log("패치되어 있지 않습니다. (복원 불필요)"); return true; }

        long origLen = -1, newLen = -1;
        var entries = new List<KeyValuePair<int, byte[]>>();
        var settings = new List<KeyValuePair<string, string>>();
        foreach (var line in rec.Skip(1))
        {
            var a = line.Split(new[] { '|' });
            if (a[0] == "L" && a.Length >= 3) { long.TryParse(a[1], out origLen); long.TryParse(a[2], out newLen); }
            else if (a[0] == "E" && a.Length >= 3) entries.Add(new KeyValuePair<int, byte[]>(int.Parse(a[1]), UnHex(a[2])));
            else if (a[0] == "S" && a.Length >= 3) settings.Add(new KeyValuePair<string, string>(string.Join("|", a.Skip(1).Take(a.Length - 2).ToArray()), a[a.Length - 1]));
        }

        var dat = DatPath(gameDir);
        bool ok = true;
        if (!File.Exists(dat)) { Log("! ftl.dat이 없습니다. 스팀에서 게임 파일 무결성 확인을 해 주세요."); ok = false; }
        else if (origLen <= 0) { Log("! 설치 기록이 손상되었습니다. 스팀에서 게임 파일 무결성 확인을 해 주세요."); ok = false; }
        else
        {
            using (var fs = new FileStream(dat, FileMode.Open, FileAccess.ReadWrite, FileShare.None))
            {
                if (fs.Length == origLen) Log("ftl.dat은 이미 원본 길이입니다. 목차만 확인합니다.");
                if (fs.Length != newLen && fs.Length != origLen)
                    Log("게임 파일이 새로 받아진 상태입니다(업데이트/무결성 확인). 기록만 지웁니다.");
                else
                {
                    var pkg = ReadPkg(fs);
                    int n = 0;
                    foreach (var e in entries)
                    {
                        int o = e.Key * EntrySize;
                        if (e.Key < 0 || e.Key >= pkg.Count || e.Value.Length != EntrySize) continue;
                        bool sameHash = true;
                        for (int i = 0; i < 4; i++) if (pkg.Entries[o + i] != e.Value[i]) sameHash = false;
                        if (!sameHash) continue;
                        fs.Position = HeaderSize + o; fs.Write(e.Value, 0, EntrySize); n++;
                    }
                    fs.Flush(true);
                    if (fs.Length > origLen) fs.SetLength(origLen);
                    fs.Flush(true);
                    Log("목차 " + n + "개 항목을 되돌리고 ftl.dat을 원래 크기로 줄였습니다.");
                }
            }
        }
        foreach (var s in settings)
        {
            try { if (File.Exists(s.Key)) SetLanguage(s.Key, s.Value == "-" ? null : s.Value.Substring(1)); }
            catch (Exception ex) { Log("! 언어 설정 되돌리기 실패: " + ex.Message); }
        }
        if (ok) File.Delete(rp);
        return ok;
    }
}
