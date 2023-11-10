import torch
from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler

model_base = "stabilityai/stable-diffusion-2-1"
lora_model_path = "/path/to/lora/model/"

pipe = StableDiffusionPipeline.from_pretrained(model_base, torch_dtype=torch.float16, use_safetensors=True)
pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)

pipe.unet.load_attn_procs(lora_model_path)
pipe.to("cuda")

# use half the weights from the LoRA finetuned model and half the weights from the base model
image = pipe(
    "Une montre pour homme de dimensions 42mm avec un bracelet noir et une fonction date.", num_inference_steps=25, guidance_scale=7.5, cross_attention_kwargs={"scale": 0.5}
).images[0]
image.save("output/watch_1.png")

# use the weights from the fully finetuned LoRA model
image = pipe("Une montre pour homme de dimensions 42mm avec un bracelet noir et une fonction date.", num_inference_steps=25, guidance_scale=7.5).images[0]
image.save("output/watch_2.png")