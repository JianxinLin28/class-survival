import subprocess


X = 0
Y = 0
WIDTH = 780
HEIGHT = 720


def run_applescript(script: str):
    result = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())

    return result.stdout.strip()


def resize_zoom_window(
    x: int,
    y: int,
    width: int,
    height: int,
):
    script = f'''
    tell application "System Events"
        set zoomProcess to missing value

        repeat with proc in application processes
            set procName to name of proc

            if procName is "Zoom Workplace" or procName is "zoom.us" then
                set zoomProcess to proc
                exit repeat
            end if
        end repeat

        if zoomProcess is missing value then
            error "Zoom is not running"
        end if

        tell zoomProcess
            if (count of windows) = 0 then
                error "Zoom has no visible windows"
            end if

            set targetWindow to window 1

            set position of targetWindow to {{{x}, {y}}}
            set size of targetWindow to {{{width}, {height}}}

            return name of targetWindow
        end tell
    end tell
    '''

    window_name = run_applescript(script)

    print(f'Resized Zoom window: "{window_name}"')
    print(f"Position: ({x}, {y})")
    print(f"Size: {width}x{height}")


def main():
    resize_zoom_window(
        X,
        Y,
        WIDTH,
        HEIGHT,
    )


if __name__ == "__main__":
    main()
