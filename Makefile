clean:
	@find . -type f -name "*.py[c|o]" -exec rm -f {} \;
	@find . -type d -name "*gendo.egg-info" -exec rm -rf {} \;
	@find . -type d -name "*gendobot.egg-info" -exec rm -rf {} \;
	@find . -type d -name "*dist" -exec rm -rf {} \;
	@find . -type d -name "*build" -exec rm -rf {} \;
