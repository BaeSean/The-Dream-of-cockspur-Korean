param(
 [ValidateSet('Verify','Install','Restore')][string]$Mode='Verify',
 [string]$GameRoot='E:\Steam\steamapps\common\TheDreamOfACockspur'
)
$ErrorActionPreference='Stop'
$GameRoot=[IO.Path]::GetFullPath($GameRoot).TrimEnd('\')
$manifest=Get-Content -LiteralPath (Join-Path $PSScriptRoot 'manifest.json') -Raw | ConvertFrom-Json
$statePath=Join-Path $PSScriptRoot 'install-state.json'
function Get-ContainedPath([string]$Base,[string]$Relative) {
 $baseFull=[IO.Path]::GetFullPath($Base).TrimEnd('\')
 $path=[IO.Path]::GetFullPath((Join-Path $baseFull $Relative))
 if (-not $path.StartsWith($baseFull+'\',[StringComparison]::OrdinalIgnoreCase)) {throw 'Path outside target folder'}
 return $path
}
function Get-Sha([string]$Path) {return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant()}
$items=@()
foreach($entry in $manifest) {
 $target=Get-ContainedPath $GameRoot $entry.path
 $payload=Get-ContainedPath (Join-Path $PSScriptRoot 'files') $entry.path
 if ((Get-Sha $payload) -ne $entry.patched_sha256) {throw ('Damaged patch file: '+$entry.path)}
 $current=if(Test-Path -LiteralPath $target){Get-Sha $target}else{$null}
 $items+= [pscustomobject]@{entry=$entry;target=$target;payload=$payload;current=$current;newFile=($entry.new_file -eq $true)}
}
if($Mode -eq 'Verify') {
 foreach($item in $items) {
  if($item.newFile -and $null -eq $item.current) {$status='Original - compatible'}
  elseif(-not $item.newFile -and $item.current -eq $item.entry.original_sha256) {$status='Original - compatible'}
  elseif($item.current -eq $item.entry.patched_sha256) {$status='Korean patch installed'}
  else {throw ('Different game version or modified file: '+$item.entry.path)}
  Write-Output ($status+': '+$item.entry.path)
 }
 exit 0
}
$exe=Join-Path $GameRoot 'The Dream Of A Cockspur.exe'
foreach($process in @(Get-Process -Name 'The Dream Of A Cockspur' -ErrorAction SilentlyContinue)) {
 if($process.Path -eq $exe) {throw 'Close the target game before installing/restoring.'}
}
if($Mode -eq 'Install') {
 if (@($items | Where-Object {if($_.newFile){$null -ne $_.current}else{$_.current -ne $_.entry.original_sha256}}).Count -gt 0) {throw 'Install requires verified original files. Restore an existing patch first.'}
 $backup=Join-Path $PSScriptRoot ('backups\'+(Get-Date -Format 'yyyyMMdd-HHmmss-fff'))
 foreach($item in $items) {
  if($item.newFile){continue}
  $backfile=Get-ContainedPath $backup $item.entry.path
  New-Item -ItemType Directory -Path ([IO.Path]::GetDirectoryName($backfile)) -Force | Out-Null
  Copy-Item -LiteralPath $item.target -Destination $backfile
  if((Get-Sha $backfile) -ne $item.entry.original_sha256) {throw 'Backup verification failed'}
 }
 $state=[pscustomobject]@{game_root=$GameRoot;backup=$backup;installed_at=(Get-Date -Format o);status='prepared'}
 $state | ConvertTo-Json | Set-Content -LiteralPath $statePath -Encoding utf8
 $touched=@()
 try {
  foreach($item in $items) {
   $touched+=$item
   New-Item -ItemType Directory -Path ([IO.Path]::GetDirectoryName($item.target)) -Force | Out-Null
   Copy-Item -LiteralPath $item.payload -Destination $item.target -Force
   if((Get-Sha $item.target) -ne $item.entry.patched_sha256) {throw 'Installed file verification failed'}
  }
  $state.status='installed';$state | ConvertTo-Json | Set-Content -LiteralPath $statePath -Encoding utf8
 } catch {
  foreach($item in $touched) {
   if($item.newFile){if(Test-Path -LiteralPath $item.target){Remove-Item -LiteralPath $item.target -Force}}
   else{Copy-Item -LiteralPath (Get-ContainedPath $backup $item.entry.path) -Destination $item.target -Force}
  }
  $state.status='rolled_back';$state | ConvertTo-Json | Set-Content -LiteralPath $statePath -Encoding utf8
  throw
 }
 Write-Output ('Installed 1918-entry English-slot Korean patch. Backup: '+$backup)
} else {
 $state=Get-Content -LiteralPath $statePath -Raw | ConvertFrom-Json
 if($state.game_root -ne $GameRoot) {throw 'Backup belongs to another installation'}
 foreach($item in $items) {
  if($item.newFile) {
   if($null -ne $item.current -and $item.current -ne $item.entry.patched_sha256) {throw ('Game changed since installation; no files restored: '+$item.entry.path)}
  } else {
   if($item.current -ne $item.entry.patched_sha256 -and $item.current -ne $item.entry.original_sha256) {throw ('Game changed since installation; no files restored: '+$item.entry.path)}
   if((Get-Sha (Get-ContainedPath $state.backup $item.entry.path)) -ne $item.entry.original_sha256) {throw 'Backup integrity check failed'}
  }
 }
 foreach($item in $items) {
  if($item.newFile) {
   if(Test-Path -LiteralPath $item.target){Remove-Item -LiteralPath $item.target -Force}
   if(Test-Path -LiteralPath $item.target){throw 'New patch file removal failed'}
  } else {
   Copy-Item -LiteralPath (Get-ContainedPath $state.backup $item.entry.path) -Destination $item.target -Force
   if((Get-Sha $item.target) -ne $item.entry.original_sha256) {throw 'Restored file verification failed'}
  }
 }
 $state.status='restored';$state | ConvertTo-Json | Set-Content -LiteralPath $statePath -Encoding utf8
 Write-Output 'Original game files restored. Saves were not changed by this script.'
}









