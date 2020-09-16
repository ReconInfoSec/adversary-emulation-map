import glob
import json
import logging
import shutil

from git import Repo
from munch import Munch, munchify
import yaml


def get_latest(refresh_repo):
  if glob.glob("./.plans"):
    if not refresh_repo:
      return
    shutil.rmtree("./.plans")
  Repo.clone_from("https://github.com/center-for-threat-informed-defense/adversary_emulation_library.git", "./.plans")

def get_plan_path(search_string):
  plans = glob.glob("./.plans/{search_string}/Emulation_Plan/*.yaml".format(search_string=search_string))
  if plans:
    return plans[0]

def get_plan(plan_path):
  try:
    with open(plan_path, "r") as f:
      plan = yaml.safe_load(f)
      plan = munchify(plan)
      return plan
  except:
    return None

def get_tactics(plan):
  for procedure in plan:
    if "id" in procedure:
      print(procedure.tactic)

def get_techniques(plan):
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
        
    except (Exception) as e:
        completed = False

    finally:
        return completed
