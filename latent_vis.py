import os
import argparse
from test_vaebm import VAE_DIR

import torch
import torchvision
import numpy as np 
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt

from torch.nn.functional import mse_loss

from vae.disvae.utils.modelIO import load_model
from igebm.model import IGEBM

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

RESULT_DIR = '/content/gdrive/MyDrive/cs698x_latent_vis'
ROOT_DIR = '/content/gdrive/MyDrive/results/'
VAE_DIR = './vae/results/'

def langevin_sample_recur(vae, ebm, **kwargs):
    """
    Sample output image using Langevin dynamics based MCMC, 
    from VAEBM.

    Parameters--> 
        vae (torch.nn.module) : VAE model used in VAEBM
        ebm (torch.nn.module) : EBM model used in VAEBM
        batch_size (int): batch size of images, default: BATCH_SIZE
        sampling_steps (int): number of sampling steps in MCMC, default: LD_N_STEPS
        step_size (int): step size in sampling 

    Returns-->
        image_out (torch.Tensor): image sample
    """
    epsilon = torch.randn(1, vae.latent_dim, requires_grad=True, device=device)
    image_out = vae.decoder(epsilon)
    image_out.detach_()

    vae_sample = image_out

    vae.eval()
    ebm.eval()
    log_h_prob = lambda epsilon: ebm(vae.decoder(epsilon)) + \
                                 0.5 * mse_loss(vae.decoder(epsilon),image_out)
    # log_h_prob = lambda eps: ebm(vae.decoder(eps)) + 0.5 * (torch.linalg.norm(eps,dim=1) ** 2)
    
    step_size = kwargs['step_size']

    for step in range(kwargs['sampling_steps']):
        noise = torch.randn_like(epsilon,device=device)
        loss = log_h_prob(epsilon)
        loss.sum().backward()

        epsilon.data.add_(noise, alpha=torch.sqrt(torch.tensor(step_size)))
        epsilon.grad.data.clamp_(-0.01,0.01)

        epsilon.data.add(epsilon.grad.data, alpha=-step_size / 2)
        epsilon.grad.detach_()
        epsilon.grad.zero_()
        
        if step == kwargs['sampling_steps'] - 1:
            vaebm_sample = vae.decoder(epsilon)
            vaebm_sample = vaebm_sample.detach()
                    
        loss = loss.detach()
        noise = noise.detach()
        
    return vae_sample, vaebm_sample

def main():
    VAE_latents = []
    EBM_latents = []

    parser = argparse.ArgumentParser()

    parser.add_argument('--vae_type',type=str, default='VAE')
    parser.add_argument('--dataset',type=str, default='mnist')
    parser.add_argument('--batch_size',type=int, default=4)
    parser.add_argument('--step_size', type=float, default=8e-3)
    parser.add_argument('--steps', type=int, default=16)
    
    args = parser.parse_args()

    vae_type = args.vae_type
    dataset = args.dataset
    batch_size = args.batch_size
    step_size = args.step_size
    steps = args.steps 

    ebm_model_file = ROOT_DIR + vae_type + '_' + dataset + '.ckpt'
    
    vae_model_name = vae_type + '_' +dataset      #Choose from VAE, beta-VAE, beta-TCVAE, factor-VAE 
    vae_model_dir = os.path.join(VAE_DIR,vae_model_name)
    vae = load_model(vae_model_dir).to(device)
    vae.eval()

    ebm = IGEBM(dataset=dataset)
    ebm.load_state_dict(torch.load(os.path.join('./results',ebm_model_file)))
    ebm = ebm.to(device)
    ebm.eval()

    for _ in range(batch_size):
        vae_sample, vaebm_sample = langevin_sample_recur(
            vae,
            ebm, 
            batch_size=batch_size, 
            sampling_steps=steps, 
            step_size=step_size
        )
        VAE_latents.append(vae(vae_sample)[1][0].detach().to('cpu')[:,:10].numpy())
        EBM_latents.append(vae(vaebm_sample)[1][0].detach().to('cpu')[:,:10].numpy())
    
    VAE_latents = np.array(VAE_latents).reshape(-1,10)
    EBM_latents = np.array(EBM_latents).reshape(-1,10)

    VAE_latents_embedded = TSNE().fit_transform(VAE_latents)
    EBM_latents_embedded = TSNE().fit_transform(EBM_latents)

    plt.scatter(*zip(*VAE_latents_embedded))
    plt.scatter(*zip(*EBM_latents_embedded))
    # plt.show()
    plt.savefig('/content/latents.png')

if __name__=='__main__':
    main()