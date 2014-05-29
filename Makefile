all:
	@echo "Available target: clean"
	
clean:
	find . -name "*.pyc" -exec rm -fv '{}' \;
	find . -name "*.pyo" -exec rm -fv '{}' \;
	find . -name "*.log" -exec rm -fv '{}' \;
	find . -name "*.bak" -exec rm -fv '{}' \;
	find . -name "*.spec" -exec rm -fv '{}' \;
	find . -name "*.swp" -exec rm -fv '{}' \;
	find . -name "*.swo" -exec rm -fv '{}' \;
	rm -rfv .externalToolBuilders/
	rm -rfv xbmc_qobuz.egg-info/ 

.PHONY: clean
