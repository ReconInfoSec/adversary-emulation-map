import argparse

import utils


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("plan_name", help="Name of the plan to map. E.g. fin6")
  parser.add_argument("--output", help="Output layer file name", required=False, default="output.json")
  parser.add_argument("--refresh-repo", help="Execute git clone to get the latest plans from Github", required=False, action="store_true")
  args = parser.parse_args()

  utils.get_latest(args.refresh_repo)
  plan_path = utils.get_plan_path(args.plan_name)
  plan = utils.get_plan(plan_path)
  techniques = utils.get_techniques(plan)
  utils.build_layer(techniques, args.plan_name, args.output)