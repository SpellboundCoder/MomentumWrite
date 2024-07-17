import flet as ft
import time
import threading
import pyclip
from data.dbconfig import Story, get_all_stories, delete_story, add_story
import datetime as dt

today = dt.datetime.today().strftime('%d-%m-%y')


class TypingMonitor:
    def __init__(self, timeout=5, on_timeout=None):
        self.timeout = timeout
        self.on_timeout = on_timeout
        self.last_event = threading.Event()
        self.stopped = False
        self.monitor_thread = threading.Thread(target=self.monitor_typing)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

    def monitor_typing(self):
        while not self.stopped:
            if not self.last_event.wait(timeout=self.timeout):
                if self.on_timeout:
                    self.on_timeout()
                    self.stop()

    def reset_timer(self):
        self.last_event.set()
        self.last_event.clear()

    def stop(self):
        self.stopped = True
        self.last_event.set()


current_time_in_sec = round(time.time())
typing_monitor: None | TypingMonitor = None


def main(page):

    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    selected_time_ref = ft.Ref[ft.Text]()
    column = ft.Ref[ft.Column]()
    container = ft.Ref[ft.Container]()
    timer = ft.Ref[ft.Text]()
    textfield = ft.Ref[ft.TextField]()

    minutes = [
        "1",
        "2",
        "3",
        "5",
        "10",
        "15",
        "20",
        "30",
        "45",
        "60"
    ]

    list_view = ft.ListView(
        spacing=10,
        width=600,
        padding=20,
        auto_scroll=True)

    success_dlg = ft.AlertDialog(
        title=ft.Text("CONGRATULATIONS YOU'VE MADE IT!"),
        on_dismiss=lambda e: on_dismiss(e, True, data=get_all_stories())
    )

    fail_dlg = ft.AlertDialog(
        title=ft.Column([
            ft.Row([ft.Text("Sorry, You stopped typing for more then  5 seconds!")],
                   alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([ft.Text('Your progress is wiped out 😰', color=ft.colors.RED_900)],
                   alignment=ft.MainAxisAlignment.CENTER),
        ]),
        on_dismiss=lambda e: on_dismiss(e, False, data=get_all_stories())
    )

    cupertino_picker = ft.CupertinoPicker(
        selected_index=3,
        magnification=1.22,
        squeeze=1.2,
        use_magnifier=True,
        on_change=lambda e: handle_picker_change(e),
        controls=[ft.Text(value=f) for f in minutes],
    )

    stories = get_all_stories()
    for story in stories:
        list_view.controls.append(ft.Text(value=story.text))

    def on_dismiss(e, success_: bool, data):
        if success_:
            text = textfield.current.value
            add_story(
                Story(text=text, date=today))
            column.current.visible = True
            container.current.visible = False
            page.remove(list_view)
            for text in data:
                list_view.controls.append(ft.Text(text.text))
            page.add(list_view)
            page.update()

        elif not success_:
            textfield.current.value = ''
            column.current.visible = True
            container.current.visible = False
            page.update()

    def on_timeout():
        page.open(fail_dlg)
        page.update()

    def handle_picker_change(e):
        selected_time_ref.current.value = minutes[int(e.data)]
        page.update()

    def countdown(value: int):
        global typing_monitor
        typing_monitor = TypingMonitor(timeout=5, on_timeout=on_timeout)

        full_time = value * 60
        seconds_left = full_time % 60
        minutes_left = int(full_time / 60)
        if minutes_left < 10:
            minutes_left = f'0{minutes_left}'
        if seconds_left < 10:
            seconds_left = f'0{seconds_left}'
        timer.current.value = f"{minutes_left}:{seconds_left}"
        timer.current.update()

        for _ in range(full_time):
            full_time -= 1
            seconds_left = full_time % 60
            minutes_left = int(full_time / 60)
            time.sleep(1)
            if minutes_left < 10:
                minutes_left = f'0{minutes_left}'
            if seconds_left < 10:
                seconds_left = f'0{seconds_left}'
            timer.current.value = f"{minutes_left}:{seconds_left}"
            timer.current.update()
        page.open(success_dlg)
        typing_monitor.stop()

    def start_writing():

        column.current.visible = False
        container.current.visible = True
        page.update()
        countdown(int(selected_time_ref.current.value))

    def on_change():
        if not typing_monitor.stopped:
            typing_monitor.reset_timer()

    page.add(
        ft.Column([
            ft.Divider(height=50),
            ft.Row([
               ft.Text('Welcome to ',
                       size=30,
                       weight=ft.FontWeight.BOLD,
                       spans=[ft.TextSpan('MomentumWrite',
                                          style=ft.TextStyle(color=ft.colors.GREEN_ACCENT_700, size=30))])
            ], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([
                ft.Text('Keep writing—if you stop for more than 5 seconds, your text will vanish.',
                        size=24, weight=ft.FontWeight.W_400)
            ], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([
                ft.Text('Stay focused and let your creativity flow!',
                        size=24, weight=ft.FontWeight.W_400)
            ], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row(
                # tight=True,
                controls=[
                    ft.Text("Session length in minutes:", size=23),
                    ft.TextButton(
                        content=ft.Text(value=minutes[1], ref=selected_time_ref, size=23),
                        style=ft.ButtonStyle(color=ft.colors.GREEN_ACCENT_700),
                        on_click=lambda e: page.open(
                            ft.CupertinoBottomSheet(
                                cupertino_picker,
                                height=216,
                                padding=ft.padding.only(top=6),
                            )
                        ),
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER
            ),
            ft.Row([ft.ElevatedButton('Start Writing',
                                      color=ft.colors.RED_ACCENT_700,
                                      on_click=lambda e: start_writing())],
                   alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([
                ft.Text('Previous works: ',
                        size=24, weight=ft.FontWeight.W_400)
            ], alignment=ft.MainAxisAlignment.CENTER),
            ft.Row([list_view], alignment=ft.MainAxisAlignment.CENTER)
            ],
            ref=column
        ),
        ft.Container(
            ref=container,
            expand=True,
            padding=25,
            visible=False,
            content=ft.Column([
                ft.Row([
                    ft.Text('Time left:', size=25, color=ft.colors.GREEN_900),
                    ft.Text(size=25, color=ft.colors.RED_900, ref=timer),
                    ft.Text('Keep writing...', size=25, color=ft.colors.GREEN_900),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

                ft.TextField(
                    multiline=True,
                    autofocus=True,
                    expand=True,
                    border_color=ft.colors.TRANSPARENT,
                    text_size=18,
                    on_change=lambda e: on_change(),
                    ref=textfield
                )
                ]
            )
        )
    )


ft.app(target=main)
