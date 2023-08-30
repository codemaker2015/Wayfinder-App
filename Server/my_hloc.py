# import tqdm, tqdm.notebook
# tqdm.tqdm = tqdm.notebook.tqdm  # notebook-friendly progress bars
from pathlib import Path

from hloc import extract_features, match_features, reconstruction, visualization, pairs_from_exhaustive, result_extractor
from hloc.visualization import plot_images, read_image
# from hloc.utils import viz_3d
import numpy as np
import pycolmap
from hloc.localize_sfm import QueryLocalizer, pose_from_cluster
import random

images = Path('koe-datasets/new')
outputs = Path('outputs/demo/')
sfm_pairs = outputs / 'pairs-sfm.txt'
loc_pairs = outputs / 'pairs-loc.txt'
sfm_dir = outputs / 'sfm'
features = outputs / 'features.h5'
matches = outputs / 'matches.h5'

def main():
    # feature_conf = extract_features.confs['superpoint_aachen'] # for outdoor
    global feature_conf, matcher_conf
    feature_conf = extract_features.confs['superpoint_inloc'] # for indoor
    matcher_conf = match_features.confs['superglue-fast']

    def get_images(folder_path, num_images):
        images = list(folder_path.glob('*.jpg'))
        selected_images = random.sample(images, min(num_images, len(images)))
        return selected_images

    # Choose between color and grayscale
    # note that under the hood, the suprrpoint algorithm already preprocess to grayscale
    # images. See Hierarchical-Localization/hloc/extract_features.py
    color_mode = "color"

    # Choose the number of images from each folder
    num_images = 14

    # landmarks to be exlucluded from the "training"
    exclude_dirs = ["conference-b"]

    references = []
    if color_mode == 'color':
        folder = images / 'rgb/'
    else:
        folder = images / 'gray/'

    # Get the selected images from each folder
    for sub_folder in folder.iterdir():
        if sub_folder.is_dir() and sub_folder.name not in exclude_dirs:
            selected_images = get_images(sub_folder, num_images)
            references.extend([str(p.relative_to(images)) for p in selected_images])

    print(references)
    print(len(references), "mapping images")

    extract_features.main(feature_conf, images, image_list=references, feature_path=features)
    pairs_from_exhaustive.main(sfm_pairs, image_list=references)
    match_features.main(matcher_conf, sfm_pairs, features=features, matches=matches);

    model = reconstruction.main(sfm_dir, images, sfm_pairs, features, matches, image_list=references)
    # check_location('night/e1-l2-conference-room-b_3.jpg')

def check_location(query = str): 
    model = pycolmap.Reconstruction(sfm_dir)
    feature_conf = extract_features.confs['superpoint_inloc'] # for indoor
    matcher_conf = match_features.confs['superglue-fast']
    references_registered = [model.images[i].name for i in model.reg_image_ids()]
    extract_features.main(feature_conf, images, image_list=[query], feature_path=features, overwrite=True)
    pairs_from_exhaustive.main(loc_pairs, image_list=[query], ref_list=references_registered)
    match_features.main(matcher_conf, loc_pairs, features=features, matches=matches, overwrite=True);

    camera = pycolmap.infer_camera_from_image(images / query)
    ref_ids = [model.find_image_with_name(n).image_id for n in references_registered]
    conf = {
        'estimation': {'ransac': {'max_error': 12}},
        'refinement': {'refine_focal_length': True, 'refine_extra_params': True},
    }
    localizer = QueryLocalizer(model, conf)
    ret, log = pose_from_cluster(localizer, query, camera, ref_ids, features, matches)

    print(f'found {ret["num_inliers"]}/{len(ret["inliers"])} inlier correspondences.')
    percent_match = (ret["num_inliers"]/len(ret["inliers"])) * 100
    print(f'Match percentage {percent_match}')
    possible_locations =  result_extractor.extract_loc_from_log(images, query, log, model)

    print('possible_locations')
    print(possible_locations)

    # mapping to the actual location
    # must match the value in OriginTargets in MainARNavigation Scene
    if "conference-a" in possible_locations[0]:
        return "Conference Room A"
    elif "conference-b" in possible_locations[0]:
        return "Conference Room B"
    elif "enginius-office" in possible_locations[0]:
        return "Enginius Office"
    elif "main-entrance" in possible_locations[0]:
        return "Main Entrance"
    elif "oddai" in possible_locations[0]:
        return "ODDAI"
    elif "oscent" in possible_locations[0]:
        return "OSCENT"
    else :
        return None

if __name__ == "__main__":
   main()