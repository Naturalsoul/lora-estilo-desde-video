# LoRA de estilo LGPE con musubi-tuner. Cierra ComfyUI antes: necesita toda la VRAM (probado en una RTX 4070 SUPER de 12 GB).
#   .\entrenar.ps1 -Prueba     # cachea y entrena 10 pasos para medir memoria y velocidad
#   .\entrenar.ps1             # entrenamiento completo (4 epocas = 1936 pasos, guarda cada una)
param(
    [switch]$Prueba,
    [string]$Musubi = "C:\musubi-tuner",   # clon de github.com/kohya-ss/musubi-tuner con su .venv
    [string]$Modelos = "C:\ComfyUI\models" # carpeta con los pesos de Qwen-Image 2512
)
$ErrorActionPreference = "Stop"
$mt = $Musubi
$py = "$mt\.venv\Scripts\python.exe"
$here = $PSScriptRoot
$dit = "$Modelos\diffusion_models\qwen_image_2512_bf16.safetensors"
$vae = "$Modelos\vae\qwen_image_vae.safetensors"
$te = "$Modelos\text_encoders\qwen_2.5_vl_7b.safetensors"
$cfg = "$here\dataset.toml"

Set-Location $mt
# las caches solo se calculan la primera vez (se saltan si ya existen)
& $py src/musubi_tuner/qwen_image_cache_latents.py --dataset_config $cfg --vae $vae --model_version original --skip_existing
& $py src/musubi_tuner/qwen_image_cache_text_encoder_outputs.py --dataset_config $cfg --text_encoder $te --batch_size 1 --model_version original --fp8_vl --skip_existing
if ($LASTEXITCODE) { throw "fallo el cache" }  # PS 5.1 no corta solo cuando falla un .exe

$largo = if ($Prueba) { @("--max_train_steps", "10", "--output_name", "lgpe_prueba") } else { @("--max_train_epochs", "4", "--save_every_n_epochs", "1", "--output_name", "lgpestyle_qwen2512") }
& "$mt\.venv\Scripts\accelerate.exe" launch --num_cpu_threads_per_process 1 --mixed_precision bf16 src/musubi_tuner/qwen_image_train_network.py `
    --dit $dit --vae $vae --text_encoder $te --model_version original --dataset_config $cfg `
    --sdpa --mixed_precision bf16 --fp8_base --fp8_scaled --blocks_to_swap 45 --gradient_checkpointing `
    --timestep_sampling shift --weighting_scheme none --discrete_flow_shift 2.2 `
    --optimizer_type adamw8bit --learning_rate 5e-5 `
    --max_data_loader_n_workers 2 --persistent_data_loader_workers `
    --network_module networks.lora_qwen_image --network_dim 16 --seed 42 `
    --output_dir "$here\salida" @largo
