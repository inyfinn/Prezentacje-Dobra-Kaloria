// "Stwórz prezentację.exe" - maleńki plik startowy (C#, .NET Framework 4 - jest w każdym Windows 10/11).
// Po co: właściwy program (Python + WebView2) startuje z dysku sieciowego 8-30 s i przez ten czas nic nie widać.
// Ten plik od razu pokazuje planszę "Uruchamiam…" z kółkiem, paskiem i czasem (od 1.1.2), uruchamia "pliki programu\program.exe" i zamyka się sam, gdy okno
// programu się pojawi (albo po 120 s). To OSOBNY proces - ekran powitalny PyInstallera blokował okno (29.09.2026).
// Kompilacja: WORK\build.ps1 (csc.exe). Składnia C# 5 - bez nowszych konstrukcji.
using System;
using System.Diagnostics;
using System.Drawing;
using System.IO;
using System.Runtime.ExceptionServices;
using System.Security;
using System.Windows.Forms;

static class Launcher
{
    const string Title = "Stwórz prezentację";

    [STAThread]
    static int Main(string[] args)
    {
        string dir = Path.GetDirectoryName(Application.ExecutablePath);
        string contents = Path.Combine(dir, "pliki programu");
        string exe = Path.Combine(contents, "program.exe");
        string cli = Path.Combine(contents, "stworz-cli.exe");
        if (!File.Exists(exe))
        {
            MessageBox.Show("Obok tego pliku musi leżeć folder „pliki programu”.\n\nSkopiuj cały folder programu (plik + folder), " +
                            "a nie sam plik.", Title, MessageBoxButtons.OK, MessageBoxIcon.Warning);
            return 2;
        }
        if (args.Length > 0 && File.Exists(cli))   // z argumentami = wiersz poleceń (AI): przekaż do wersji konsolowej
        {
            var psi = new ProcessStartInfo(cli, QuoteAll(args));
            psi.UseShellExecute = false;
            using (var c = Process.Start(psi)) { c.WaitForExit(); return c.ExitCode; }
        }

        Application.EnableVisualStyles();
        // plansza nigdy nie pokazuje okna błędu - w razie kłopotu po prostu znika, program startuje dalej
        Application.SetUnhandledExceptionMode(UnhandledExceptionMode.CatchException);
        Application.ThreadException += delegate { try { foreach (Form f in Application.OpenForms) { f.Close(); break; } } catch { } };
        if (!WebView2Installed())   // okno programu rysuje Microsoft Edge WebView2 - bez niego program się nie uruchomi
        {
            var r = MessageBox.Show("Do działania programu potrzebny jest składnik Windows „Microsoft Edge WebView2”, " +
                                    "którego nie ma na tym komputerze.\n\nKliknij OK, żeby otworzyć stronę pobierania " +
                                    "(wybierz „Evergreen Bootstrapper”), zainstaluj go i uruchom program ponownie.",
                                    Title, MessageBoxButtons.OKCancel, MessageBoxIcon.Warning);
            if (r == DialogResult.OK)
                try { Process.Start("https://developer.microsoft.com/microsoft-edge/webview2/"); } catch { }
            return 3;
        }
        // czas startu z poprzednich uruchomień (pierwszy raz: 6 s na dysku lokalnym, 15 s na sieciowym)
        string userDir = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
                                      "Dobra Kaloria", "Stworz prezentacje");
        string timeFile = Path.Combine(userDir, "start-czas.txt");
        double expected = dir.StartsWith(@"\\") || new DriveInfo(Path.GetPathRoot(dir)).DriveType == DriveType.Network ? 15 : 6;
        try
        {
            double last;
            if (File.Exists(timeFile) && double.TryParse(File.ReadAllText(timeFile).Trim(),
                System.Globalization.NumberStyles.Float, System.Globalization.CultureInfo.InvariantCulture, out last) && last > 0.5)
                expected = last;
        }
        catch { }
        var fonts = new System.Drawing.Text.PrivateFontCollection();
        try
        {
            string lato = Path.Combine(contents, "app", "ui", "assets", "fonts", "Lato-Regular.ttf");
            if (File.Exists(lato)) fonts.AddFontFile(lato);
        }
        catch { }
        Image bgImg = null;
        string img = Path.Combine(contents, "app", "ui", "img", "powitanie.png");
        try
        {
            if (File.Exists(img))
                using (var fs = new FileStream(img, FileMode.Open, FileAccess.Read)) bgImg = new Bitmap(Image.FromStream(fs));
        }
        catch { }
        var form = new Splash(bgImg, expected, fonts);
        form.Text = Title;
        form.FormBorderStyle = FormBorderStyle.None;
        form.StartPosition = FormStartPosition.CenterScreen;
        form.ClientSize = new Size(560, 330);
        form.BackColor = Color.FromArgb(15, 118, 62);        // zieleń marki 0F763E
        form.ShowInTaskbar = true;
        form.TopMost = false;                                 // nie zasłaniamy innych okien na siłę
        try { form.Icon = Icon.ExtractAssociatedIcon(Application.ExecutablePath); } catch { }

        Process prog = null;
        try
        {
            var psi = new ProcessStartInfo(exe);
            psi.WorkingDirectory = dir;
            psi.UseShellExecute = false;
            prog = Process.Start(psi);
        }
        catch (Exception ex)
        {
            MessageBox.Show("Nie udało się uruchomić programu:\n" + ex.Message, Title, MessageBoxButtons.OK, MessageBoxIcon.Error);
            return 3;
        }

        var started = DateTime.UtcNow;
        var timer = new Timer();
        timer.Interval = 250;
        timer.Tick += delegate
        {
            bool done = false;
            try
            {
                prog.Refresh();
                done = prog.HasExited || prog.MainWindowHandle != IntPtr.Zero;
            }
            catch { done = true; }
            if (done || (DateTime.UtcNow - started).TotalSeconds > 120)   // twardy limit: plansza nigdy nie wisi
            {
                timer.Stop();
                double took = (DateTime.UtcNow - started).TotalSeconds;
                if (done && took < 110)                                   // zapamiętaj, ile trwał start (do ETA następnym razem)
                    try
                    {
                        Directory.CreateDirectory(userDir);
                        File.WriteAllText(timeFile, took.ToString("0.0", System.Globalization.CultureInfo.InvariantCulture));
                    }
                    catch { }
                form.Ready = true;
                form.Refresh();
                var close = new Timer();
                close.Interval = 250;                                     // pełny pasek przez chwilę, potem zamknij
                close.Tick += delegate { close.Stop(); form.Close(); };
                close.Start();
            }
        };
        form.Shown += delegate { timer.Start(); };
        form.Click += delegate { form.Close(); };                         // klik zamyka planszę (program działa dalej)
        Application.Run(form);
        return 0;
    }

    static bool WebView2Installed()
    {
        // klucze z dokumentacji Microsoft (wykrywanie WebView2 Runtime): maszyna 64/32-bit i instalacja na użytkownika
        const string id = @"\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}";
        string[] keys = { @"HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node" + id, @"HKEY_LOCAL_MACHINE\SOFTWARE" + id,
                          @"HKEY_CURRENT_USER\Software" + id };
        foreach (string k in keys)
        {
            try
            {
                var v = Microsoft.Win32.Registry.GetValue(k, "pv", null) as string;
                if (!string.IsNullOrEmpty(v) && v != "0.0.0.0") return true;
            }
            catch { }
        }
        return false;
    }

    static string QuoteAll(string[] args)
    {
        var parts = new string[args.Length];
        for (int i = 0; i < args.Length; i++)
        {
            string a = args[i];
            parts[i] = (a.IndexOf(' ') >= 0 || a.IndexOf('"') >= 0 || a.Length == 0)
                ? "\"" + a.Replace("\\\"", "\\\\\"").Replace("\"", "\\\"") + (a.EndsWith("\\") ? "\\" : "") + "\""
                : a;
        }
        return string.Join(" ", parts);
    }
}

// Plansza startowa: obraz marki (powitanie.png) + na dole kręcące się kółko, pasek postępu i "zostało ok. N s".
// Czas startu liczony z poprzednich uruchomień na tym komputerze (plik start-czas.txt w folderze użytkownika).
class Splash : Form
{
    readonly Image bg;
    readonly DateTime t0 = DateTime.UtcNow;
    readonly double expected;           // sekundy - ile zwykle trwa start
    readonly Timer anim = new Timer();
    Font fMain, fSmall;
    static System.Drawing.Text.PrivateFontCollection keepFonts;   // MUSI żyć do końca procesu (GC = AccessViolation)
    bool systemFont;
    float angle;
    public bool Ready;

    public Splash(Image background, double expectedSeconds, System.Drawing.Text.PrivateFontCollection fonts)
    {
        bg = background;
        expected = Math.Max(2.0, expectedSeconds);
        DoubleBuffered = true;
        SetStyle(ControlStyles.AllPaintingInWmPaint | ControlStyles.UserPaint | ControlStyles.OptimizedDoubleBuffer, true);
        keepFonts = fonts;
        FontFamily fam = fonts != null && fonts.Families.Length > 0 ? fonts.Families[0] : new FontFamily("Segoe UI");
        fMain = new Font(fam, 12.5f, FontStyle.Regular, GraphicsUnit.Point);
        fSmall = new Font(fam, 10.5f, FontStyle.Regular, GraphicsUnit.Point);
        anim.Interval = 30;                                    // ~33 klatek na sekundę
        anim.Tick += delegate { angle = (angle + 9f) % 360f; Invalidate(); };
        Shown += delegate { anim.Start(); };
        FormClosed += delegate { anim.Stop(); };
    }

    double Elapsed { get { return (DateTime.UtcNow - t0).TotalSeconds; } }

    protected override void OnPaint(PaintEventArgs e)
    {
        var g = e.Graphics;
        g.SmoothingMode = System.Drawing.Drawing2D.SmoothingMode.AntiAlias;
        g.TextRenderingHint = System.Drawing.Text.TextRenderingHint.AntiAliasGridFit;
        if (bg != null) g.DrawImage(bg, 0, 0, ClientSize.Width, ClientSize.Height);
        else g.Clear(Color.FromArgb(15, 118, 62));
        int W = ClientSize.Width;
        // pasek postępu: dochodzi do 92% w przewidywanym czasie, potem wolno pełznie - nigdy "stoi"
        double t = Elapsed, p = t <= expected ? 0.92 * (1 - Math.Pow(1 - t / expected, 2)) : 0.92 + 0.07 * (1 - Math.Exp(-(t - expected) / 8));
        if (Ready) p = 1;
        int bx = 56, bw = W - 112, by = 296, bh = 6;
        using (var track = new SolidBrush(Color.FromArgb(70, 255, 255, 255))) FillRound(g, track, bx, by, bw, bh);
        using (var fill = new SolidBrush(Color.FromArgb(255, 212, 42)))            // żółty marki FFD42A
            FillRound(g, fill, bx, by, Math.Max(bh, (int)(bw * p)), bh);
        // kółko ładowania
        int cs = 22, cx = bx, cy = 258;
        using (var ring = new Pen(Color.FromArgb(70, 255, 255, 255), 3f)) g.DrawEllipse(ring, cx, cy, cs, cs);
        using (var arc = new Pen(Color.White, 3f))
        {
            arc.StartCap = arc.EndCap = System.Drawing.Drawing2D.LineCap.Round;
            arc.LineJoin = System.Drawing.Drawing2D.LineJoin.Round;
            if (Ready)   // gotowe: pełne kółko ze znaczkiem zamiast kręcącego się łuku
            {
                g.DrawEllipse(arc, cx, cy, cs, cs);
                g.DrawLines(arc, new[] { new PointF(cx + 6.5f, cy + 11.5f), new PointF(cx + 10f, cy + 15f), new PointF(cx + 16f, cy + 8f) });
            }
            else g.DrawArc(arc, cx, cy, cs, cs, angle, 100);
        }
        // napisy
        DrawTexts(g, cx, cy, cs, bx, bw, t);
    }

    [HandleProcessCorruptedStateExceptions, SecurityCritical]
    void DrawTexts(Graphics g, int cx, int cy, int cs, int bx, int bw, double t)
    {
        try { DrawTextsCore(g, cx, cy, cs, bx, bw, t); }
        catch (Exception)
        {
            if (systemFont) return;                   // nawet czcionka systemowa zawiodła - bez napisów, bez błędu
            systemFont = true;
            fMain = new Font("Segoe UI", 12f); fSmall = new Font("Segoe UI", 10f);
            try { DrawTextsCore(g, cx, cy, cs, bx, bw, t); } catch (Exception) { }
        }
    }

    void DrawTextsCore(Graphics g, int cx, int cy, int cs, int bx, int bw, double t)
    {
        string left = Ready ? "Gotowe" : "Uruchamiam program…";
        int rest = (int)Math.Ceiling(expected - t);
        string right = Ready ? "" : (rest >= 1 ? "zostało ok. " + rest + " s" : "jeszcze chwilkę…");
        using (var white = new SolidBrush(Color.White))
        using (var soft = new SolidBrush(Color.FromArgb(224, 236, 228)))
        {
            g.DrawString(left, fMain, white, cx + cs + 12, cy + 1);
            var sz = g.MeasureString(right, fSmall);
            g.DrawString(right, fSmall, soft, bx + bw - sz.Width, cy + 3);
        }
    }

    static void FillRound(Graphics g, Brush b, int x, int y, int w, int h)
    {
        using (var path = new System.Drawing.Drawing2D.GraphicsPath())
        {
            int r = h;
            path.AddArc(x, y, r, r, 90, 180);
            path.AddArc(x + w - r, y, r, r, 270, 180);
            path.CloseFigure();
            g.FillPath(b, path);
        }
    }
}
