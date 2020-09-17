import glob
import json
import logging
import shutil

from git import Repo
from munch import Munch, munchify
import yaml


PLANS_DIR = "./.plans"

def get_latest(refresh_repo):
  """Get the latest Emulation Plans from the MITRE Github repo. (Optionally refreshes the local copy but will grab automatically if the repo does not exist at the `PLANS_DIR` location.

    Args:
        refresh_repo (bool): Flag indicating whether to refresh the local copy

    Returns:
        NA. Files created or updated as a side-effect
  """
  if glob.glob(PLANS_DIR):
    if not refresh_repo:
      return
    try:
      shutil.rmtree(PLANS_DIR)
    except FileNotFoundError:
      pass
  print("Requesting latest plans from Github ...")
  try:
    Repo.clone_from("https://github.com/center-for-threat-informed-defense/adversary_emulation_library.git", PLANS_DIR)
    print("Successfully retrieved lastest plans from Github")
  except:
    raise RuntimeError("Could not clone the remote repo and retrieve Emulation Plans from Github")

def get_plan_path(search_string):
  """Search for, and verify a plan exists for the name supplied

    Args:
        search_string (string): The name of an adversary, or plan, to map

    Returns:
        (string): The path of the plan yaml file
    """
  plans = glob.glob("{plans_dir}/{search_string}/Emulation_Plan/*.yaml".format(plans_dir=PLANS_DIR, search_string=search_string))
  if plans:
    return plans[0]
  else:
    return None

def get_plan(plan_path):
  """Reads the plan and "munches" it into an object

    Args:
        plan_path (string): The path to the plan yaml file

    Returns:
        (Munch): a munched (dict) "Plan" object
    """
  try:
    with open(plan_path, "r") as f:
      plan = yaml.safe_load(f)
      plan = munchify(plan)
      return plan
  except:
    return None

def get_techniques(plan):
  """Parses a plan and retrieves the techniques for mapping.

    Includes the procedure ID and procedure step for reference in layer tooltips

    Args:
        plan (dict (munch)): A "Plan" object

    Returns:
        (list): List of (munched) "Technique" objects
    """
  techniques = []
  for procedure in plan:
    if "id" in procedure:
      technique = Munch()
      technique.id = procedure.technique.attack_id
      technique.procedure_id = procedure.id
      technique.procedure_step = procedure.procedure_step
      techniques.append(technique)
  return techniques

def build_layer(plan_techniques, plan_name, layer_name):
    """Create a Navigator layer (.json) file on the local filesystem

    Add the required meta data and format per the MITRE layer spec
    https://github.com/mitre-attack/attack-navigator/blob/master/layers/LAYERFORMATv3.md

    Args:
        plan_techniques (dict): A dictionary of techniques which are in the plan. the "metadata" field contains additional information about the plan as related to the technique
        layer_name (str): Output file name

    Returns:
        (bool): True if successful, False if not
    """

    completed = False

    data = {}
    data["domain"] = "mitre-enterprise"
    data["name"] = "{plan_name} Adversary Emulation Heatmap".format(plan_name=plan_name)
    data["description"] = "Techniques part of the {plan_name} Adversary Emulation plan".format(plan_name=plan_name)
    data["version"] = "3.0"
    data["techniques"] = []

    for technique in plan_techniques:
        data["techniques"].append({
          "color": "#3f2b96",
          "techniqueID": technique.id, 
          "metadata": [{
            "name": "Procedure ID", 
            "value": technique.procedure_id
            }, 
            {
              "name": "Procedure Step", 
              "value": technique.procedure_step
            }]})
        if "." in technique.id:
          data["techniques"].append({
            "techniqueID": technique.id.split(".")[0], 
            "showSubtechniques": True
          })

    try:
        # Indent makes it print pretty
        with open(layer_name, "w") as f:
            json.dump(data, f, indent=2)
        completed = True
        print("Success. Layer created at {output}".format(output=layer_name))
        
    except (Exception) as e:
        completed = False

    finally:
        return completed
