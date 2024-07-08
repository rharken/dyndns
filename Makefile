dyndns: dyndns.py Dockerfile
	docker build -t dyndns .

clean:
	docker system prune --all --force
