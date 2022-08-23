# %%
import matplotlib.pyplot as plt
import numpy as np
import openmc
import pandas as pd

import importlib
import os
import re

import model
import processing
import utils
import settings
import modify_materials
import finite_difference

# Key examples for run  type:
# Overall pattern: sourceInfo_discretisation_discretisationNumber_MTnumberPerturbed
# npd neutron prompt delayed
# gp gamma prompt only
# npdgpd neutron prompt delayed gamma prompt delayed
# We are assuming all perturbations will be of all iron isotopes


def execute_perturbation(mt, perturbation, discretization=None):
    if discretization is None:
        command = f"python3 perturb_xs.py -mt {mt} -p {perturbation}"
    else:
        command = f"python3 perturb_xs.py -mt {mt} -p {perturbation} -di {discretization}"
    os.system(command)


def run_single(N, run_env, check_repeat):
    settings.N = N
    settings.RUN_ENV = run_env

    if check_repeat:
        output_path = os.path.join(settings.RUN_ENV, f'output/e{N}')
        if os.path.exists(output_path):
            return

    model.load_model()
    openmc.run(cwd=run_env)
    model.post_process()
    processing.main(["output_summary"])


def run(powers, mt, perturbations, discretization, standard_run=False, check_repeat=True):
    if os.getcwd() != '/ironbenchmark':
        os.chdir('/ironbenchmark')
    perturb_folder = '/ironbenchmark/perturbed_run_data/'
    standard_run_folder = '/ironbenchmark/standard_run'

    for perturbation in perturbations:
        if standard_run:
            for i in powers:
                run_single(i, standard_run_folder, check_repeat)
        elif discretization is None:
            execute_perturbation(mt, perturbation)
            modify_materials.main(perturbation=perturbation)
            id_code = f'mt{mt}-p{perturbation}'
            run_env = os.path.join(perturb_folder, id_code)
            for i in powers:
                run_single(i, run_env, check_repeat)
        else:
            execute_perturbation(mt, perturbation, discretization)
            modify_materials.main(
                perturbation=perturbation, discretization=discretization)
            for group in range(discretization):
                id_code = f'mt{mt}-p{perturbation}d{discretization:03}'
                group_code = f'g{group+1:03}'
                run_env = os.path.join(perturb_folder, id_code, group_code)
                for i in powers:
                    run_single(i, run_env, check_repeat)


if __name__ == "__main__":
    powers = [8]
    mt = 102
    perturbations = [0.01, 0.03, 0.1, 0.3, 1.0, 3.0]
    discretization = None
    run(powers, mt, perturbations, discretization)
    finite_difference.compare_perturbation('Fe56', mt, perturbations, discretization=None,
                                           group=None, structure='partisn')


# %%
