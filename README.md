# VAEBMs

### Update (06-Dec-2021)
The official implementation (released recently) can be found here : [NVLabs/VAEBM](https://github.com/NVlabs/VAEBM)

## Introduction
Repository for CS698X course project (Topics in Probabilistic Modeling and Inference, Winter 2021, IIT Kanpur), on energy-based VAEs. Contains (unofficial) implementation of VAEBM [1] for Vanilla VAE, beta-TCVAE and Factor-VAE for MNIST, CelebA-64 and Chairs dataset. 

## Running the models
The Energy based model can be trained for a given VAE and dataset.
To train the model on default parameters, run the following command in the CS698X directory:

```bash
python3 train_vaebm.py
```
Args:
```python
  --vae_type, type=str, default='VAE'
  --num_workers,type=int, default=2
  --dataset,type=str, default='mnist'
  --batch_size,type=int, default=32
  --l2_reg_weight, type=float, default=1.0
  --spectral_norm_weight, type=float, default=0.2
  --sample_type,type=str, default='lang',
  --sample_step_size, type=float, default=8e-5
  --sample_steps, type=int, default=10
  --train_step_size, type=float, default=4e-5
  --train_steps, type=int, default=15
```
To generate samples and traversals, run the following command :
```bash
python3 test_vaebm.py
```

Args:
```python
  --vae_type,type=str, default='VAE'
  --dataset,type=str, default='mnist'
  --batch_size,type=int, default=1
  --step_size, type=float, default=8e-3
  --steps, type=int, default=16
  ```
Samples are stored according to the VAE used, dataset used and the step size involved. Pre-Trained models can be found here: [Google Drive](https://drive.google.com/drive/folders/1RW8uu5ZDbvm8dOZ0nWSHhhz76AY5F0Tf?usp=sharing). Please change the ROOT_DIR in `test_vaebm.py` to wherever the models are stored before running.

## References
[1] Zhisheng Xiao et al. “VAEBM: A Symbiosis between Variational Autoencoders and Energy-based Models”. In: International Conference on Learning Representations. 2021.  
[2] Code for IGEBM from [igebm-pytorch](https://github.com/rosinality/igebm-pytorch)  
[3] Spectral Norm code from [NVAE Repository](https://github.com/NVlabs/NVAE)  
[4] FID Calculations using [pytorch-fid](https://github.com/mseitzer/pytorch-fid) library  
[5] Pretrained VAE from [disentangling-vae](https://github.com/YannDubs/disentangling-vae)
