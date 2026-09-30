// "Stwórz prezentację.exe" - maleńki plik startowy (C#, .NET Framework 4 - jest w każdym Windows 10/11).
// Po co: właściwy program (Python + WebView2) startuje z dysku sieciowego 8-30 s i przez ten czas nic nie widać.
// Ten plik od razu pokazuje planszę "Uruchamiam…", uruchamia "pliki programu\program.exe" i zamyka się sam, gdy okno
// programu się pojawi (albo po 120 s). To OSOBNY proces - ekran powitalny PyInstallera blokował okno (29.09.2026).
// Kompilacja: WORK\build.ps1 (csc.exe). Składnia C# 5 - bez nowszych konstrukcji.
using System;
using System.Diagnostics;
using System.Drawing;
using System.IO;
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
        var form = new Form();
        form.Text = Title;
        form.FormBorderStyle = FormBorderStyle.None;
        form.StartPosition = FormStartPosition.CenterScreen;
        form.ClientSize = new Size(560, 330);
        form.BackColor = Color.FromArgb(15, 118, 62);        // zieleń marki 0F763E
        form.ShowInTaskbar = true;
        form.TopMost = false;                                 // nie zasłaniamy innych okien na siłę
        try { form.Icon = Icon.ExtractAssociatedIcon(Application.ExecutablePath); } catch { }
        string img = Path.Combine(contents, "app", "ui", "img", "powitanie.png");
        if (File.Exists(img))
        {
            try
            {
                using (var fs = new FileStream(img, FileMode.Open, FileAccess.Read))
                {
                    form.BackgroundImage = Image.FromStream(fs);
                    form.BackgroundImageLayout = ImageLayout.Stretch;
                }
            }
            catch { }
        }
        else
        {
            var lbl = new Label();
            lbl.Text = "Stwórz prezentację\n\nUruchamiam program, to potrwa kilka sekund…";
            lbl.ForeColor = Color.White;
            lbl.Font = new Font("Segoe UI", 14f, FontStyle.Bold);
            lbl.Dock = DockStyle.Fill;
            lbl.TextAlign = ContentAlignment.MiddleCenter;
            form.Controls.Add(lbl);
        }

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
                form.Close();
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
