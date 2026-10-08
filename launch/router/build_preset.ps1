<#
.SYNOPSIS
  Собирает рабочий models-preset.local.ini для router-режима llama-server
  из шаблона launch\router\models-preset.ini.

.DESCRIPTION
  - раскрывает плейсхолдеры ${MODELS_DIR} / ${LLAMA_DIR} / ${PROJECT_DIR};
  - выбрасывает секции, чьи файлы (model / model-draft / mmproj) отсутствуют
    на этом ПК, и сообщает о них;
  - строку chat-template-file убирает, если файла нет (шаблон не критичен);
  - пишет результат в UTF-8 БЕЗ BOM с CRLF (иначе llm-парсер INI падает).

  Неизвестный ключ в секции — это ошибка парсера llama-server ровно так же,
  как в исходном .bat-флаге: опечатку поймает запуск сервера.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$Template,
    [Parameter(Mandatory = $true)][string]$Out,
    [string]$ModelsDir = '',
    [string]$LlamaDir = '',
    [string]$ProjectDir = ''
)

$ErrorActionPreference = 'Stop'
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch { }

function Get-Kv {
    param([string]$Line)
    if ($Line -match '^\s*([A-Za-z0-9_.\-]+)\s*=\s*(.*?)\s*$') {
        return [pscustomobject]@{ Key = $Matches[1]; Val = $Matches[2].Trim('"') }
    }
    return $null
}

function Test-FileRef {
    param([string]$Path)
    if ([string]::IsNullOrWhiteSpace($Path)) { return $false }
    if ($Path -match '^[a-zA-Z]+://') { return $true }   # URL (hf:/https:) не проверяем
    return (Test-Path -LiteralPath $Path -PathType Leaf)
}

$text = Get-Content -LiteralPath $Template -Raw
$text = $text.Replace('${MODELS_DIR}', $ModelsDir).
              Replace('${LLAMA_DIR}', $LlamaDir).
              Replace('${PROJECT_DIR}', $ProjectDir)

$lines = $text -split "\r?\n"

# --- разбор на header + секции ---------------------------------------------
$header = New-Object System.Collections.Generic.List[string]
$sections = New-Object System.Collections.Generic.List[object]
$cur = $null
foreach ($line in $lines) {
    if ($line -match '^\s*\[(.+?)\]\s*$') {
        $cur = [pscustomobject]@{
            Name  = $Matches[1]
            Lines = New-Object System.Collections.Generic.List[string]
        }
        $cur.Lines.Add($line) | Out-Null
        $sections.Add($cur) | Out-Null
    }
    elseif ($null -eq $cur) {
        $header.Add($line) | Out-Null
    }
    else {
        $cur.Lines.Add($line) | Out-Null
    }
}

# --- фильтрация ------------------------------------------------------------
$outLines = New-Object System.Collections.Generic.List[string]
foreach ($h in $header) { $outLines.Add($h) | Out-Null }

$included = New-Object System.Collections.Generic.List[string]
$skipped = New-Object System.Collections.Generic.List[string]
$warned = New-Object System.Collections.Generic.List[string]

foreach ($sec in $sections) {
    $drop = $false
    $modelPath = $null

    foreach ($l in $sec.Lines) {
        $kv = Get-Kv $l
        if ($null -eq $kv) { continue }
        if ($kv.Key -eq 'model') { $modelPath = $kv.Val; break }
    }

    if ($sec.Name -ne '*') {
        if (-not (Test-FileRef $modelPath)) {
            if ($null -eq $modelPath) {
                $skipped.Add("$($sec.Name)  (нет ключа model)") | Out-Null
            }
            else {
                $skipped.Add("$($sec.Name)  (нет файла: $modelPath)") | Out-Null
            }
            $drop = $true
        }
        else {
            foreach ($l in $sec.Lines) {
                $kv = Get-Kv $l
                if ($null -eq $kv) { continue }
                if ($kv.Key -in @('model-draft', 'mmproj', 'chat-template-file')) {
                    if (-not (Test-FileRef $kv.Val)) {
                        if ($kv.Key -eq 'chat-template-file') {
                            $warned.Add("$($sec.Name): пропущен chat-template-file (нет $($kv.Val))") | Out-Null
                        }
                        else {
                            $skipped.Add("$($sec.Name)  (нет $($kv.Key): $($kv.Val))") | Out-Null
                            $drop = $true
                        }
                        continue
                    }
                }
            }
        }
    }

    if ($drop) { continue }

    foreach ($l in $sec.Lines) {
        $kv = Get-Kv $l
        if ($null -ne $kv -and $kv.Key -eq 'chat-template-file' -and -not (Test-FileRef $kv.Val)) {
            continue   # уже предупреждены выше
        }
        $outLines.Add($l) | Out-Null
    }
    $included.Add($sec.Name) | Out-Null
}

if ($included.Count -eq 0) {
    throw "Ни одной модели не найдено по шаблону $Template (проверьте MODELS_DIR)."
}

# --- запись (UTF-8 без BOM, CRLF) ------------------------------------------
$final = ($outLines -join "`r`n")
[System.IO.File]::WriteAllText($Out, $final, (New-Object System.Text.UTF8Encoding($false)))

# --- отчёт -----------------------------------------------------------------
Write-Host ("Пресет: {0}" -f $Out)
Write-Host ("Моделей включено: {0}" -f $included.Count)
foreach ($id in $included) { Write-Host ("  + {0}" -f $id) }
if ($skipped.Count -gt 0) {
    Write-Host ("Пропущено (файлов нет): {0}" -f $skipped.Count)
    foreach ($s in $skipped) { Write-Host ("  - {0}" -f $s) }
}
if ($warned.Count -gt 0) {
    Write-Host ("Предупреждения: {0}" -f $warned.Count)
    foreach ($w in $warned) { Write-Host ("  ! {0}" -f $w) }
}
