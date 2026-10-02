"""No-command-line Windows desktop patcher."""
import json
from pathlib import Path
import queue
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from patcher_engine import Patcher

PACKAGE = Path(sys.executable).resolve().parent if getattr(sys, 'frozen', False) else Path(__file__).resolve().parents[1]


def main():
    if len(sys.argv) == 5 and sys.argv[1] == '--test-export':
        engine = Patcher(PACKAGE, Path(sys.argv[2]))
        assert engine.verify() == 'original'
        engine.export_copy(Path(sys.argv[3]))
        assert engine.verify() == 'original'
        Path(sys.argv[4]).write_text(json.dumps({'executable_export': 'passed', 'game_unchanged': True, 'files': len(engine.rows)}), encoding='utf-8')
        return
    # Noninteractive regression mode for the packaged executable on an isolated fixture.
    if len(sys.argv) == 4 and sys.argv[1] == '--test-fixture':
        engine = Patcher(PACKAGE, Path(sys.argv[2]))
        assert engine.verify() == 'original'
        engine.install()
        assert engine.verify() == 'installed'
        engine.restore()
        assert engine.verify() == 'original'
        Path(sys.argv[3]).write_text(json.dumps({'executable_roundtrip': 'passed', 'files': len(engine.rows)}), encoding='utf-8')
        return
    app = tk.Tk()
    smoke = len(sys.argv) == 3 and sys.argv[1] == '--smoke-ui'
    if smoke:
        app.withdraw()
    app.title('The Dream Of A Cockspur · 한국어 패치')
    app.geometry('740x520')
    app.minsize(680, 500)
    style = ttk.Style(app)
    style.configure('TLabel', font=('Malgun Gothic', 10))
    style.configure('TButton', font=('Malgun Gothic', 10), padding=8)
    frame = ttk.Frame(app, padding=24)
    frame.pack(fill='both', expand=True)
    ttk.Label(frame, text='한국어 패치 설치', font=('Malgun Gothic', 19, 'bold')).pack(anchor='w')
    ttk.Label(frame, text='게임을 종료한 뒤 실행 파일이 있는 게임 폴더를 선택하십시오.').pack(anchor='w', pady=(8, 16))
    folder = tk.StringVar()
    row = ttk.Frame(frame)
    row.pack(fill='x')
    ttk.Entry(row, textvariable=folder, state='readonly').pack(side='left', fill='x', expand=True)
    browse = ttk.Button(row, text='게임 폴더 선택', command=lambda: folder.set(filedialog.askdirectory(title='The Dream Of A Cockspur.exe가 있는 폴더') or folder.get()))
    browse.pack(side='right', padx=(8, 0))
    state = tk.StringVar(value='폴더를 선택하면 설치할 수 있습니다.')
    status_label = ttk.Label(frame, textvariable=state, wraplength=660)
    status_label.pack(anchor='w', pady=20)
    buttons = ttk.Frame(frame)
    buttons.pack(fill='x')
    events = queue.Queue()
    busy = [False]
    controls = [browse]

    def run(action):
        game = Path(folder.get())
        if not folder.get() or not (game / 'The Dream Of A Cockspur.exe').is_file():
            messagebox.showerror('게임 폴더 확인', 'The Dream Of A Cockspur.exe가 있는 폴더를 선택하십시오.')
            return
        running = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq The Dream Of A Cockspur.exe', '/FO', 'CSV', '/NH'], capture_output=True, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        if b'The Dream Of A Cockspur.exe' in running.stdout:
            messagebox.showerror('게임 종료 필요', '게임을 완전히 종료한 뒤 다시 시도하십시오.')
            return
        output = None
        if action == 'export_copy':
            chosen = filedialog.askdirectory(title='복사용 파일과 원본 백업을 저장할 위치 (게임 폴더 밖)')
            if not chosen:
                return
            output = Path(chosen) / 'Cockspur-copy-files'
        busy[0] = True
        for widget in controls:
            widget.configure(state='disabled')
        state.set('파일을 확인하고 있습니다. 창을 닫지 마십시오.')

        def worker():
            try:
                engine = Patcher(PACKAGE, game, lambda message: events.put(('progress', message)))
                result = engine.export_copy(output) if action == 'export_copy' else getattr(engine, action)()
                if action == 'verify':
                    result = {'original': '원본 상태입니다. 설치할 수 있습니다.', 'installed': '한국어 패치가 정상 설치되어 있습니다.', 'mixed': '일부 파일 상태가 다릅니다. 원본 복원이 필요합니다.'}[result]
                events.put(('done', result))
            except Exception as error:
                events.put(('error', str(error)))
        threading.Thread(target=worker, daemon=False).start()

    for index, (label, action) in enumerate([('한국어 패치 설치', 'install'), ('원본으로 복원', 'restore'), ('복사용 파일 만들기', 'export_copy'), ('상태 확인', 'verify')]):
        button = ttk.Button(buttons, text=label, command=lambda action=action: run(action))
        button.grid(row=index // 2, column=index % 2, sticky='ew', padx=(0, 8), pady=(0, 8))
        controls.append(button)
    buttons.columnconfigure(0, weight=1)
    buttons.columnconfigure(1, weight=1)
    footer = ttk.Label(frame, text='자동 설치 백업: 게임 폴더의 _cockspur_ko_backup\n복사용 원본 백업: 저장 위치의 Cockspur-copy-files/original-files\n설치 후 English를 선택하십시오. 세이브는 수정하지 않습니다.', wraplength=660)
    footer.pack(anchor='w', pady=(14, 0))
    frame.bind('<Configure>', lambda event: [widget.configure(wraplength=max(200, event.width)) for widget in (status_label, footer)])

    def poll():
        while not events.empty():
            kind, message = events.get()
            state.set(message.split('\n', 1)[0])
            if kind != 'progress':
                busy[0] = False
                for widget in controls:
                    widget.configure(state='normal')
                (messagebox.showerror if kind == 'error' else messagebox.showinfo)('한국어 패치', message)
        app.after(100, poll)

    app.protocol('WM_DELETE_WINDOW', lambda: messagebox.showinfo('작업 중', '작업이 끝난 뒤 창을 닫아 주십시오.') if busy[0] else app.destroy())
    poll()
    if smoke:
        app.update_idletasks()
        report = {'tk_initialized': True, 'controls': len(controls), 'button_labels': [widget.cget('text') for widget in controls], 'window_title': app.title(), 'visual_inspection': False}
        Path(sys.argv[2]).write_text(json.dumps(report, ensure_ascii=False), encoding='utf-8')
        app.destroy()
        return
    app.mainloop()


if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == '--smoke-ui':
        try:
            main()
        except Exception:
            import traceback
            Path(sys.argv[2]).write_text(traceback.format_exc(), encoding='utf-8')
            sys.exit(1)
    else:
        main()
