#!bin/bash

# MODEL_NAME="runwayml/stable-diffusion-v1-5"
MODEL_NAME="stabilityai/stable-diffusion-2-1"
OUTPUT_DIR="models/lora/stable-diffusion-2-1-chronext"
# HUB_MODEL_ID="pokemon-lora"
DATASET_NAME="datasets/watches_dataset/"

accelerate launch --mixed_precision="fp16" diffusion/train_txt_to_img_lora.py \
  --pretrained_model_name_or_path=$MODEL_NAME \
  --dataset_name=$DATASET_NAME \
  --dataloader_num_workers=8 \
  --resolution=512 --center_crop --random_flip \
  --train_batch_size=1 \
  --gradient_accumulation_steps=4 \
  --max_train_steps=15000 \
  --learning_rate=1e-04 \
  --max_grad_norm=1 \
  --lr_scheduler="cosine" --lr_warmup_steps=0 \
  --output_dir=${OUTPUT_DIR} \
  --checkpointing_steps=500 \
  --validation_prompt="Une montre pour homme de dimensions 42mm avec un bracelet noir et une fonction date." \
  --seed=1337
#   --push_to_hub \
#   --hub_model_id=${HUB_MODEL_ID} \
#   --report_to=tensorboard \