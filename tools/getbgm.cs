// 설치기 exe 안의 bgm.mp3 / bgm.env 를 꺼낸다 (exe를 실행하지 않고 읽기만 함)
using System; using System.IO; using Mono.Cecil;
static class GetBgm
{
    static int Main(string[] a)
    {
        var asm = AssemblyDefinition.ReadAssembly(a[0]);
        bool ok = false;
        foreach (var r in asm.MainModule.Resources)
        {
            var e = r as EmbeddedResource; if (e == null) continue;
            if (r.Name == "bgm.mp3") { File.WriteAllBytes(a[1], e.GetResourceData()); ok = true; }
            if (r.Name == "bgm.env") File.WriteAllBytes(Path.Combine(Path.GetDirectoryName(a[0]), "bgm.env"), e.GetResourceData());
        }
        if (!ok) { Console.Error.WriteLine("bgm.mp3 가 들어 있지 않습니다."); return 1; }
        return 0;
    }
}
