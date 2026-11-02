IMAGE     := mobile-code-reviewer
CONTAINER := mobile-code-reviewer
PORT      := 8043
# Parent directory of this repo: all sibling repositories are served from here
REPOS_DIR := $(abspath $(CURDIR)/..)
# Bind only to this host's Tailscale address, so the app is reachable from the tailnet only
BIND_IP    = $(shell tailscale ip -4 2>/dev/null | head -n1)

.PHONY: build start stop

build:
	docker build -t $(IMAGE) .

start:
	@test -n "$(BIND_IP)" || { echo "No Tailscale IPv4 address found. Is Tailscale running?"; exit 1; }
	docker run -d --rm --name $(CONTAINER) \
		-p $(BIND_IP):$(PORT):8043 \
		-v $(REPOS_DIR):/repos:ro \
		$(IMAGE)

stop:
	docker stop $(CONTAINER)
