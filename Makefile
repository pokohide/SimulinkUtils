SAMPLE_SRC     := setting.yaml.sample
SETTING_SRC    := setting.yaml
SETTING_EXISTS := $(shell find -name ${SETTING_SRC})

init:
	pip install -r requirements.txt
	$(if $(SETTING_EXISTS), cp $(SAMPLE_SRC) $(SETTING_SRC))

test:
