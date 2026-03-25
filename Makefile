CONFIGURE_FLAGS = --prefix=/usr --with-aopkg=true --config-dir=/etc/aopm.d --var-dir=/var/aopm
ENV = bash
PYTHON = python3
CONFIG_FILE = install.config
configure:
	@$(ENV) configure.sh $(CONFIGURE_FLAGS)

compile:
	@$(PYTHON) compiler.py $(CONFIG_FILE)

clean:
	@rm -r compile
	@rm -r build
	@rm -f aopm.spec
	@rm -f aopkg.spec
	@rm -f install.config
	@rm -f .config

install:
	@$(PYTHON) install.py $(CONFIG_FILE)