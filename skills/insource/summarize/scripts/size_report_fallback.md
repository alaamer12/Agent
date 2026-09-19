# Fallback size-report commands

Use `size_report.py` by default. If Python is unavailable in the environment, use one of these instead — same three metrics (lines, words, characters), same before/after/reduction shape.

## Bash (Linux/macOS)

```bash
input="path/to/source.txt"
output="path/to/summarized_source.txt"

in_lines=$(wc -l < "$input");   out_lines=$(wc -l < "$output")
in_words=$(wc -w < "$input");   out_words=$(wc -w < "$output")
in_chars=$(wc -m < "$input");   out_chars=$(wc -m < "$output")

printf "Metric      Input  Summary  Reduction\n"
printf "Lines       %5d  %7d  %s\n" "$in_lines" "$out_lines" \
  "$(awk -v b="$in_lines" -v a="$out_lines" 'BEGIN{if(b==0){print "n/a"}else{printf "%.1f%%", (1-a/b)*100}}')"
printf "Words       %5d  %7d  %s\n" "$in_words" "$out_words" \
  "$(awk -v b="$in_words" -v a="$out_words" 'BEGIN{if(b==0){print "n/a"}else{printf "%.1f%%", (1-a/b)*100}}')"
printf "Characters  %5d  %7d  %s\n" "$in_chars" "$out_chars" \
  "$(awk -v b="$in_chars" -v a="$out_chars" 'BEGIN{if(b==0){print "n/a"}else{printf "%.1f%%", (1-a/b)*100}}')"
```

## PowerShell (Windows)

```powershell
$input_path  = "path\to\source.txt"
$output_path = "path\to\summarized_source.txt"

$inText  = Get-Content $input_path -Raw
$outText = Get-Content $output_path -Raw

function Get-Counts($text) {
    [PSCustomObject]@{
        Lines = ($text -split "`n").Count
        Words = ($text -split '\s+' | Where-Object { $_ -ne '' }).Count
        Chars = $text.Length
    }
}

$in  = Get-Counts $inText
$out = Get-Counts $outText

function Pct($b, $a) { if ($b -eq 0) { "n/a" } else { "{0:N1}%" -f ((1 - $a/$b) * 100) } }

"{0,-10} {1,8} {2,10}  Reduction" -f "Metric", "Input", "Summary"
"{0,-10} {1,8} {2,10}  {3}" -f "Lines", $in.Lines, $out.Lines, (Pct $in.Lines $out.Lines)
"{0,-10} {1,8} {2,10}  {3}" -f "Words", $in.Words, $out.Words, (Pct $in.Words $out.Words)
"{0,-10} {1,8} {2,10}  {3}" -f "Characters", $in.Chars, $out.Chars, (Pct $in.Chars $out.Chars)
```

Both produce the same shape of report as `size_report.py` — use whichever the environment supports, but never skip the report for a file-based summarization task.
