# Pasos con el modelo de visión Qwen2.5-VL 7B (fp8, local), usando el script de captions de musubi-tuner.
#   .\vlm.ps1 filtro     # candidatas/ -> vlm_filtro.jsonl (YES/NO por imagen, ~2 img/s)
#   .\vlm.ps1 captions   # dataset/    -> captions_vlm.jsonl (descripción larga, ~9 s/img)
param(
    [Parameter(Mandatory)][ValidateSet("filtro", "captions")][string]$Paso,
    [string]$Musubi = "C:\musubi-tuner",
    [string]$Modelo = "C:\ComfyUI\models\text_encoders\qwen_2.5_vl_7b.safetensors"
)
$ErrorActionPreference = "Stop"
$here = $PSScriptRoot
$py = "$Musubi\.venv\Scripts\python.exe"
$script = "$Musubi\src\musubi_tuner\caption_images_by_qwen_vl.py"

if ($Paso -eq "filtro") {
    # max_new_tokens 4: solo necesitamos YES o NO, así es ~20 veces más rápido que un caption
    $prompt = "Is this a clean exploration screenshot of the game world (a town, route, cave or building interior) " +
              "seen from the normal high overhead camera, where the player character is small and there is NO battle, " +
              "NO Pokemon catching scene, NO close-up of a character, NO menu and NO text or dialog box on screen? Answer only YES or NO."
    & $py $script --image_dir "$here\candidatas" --model_path $Modelo --fp8_vl --max_size 640 --max_new_tokens 4 `
        --output_file "$here\vlm_filtro.jsonl" --prompt $prompt
} else {
    & $py $script --image_dir "$here\dataset" --model_path $Modelo --fp8_vl --max_new_tokens 300 `
        --output_file "$here\captions_vlm.jsonl"
}
if ($LASTEXITCODE) { throw "falló Qwen2.5-VL ($Paso)" }
