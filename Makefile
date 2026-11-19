# fylgja-examples (CONTRIBUTING.md).

.PHONY: all demo-dependencies venv test lint linkcheck wheelcheck \
	infrahub-up infrahub-down infrahub-register infrahub-seed contract orchestrator-env prefect-up prefect-down \
	orchestrator-serve netbox-up netbox-down netbox-seed netbox-hook netbox-change contract-netbox infrahub-demo \
	netbox-demo demo-down

VENV := .venv

# local/ is the main checkout's, also when make runs in a worktree: the parent of git's common directory.
MAIN := $(shell dirname "$$(git rev-parse --path-format=absolute --git-common-dir)")
LOCAL ?= $(MAIN)/local

# The development Infrahub (CONTRIBUTING.md): its version, the SDK's for infrahubctl, the ref registered, the
# seeded branch, PURGE=1 (no other value) for an infrahub-down that removes the volumes, and PROPOSED_CHANGE=1 (no
# other value) for an infrahub-seed that makes the seeded branch's proposed change.
INFRAHUB_VERSION ?= 1.11.11
INFRAHUB_SDK_VERSION ?= 1.23.2
REF ?= $(shell git branch --show-current)
SEED_BRANCH ?= third-link
PURGE ?=
PROPOSED_CHANGE ?=

# The development NetBox (CONTRIBUTING.md): NetBox's version, netbox-docker's release and the branching plugin's;
# PURGE=1 above, and no other value, for a netbox-down that removes the volumes.
NETBOX_VERSION ?= 4.7.5
NETBOX_DOCKER_VERSION ?= 5.1.1
NETBOX_BRANCHING_VERSION ?= 1.2.3
# The branch netbox-change builds, and NETBOX_TAG=1 (no other value) for a netbox-change that sets the tag last, which
# asks for the rehearsal.
NETBOX_BRANCH ?= third-link
NETBOX_TAG ?=

# The example orchestrator's change source, infrahub or netbox (D-097): the runner orchestrator-serve starts is
# given that source's environment, and orchestrator-env SOURCE=netbox runs nothing of Infrahub's.
SOURCE ?= infrahub
SOURCES := infrahub netbox
# Not empty where SOURCE is not one word of SOURCES: orchestrator-env then refuses before anything, as
# orchestrator-serve's edge_dev.py does.
SOURCE_REFUSED = $(filter-out 1,$(words $(SOURCE)))$(filter-out $(SOURCES),$(SOURCE))

all: lint test

# What the demonstrations need of the host (docs/demonstrations.md, "What the host must have"), installed where it is
# missing and checked where only its owner can give it (scripts/demo_dependencies.sh): git, ss and curl; uv at the
# version pyproject.toml's required-version pins; python3 at the members' requires-python, checked and never
# installed (D-115); Docker with its Compose plugin, and containerlab at the version the demonstrations were verified
# on, by containerlab's setup script; the groups docker and clab_admins; the AppArmor widening on Ubuntu; and the node
# login in local/.env and the memory, checked. DRY_RUN=1 prints each command that would change the host instead.
UV_VERSION := $(shell sed -n 's/^required-version = "==\(.*\)"$$/\1/p' pyproject.toml)
PYTHON_MIN := 3.14
CONTAINERLAB_VERSION := 0.81.0

demo-dependencies:
	@test -n "$(UV_VERSION)" || { echo "demo-dependencies: no required-version in pyproject.toml" >&2; exit 1; }
	@UV_VERSION=$(UV_VERSION) PYTHON_MIN=$(PYTHON_MIN) CONTAINERLAB_VERSION=$(CONTAINERLAB_VERSION) LOCAL='$(LOCAL)' \
		bash scripts/demo_dependencies.sh

# The environment, .venv, a locked sync of the uv workspace: the example orchestrator editable with every extra, and
# fylgja-core, fylgja-infrahub and fylgja-netbox at the versions uv.lock holds, from PyPI, which a pin moved in a
# pyproject.toml without `uv lock` refuses. The interpreter is the PATH's python3, never one uv fetches. CORE, the path of
# a fylgja-core checkout (never set by CI), installs that checkout's three distributions editable over the locked ones,
# and uv says nothing of the pins it replaces: only `uv pip check` reports it. `make venv` alone puts the lock back.
CORE ?=

venv:
	UV_PROJECT_ENVIRONMENT=$(abspath $(VENV)) uv sync --locked --all-packages --all-extras --python python3
	printf '*\n' > $(VENV)/.gitignore
	$(if $(CORE),uv pip install --python $(VENV)/bin/python -e $(CORE)/core -e $(CORE)/readers/infrahub -e $(CORE)/readers/netbox)
	$(if $(CORE),@echo "venv: the environment holds the checkout $(CORE) and is no longer the lock's; make venv alone restores it")

# The pure tier: no infrastructure.
test:
	cd infrahub && ../$(VENV)/bin/pytest -q
	cd netbox && ../$(VENV)/bin/pytest -q
	cd orchestrator && ../$(VENV)/bin/pytest -q

# mypy runs three times: the orchestrator's, infrahub/'s and netbox/'s tests would name modules alike in one run.
lint:
	$(VENV)/bin/ruff check --config orchestrator/pyproject.toml --config 'lint.isort.known-first-party=["fylgja_core"]' scripts infrahub netbox
	cd orchestrator && ../$(VENV)/bin/ruff check --config pyproject.toml . && ../$(VENV)/bin/mypy
	$(VENV)/bin/mypy infrahub/seed infrahub/tests scripts/infrahub_dev.py
	$(VENV)/bin/mypy netbox/seed netbox/tests scripts/netbox_dev.py

# Every relative link and anchor in the tracked Markdown resolves in a clone.
linkcheck:
	python3 -I scripts/linkcheck.py

# The example's wheel, built from orchestrator/ and formats/ with its two formats and its Infrahub change source's
# queries, installed in an empty environment beside fylgja-core, fylgja-infrahub and fylgja-netbox at VERSION from
# PyPI, never built here, where both its change sources import, each with nothing of the other, and its command
# answers --help and --version. Needs the network, and no Docker.
wheelcheck:
	python3 -I scripts/wheelcheck.py

# The development Infrahub, the Compose project fylgja-examples-infrahub: local/.env's missing names written, never
# printed; the published Compose file fetched once; started, and waited for until /api/info answers the version.
infrahub-up:
	python3 -I scripts/infrahub_dev.py up --local $(LOCAL) --version $(INFRAHUB_VERSION) --override infrahub/dev/compose.override.yml --repo $(MAIN)/.git

# Stopped, its containers, network and volumes kept; PURGE=1, and no other value, removes them and
# local/infrahub/seed.json.
infrahub-down:
	python3 -I scripts/infrahub_dev.py down --local $(LOCAL) --version $(INFRAHUB_VERSION) --override infrahub/dev/compose.override.yml --repo $(MAIN)/.git $(if $(filter 1,$(PURGE)),--purge)

# The development NetBox, the Compose project fylgja-examples-netbox: local/.env's missing names written, never printed;
# netbox-docker's release fetched once; a project network of another subnet than the override's recreated, its
# containers removed and its volumes kept; the plugin's image built, started, and waited for until Docker calls netbox
# healthy, its worker started, and /api/status/ names both versions and a running worker, read with the superuser's
# token, provisioned into local/.env where it lacks one or NetBox refuses it.
netbox-up:
	python3 -I scripts/netbox_dev.py up --local $(LOCAL) --netbox $(NETBOX_VERSION) --docker $(NETBOX_DOCKER_VERSION) --branching $(NETBOX_BRANCHING_VERSION) --override netbox/dev/compose.override.yml

# Stopped, its containers, network and volumes kept; PURGE=1, and no other value, removes them. local/.env, the
# release and the image stay.
netbox-down:
	python3 -I scripts/netbox_dev.py down --local $(LOCAL) --netbox $(NETBOX_VERSION) --docker $(NETBOX_DOCKER_VERSION) --branching $(NETBOX_BRANCHING_VERSION) --override netbox/dev/compose.override.yml $(if $(filter 1,$(PURGE)),--purge)

# The fixture network on the development NetBox's main from netbox/seed/main.yaml, found by its names or made, with
# the configuration template that renders it and the probes' inactive configuration context; main read back and
# refused, naming each difference and deleting nothing, where it is not the fixture (CONTRIBUTING.md). Then the
# reader's and the example's accounts at their least permissions, and their tokens' lines in local/.env, each kept
# where NetBox holds its token as that account's and made again where it does not. Load local/.env first, and again
# after for the two lines.
netbox-seed:
	$(VENV)/bin/python netbox/seed/seed.py --files netbox/seed
	$(VENV)/bin/python netbox/seed/account.py --env $(LOCAL)/.env

# The trigger on the development NetBox: the tag fylgja-rehearse, a webhook to the edge's Prefect that starts
# twin-rehearse/main, and the event rule that sends it when a branch carrying the tag is updated, each found by its
# name or made, and left (D-097). The webhook names the deployment's id, read from Prefect at the API edge_dev.py api
# prints, so it is run once make orchestrator-serve SOURCE=netbox serves, and again after every new Prefect home.
# Load local/.env first.
netbox-hook:
	prefect=$$(python3 -I scripts/edge_dev.py api --local $(LOCAL) --main $(MAIN)) && $(VENV)/bin/python netbox/seed/hook.py --prefect "$$prefect"

# The seeded change: the branch NETBOX_BRANCH, deleted where it stands with its marks and made anew from main, its two
# steps written and each marked by the example's own stage mark under the source netbox, which needs the core running;
# with NETBOX_TAG=1, last, the tag set, which asks for the rehearsal. Load local/.env first.
netbox-change:
	$(VENV)/bin/python netbox/seed/change.py --branch $(NETBOX_BRANCH) $(if $(filter 1,$(NETBOX_TAG)),--tag )-- python3 -I scripts/edge_dev.py run --source netbox --local $(LOCAL) --main $(MAIN) -- stage mark

# infrahubctl, in a venv of its own under local/infrahub/, so that the SDK meets nothing else (D-083): made by uv, at
# the SDK's pin, and no part of the workspace.
$(LOCAL)/infrahub/.venv/bin/infrahubctl:
	uv venv --no-project --clear --python python3 $(LOCAL)/infrahub/.venv
	printf '*\n' > $(LOCAL)/infrahub/.venv/.gitignore
	uv pip install -q --python $(LOCAL)/infrahub/.venv/bin/python 'infrahub-sdk[ctl]==$(INFRAHUB_SDK_VERSION)'

# The schema library, the group fylgja-devices and this repository's registration on main, at REF, the branch checked
# out, and its commit (CONTRIBUTING.md); a detached head names no branch and is refused. Load local/.env first.
infrahub-register: $(LOCAL)/infrahub/.venv/bin/infrahubctl
	$(if $(REF),,$(error REF is empty: a detached head names no branch to register; give REF=<branch>))
	$(VENV)/bin/python infrahub/seed/register.py --ref $(REF) --commit $$(git rev-parse --verify '$(REF)^{commit}') --schema infrahub/schema/dcim --ctl $(LOCAL)/infrahub/.venv/bin/infrahubctl

# The FylgjaProbe kind and the example's FylgjaStage on main where main lacks them; the fixture network on
# main from infrahub/seed/main/'s object files, loaded by infrahubctl, and its configurations generated and waited
# for; then an earlier seed's marks and open proposed change of SEED_BRANCH removed, and the branch made anew with
# infrahub/seed/stages/'s two edits, each generated, waited for, timed by the reader's head and marked on main; with
# PROPOSED_CHANGE=1, last, its proposed change into main. Into local/infrahub/seed.json (CONTRIBUTING.md). Load
# local/.env first.
infrahub-seed: $(LOCAL)/infrahub/.venv/bin/infrahubctl
	$(VENV)/bin/python infrahub/seed/seed.py --branch $(SEED_BRANCH) --files infrahub/seed --out $(LOCAL)/infrahub/seed.json --ctl $(LOCAL)/infrahub/.venv/bin/infrahubctl --schema infrahub/schema/fylgja-probe.yml --schema infrahub/schema/fylgja-stage.yml $(if $(filter 1,$(PROPOSED_CHANGE)),--proposed-change)

# The example orchestrator's lines in local/.env, generated and never printed: the basic auth the edge's Prefect, the
# task workers and NetBox's webhook share, the runner's token of the core's, listed in the token file FYLGJA_TOKENS
# names, the scope, the reader document and the records' directory, and NetBox's reader document and scope; then, but
# with SOURCE=netbox, its Infrahub account and that account's token, checked where the line is there (CONTRIBUTING.md,
# "Running the example orchestrator"). With SOURCE=netbox it needs no Infrahub: the example's NetBox token is make
# netbox-seed's.
# Load local/.env first.
orchestrator-env: $(if $(SOURCE_REFUSED)$(filter netbox,$(SOURCE)),,$(LOCAL)/infrahub/.venv/bin/infrahubctl)
	$(if $(SOURCE_REFUSED),$(error SOURCE is infrahub or netbox))python3 -I scripts/edge_dev.py env --local $(LOCAL) --main $(MAIN)
	$(if $(filter netbox,$(SOURCE)),,$(VENV)/bin/python infrahub/seed/account.py --env $(LOCAL)/.env --ctl $(LOCAL)/infrahub/.venv/bin/infrahubctl)

# The edge's Prefect server on port 4200 of the Docker bridge's gateway (PREFECT_BIND over it), under local/prefect/,
# waited for until it answers; refused, with nothing started or stopped, where anything else listens on the port.
# Load local/.env first.
prefect-up:
	python3 -I scripts/edge_dev.py prefect-up --local $(LOCAL) --main $(MAIN)

# The server prefect-up started ended, and no other process.
prefect-down:
	python3 -I scripts/edge_dev.py prefect-down --local $(LOCAL) --main $(MAIN)

# The runner, fylgja-orchestrator serve, in the foreground until it is stopped, given its own tokens of the change
# source SOURCE and no other. Load local/.env first.
orchestrator-serve:
	python3 -I scripts/edge_dev.py serve --source $(SOURCE) --local $(LOCAL) --main $(MAIN)

# The contract tier: infrahub/'s code, then the example orchestrator's, against the running
# development Infrahub, the last with a Prefect server of its own on loopback (CONTRIBUTING.md). Load local/.env first.
contract:
	cd infrahub && FYLGJA_INFRAHUB_SEED=$(LOCAL)/infrahub/seed.json FYLGJA_INFRAHUB_CTL=$(LOCAL)/infrahub/.venv/bin/infrahubctl ../.venv/bin/pytest -q -rA -m contract tests/contract
	cd orchestrator && FYLGJA_INFRAHUB_SEED=$(LOCAL)/infrahub/seed.json FYLGJA_INFRAHUB_CTL=$(LOCAL)/infrahub/.venv/bin/infrahubctl ../.venv/bin/pytest -q -rA -m contract tests/contract

# The NetBox contract tier: netbox/'s code, then the example orchestrator's NetBox change
# source, against the running development NetBox, the last with a Prefect server of its own on the Docker bridge's
# gateway (CONTRIBUTING.md). Load local/.env first.
contract-netbox:
	cd netbox && ../.venv/bin/pytest -q -rA -m contract_netbox tests/contract
	cd orchestrator && ../.venv/bin/pytest -q -rA -m contract_netbox tests/contract_netbox

# A demonstration of one source of truth, infrahub or netbox, with no step by hand (CONTRIBUTING.md, "The
# demonstrations"; D-104): the host's preconditions checked, then the source's runbook taken in order through the
# targets above, the core and the runner started in the background by recorded pids, to the change opened, then the
# rehearsal it starts waited for on the edge's Prefect and its verdict read: exit 0 for passed alone. It reads
# local/.env itself, before every step, and at REF it registers this repository with Infrahub. No other variable
# given here, or held by the shell or local/.env, reaches a target: each is run at this file's own value, the script
# saying which were not passed on.
infrahub-demo netbox-demo: | $(VENV)/bin/fylgja-core-server
	python3 -I scripts/demo.py up $(@:-demo=) --local $(LOCAL) --main $(MAIN) --ref='$(REF)'

# The venv, made for a demonstration where the core's server command is missing, and never remade by one.
$(VENV)/bin/fylgja-core-server:
	$(MAKE) venv

# What a demonstration started, ended: its runner, every twin its core holds, its core, the Prefect server it
# started and its source, whose volumes are kept; PURGE=1 on a make command line removes them too, one a make above
# hands down in MAKEFLAGS counting as a command line's, and no other value and no PURGE of the environment's,
# exported by the shell or by a local/.env it loaded, does.
demo-down:
	python3 -I scripts/demo.py down --local $(LOCAL) --main $(MAIN) $(if $(and $(filter 1,$(PURGE)),$(filter command line,$(origin PURGE))),--purge)
