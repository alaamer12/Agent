# Third-Party Notices

This project bundles code from the following third-party open-source projects. Each retains its original license.

## bradautomates/claude-video

The pipeline scripts under [`scripts/`](scripts/) — `watch.py`, `download.py`, `frames.py`, `transcribe.py`, `whisper.py`, `setup.py` — are vendored from [bradautomates/claude-video](https://github.com/bradautomates/claude-video).

**Modifications** made in this copy, under the terms of the MIT license below:

- `download.py` — `download()`/`download_url()` take `yt_extra` (cookie passthrough) and `skip_video` (`--skip-download`); `_js_runtime_args()` passes `--js-runtimes deno|node` when yt-dlp supports the flag and a runtime is installed; `_read_info()` extracted from `download_url()`.
- `watch.py` — added the `--transcript-only`, `--cookies`, and `--cookies-from-browser` flags and the `report_transcript_only()` caption-only report path.

Frame budgets, transcript parsing, and the Whisper clients are unmodified.

## Added in this skill, not vendored

- `scripts/motion.py` — frame-to-frame motion direction measurement. Original to this skill, released under the project's own [LICENSE](LICENSE).

The following license applies to those files:

```
MIT License

Copyright (c) 2025 bradautomates

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
