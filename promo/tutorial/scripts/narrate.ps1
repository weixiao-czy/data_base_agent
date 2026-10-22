param([switch]$ListVoices,[string]$VoiceName = '',[int]$Rate = 5,[string]$OutDir = '')
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Speech
$speaker = New-Object System.Speech.Synthesis.SpeechSynthesizer
try {
    $voices = @($speaker.GetInstalledVoices() | Where-Object { $_.Enabled } | ForEach-Object { $_.VoiceInfo })
    if ($ListVoices) {
        $voices | Select-Object Name, Culture | Format-Table
        exit 0
    }
    if ($VoiceName) {
        $selected = $voices | Where-Object { $_.Name -eq $VoiceName } | Select-Object -First 1
    } else {
        $selected = $voices | Where-Object { $_.Culture.Name -eq 'zh-CN' } | Select-Object -First 1
    }
    if (-not $selected) { throw 'No matching Chinese SAPI voice. Install a zh-CN SAPI voice, or supply external WAV cues as described in RENDER_HANDOFF.md. Do not substitute an English voice.' }
    $speaker.SelectVoice($selected.Name)
    # Rate 0 is the slow SAPI default; SAPI accepts -10..10. Keep the spoken pace high
    # enough that scripts/assemble_voice.py never needs more than 1.20x atempo.
    $speaker.Rate = $Rate
    $speaker.Volume = 100
    $project = Split-Path $PSScriptRoot -Parent
    $cues = Get-Content -LiteralPath (Join-Path $project 'narration-cues.json') -Raw -Encoding UTF8 | ConvertFrom-Json
    $outputDir = if ($OutDir) { if ([System.IO.Path]::IsPathRooted($OutDir)) { $OutDir } else { Join-Path $project $OutDir } } else { Join-Path $project 'public/voice-cues' }
    New-Item -ItemType Directory -Path $outputDir -Force | Out-Null
    $format = New-Object System.Speech.AudioFormat.SpeechAudioFormatInfo(44100, [System.Speech.AudioFormat.AudioBitsPerSample]::Sixteen, [System.Speech.AudioFormat.AudioChannel]::Mono)
    foreach ($cue in $cues) {
        $output = Join-Path $outputDir ('{0:D3}.wav' -f [int]$cue.id)
        $speaker.SetOutputToWaveFile($output, $format)
        $speaker.Speak([string]$cue.text)
        $speaker.SetOutputToNull()
        Write-Host ('Voice cue {0:D3} / {1}: {2} @ rate {3}' -f [int]$cue.id, $cues.Count, $selected.Name, $Rate)
    }
} finally { $speaker.Dispose() }
